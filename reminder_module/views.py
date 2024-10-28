from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect

from doctor_module.models import Doctors, Availability
from .models import MedicineReminder, ReserveDoctor
from .forms import MedicineReminderForm, ReserveDoctorForm
# from reminder_module.task import send_scheduled_emails
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.views.generic.edit import CreateView
from .models import MedicineReminder
from .forms import MedicineReminderForm
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from datetime import datetime, timedelta, date


@method_decorator(login_required, name='dispatch')
class CreateReminderView(View):
    def get(self, request):
        data = MedicineReminderForm()
        return render(request, 'reminder_module/medical_page.html', context={'form': data})

    def post(self, request):
        data = MedicineReminderForm(request.POST)
        if data.is_valid():
            MedicineReminder.objects.create(
                user=request.user,
                medicine_name=data.cleaned_data['medicine_name'],
                route_of_administration=data.cleaned_data['route_of_administration'],
                dosage_form=data.cleaned_data['dosage_form'],
                dosage_unit_of_measure=data.cleaned_data['dosage_unit_of_measure'],
                dosage_quantity_of_units_per_time=data.cleaned_data['dosage_quantity_of_units_per_time'],
                regimen_note=data.cleaned_data['regimen_note'],
                equally_distributed_regimen=True,
                periodic_interval=data.cleaned_data['periodic_interval'],
                dosage_frequency=data.cleaned_data['dosage_frequency'],
                first_time_of_intake=data.cleaned_data['first_time_of_intake'],
                is_chronic_or_acute=data.cleaned_data['is_chronic_or_acute'],
                stopped_by_datetime=data.cleaned_data['stopped_by_datetime'],
            )
        return render(request, 'reminder_module/medical_page.html', context={'form': data})


@method_decorator(login_required, name='dispatch')
class UpdateReminderView(View):
    def get(self, request, reminder_id):
        # گرفتن شیء MedicineReminder بر اساس شناسه
        reminder = MedicineReminder.objects.get(id=reminder_id, user=request.user)

        # پر کردن فرم به صورت دستی با داده‌های مدل
        initial_data = {
            'medicine_name': reminder.medicine_name,
            'route_of_administration': reminder.route_of_administration,
            'dosage_form': reminder.dosage_form,
            'dosage_unit_of_measure': reminder.dosage_unit_of_measure,
            'dosage_quantity_of_units_per_time': reminder.dosage_quantity_of_units_per_time,
            'regimen_note': reminder.regimen_note,
            'periodic_interval': reminder.periodic_interval,
            'dosage_frequency': reminder.dosage_frequency,
            'first_time_of_intake': reminder.first_time_of_intake,
            'is_chronic_or_acute': reminder.is_chronic_or_acute,
            'stopped_by_datetime': reminder.stopped_by_datetime,
        }

        form = MedicineReminderForm(initial=initial_data)
        return render(request, 'reminder_module/update_medical_page.html', context={'form': form})

    def post(self, request, reminder_id):
        # گرفتن شیء MedicineReminder بر اساس شناسه
        reminder = MedicineReminder.objects.get(id=reminder_id, user=request.user)

        form = MedicineReminderForm(request.POST)
        if form.is_valid():
            # به‌روزرسانی شیء مدل با داده‌های جدید از فرم
            reminder.medicine_name = form.cleaned_data['medicine_name']
            reminder.route_of_administration = form.cleaned_data['route_of_administration']
            reminder.dosage_form = form.cleaned_data['dosage_form']
            reminder.dosage_unit_of_measure = form.cleaned_data['dosage_unit_of_measure']
            reminder.dosage_quantity_of_units_per_time = form.cleaned_data['dosage_quantity_of_units_per_time']
            reminder.regimen_note = form.cleaned_data['regimen_note']
            reminder.periodic_interval = form.cleaned_data['periodic_interval']
            reminder.dosage_frequency = form.cleaned_data['dosage_frequency']
            reminder.first_time_of_intake = form.cleaned_data['first_time_of_intake']
            reminder.is_chronic_or_acute = form.cleaned_data['is_chronic_or_acute']
            reminder.stopped_by_datetime = form.cleaned_data['stopped_by_datetime']

            # ذخیره تغییرات در دیتابیس
            reminder.save()

        return render(request, 'reminder_module/update_medical_page.html', context={'form': form})


@login_required()
def deleteReminder(request, primary_key):
    reminder = MedicineReminder.objects.get(id=primary_key, user=request.user)
    reminder.delete()
    return render(request)


class ReserveDoctorView(View):
    def get(self, request):
        departments = Doctors.objects.values_list('proficiency', flat=True).distinct()
        doctors_by_department = {}
        for department in departments:
            doctors_by_department[department] = Doctors.objects.filter(proficiency=department)

        form = ReserveDoctorForm()
        return render(request, 'reminder_module/reserve_doctor_patient.html', {
            'departments': departments,
            'doctors_by_department': doctors_by_department,
            'form': form
        })

    def post(self, request):
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('day')
        time = request.POST.get('time')
        comments = request.POST.get('comments')
        errors = {}

        if not doctor_id or not date or not time:
            errors['general'] = 'تمامی فیلدهای ضروری را پر کنید.'
        else:
            doctor = Doctors.objects.get(id=doctor_id)
            availabilities = Availability.objects.filter(doctor=doctor, day_of_week=date)
            if not availabilities.exists():
                errors['date'] = 'پزشک در این روز از هفته در دسترس نیست.'
            else:
                try:
                    time_obj = datetime.strptime(time, '%H:%M').time()
                except ValueError:
                    errors['time'] = 'زمان معتبر نیست.'
                is_time_valid = any(
                    availability.start_time <= time_obj <= availability.end_time for availability in availabilities
                )

                if not is_time_valid:
                    errors['time'] = 'زمان انتخاب شده در دسترس نمی‌باشد.'

                # بررسی اینکه آیا این زمان قبلاً توسط بیمار دیگری رزرو شده است یا خیر
                elif ReserveDoctor.objects.filter(doctor=doctor, date=date, time=time_obj).exists():
                    errors['time'] = 'این زمان قبلاً رزرو شده است. لطفاً ساعت دیگری انتخاب کنید.'

        if not errors:
            # ذخیره رزرو
            ReserveDoctor.objects.create(
                doctor=doctor,
                user=request.user,
                date=date,
                time=time_obj,
                comments=comments
            )
            return render(request, 'reminder_module/reserve_doctor_patient.html', {
                'success': True
            })

        # اگر خطا وجود داشته باشد، داده‌ها و خطاها را دوباره ارسال می‌کنیم
        departments = Doctors.objects.values_list('proficiency', flat=True).distinct()
        doctors_by_department = {}
        for department in departments:
            doctors_by_department[department] = Doctors.objects.filter(proficiency=department)

        return render(request, 'reminder_module/reserve_doctor_patient.html', {
            'departments': departments,
            'doctors_by_department': doctors_by_department,
            'errors': errors,
            'doctor_id': doctor_id,
            'date': date,
            'time': time,
            'comments': comments,
        })


def get_available_times(request, doctor_id, day):
    doctor = Doctors.objects.get(id=doctor_id)
    availability = doctor.availabilities.filter(day_of_week=day).first()

    reserved_times = list(ReserveDoctor.objects.filter(doctor=doctor).values_list('time', flat=True))
    reserved_times = [rt.strftime('%H:%M') for rt in reserved_times]

    available_times = []
    if availability:
        start_time = availability.start_time
        print("start_time", start_time)

        while start_time < availability.end_time:
            formatted_time = start_time.strftime('%H:%M')
            if formatted_time not in reserved_times:
                available_times.append({
                    'value': formatted_time,
                    'label': formatted_time
                })
            start_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=10)).time()

    return JsonResponse({'times': available_times})


def get_available_days(request, doctor_id):
    doctor = Doctors.objects.get(id=doctor_id)
    availabilities = doctor.availabilities.all()
    available_days = [{'value': availability.day_of_week, 'label': availability.get_day_of_week_display()} for
                      availability in availabilities]
    return JsonResponse({'days': available_days})


