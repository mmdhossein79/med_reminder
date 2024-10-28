import jdatetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from doctor_module.models import Doctors, ChatMessage
from doctor_module.forms import *
from account_module.utility import get_random_number, is_valid_email
from doctor_module.email_service import send_email
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from account_module.models import Users
from reminder_module.models import MedicineReminder, ReserveDoctor
from account_module.utility import DAYS_TRANSLATION
from django.utils import timezone
from datetime import timedelta
from itertools import chain
from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from khayyam import JalaliDate


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        context = {
            'register_form': register_form
        }
        return render(request, 'doctor_module/register.html', context)

    def post(self, request):
        register_form = RegisterForm(request.POST)

        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            if is_valid_email(username):
                try:
                    user_exists = Doctors.objects.filter(user__email=username).exists()
                    if user_exists:
                        register_form.add_error('username', 'ایمیل وارد شده تکراری می‌باشد')
                    else:
                        new_user = Users(
                            email=username,
                            email_code_doctor=get_random_number(),
                            role='doctor'

                        )
                        new_user.save()
                        new_doctor = Doctors(
                            user=new_user,
                            # اگر اطلاعات اولیه‌ای برای دکتر داری، اینجا اضافه کن
                        )
                        new_doctor.save()
                        send_email('یک نامه از طرف داروخانه', new_user.email, {'email_code_doctor': new_user},
                                   'activate_account_doctor.html')
                        return redirect('get_code_doctor', username=username)
                except ValidationError:
                    register_form.add_error('username', 'ایمیل وارد شده معتبر نمی‌باشد')

        context = {
            'register_form': register_form
        }
        return render(request, 'doctor_module/register.html', context)


class GetCodeView(View):
    def get(self, request, username):
        code_form = GetCodeForm()
        context = {
            'code_form': code_form,
            'username': username
        }
        return render(request, 'doctor_module/get_code.html', context)

    def post(self, request, username):

        code_form = GetCodeForm(request.POST)
        if code_form.is_valid():
            code = code_form.cleaned_data.get('code')
            try:
                user = Users.objects.get(email__iexact=username)
                if code.isdigit() and user.email_code_doctor.isdigit() and code == user.email_code_doctor and user.role == "doctor":
                    login(request, user)
                    return redirect('more_information_doctor')
                else:
                    code_form.add_error('code', 'کلمه عبور اشتباه است')
            except Doctors.DoesNotExist:
                code_form.add_error('code', 'کاربری وجود ندارد')

        context = {
            'code_form': code_form,
            'username': username
        }
        return render(request, 'doctor_module/get_code.html', context)


class LoginView(View):
    def get(self, request):
        login_form = LoginForm()
        context = {
            'login_form': login_form
        }

        return render(request, 'doctor_module/login.html', context)

    def post(self, request: HttpRequest):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_email = login_form.cleaned_data.get('email')
            user_pass = login_form.cleaned_data.get('password')
            user: Doctors = Doctors.objects.filter(user__email__iexact=user_email).first()
            if user:
                is_doctor = user.user
                if user is not None and is_doctor.role == "doctor":
                    if user.activate_account_doctor:
                        users = user.user
                        is_password_correct = users.check_password(user_pass)
                        if is_password_correct:
                            login(request, users)
                            next_url = request.GET.get('next', 'doctor_dashboard')
                            return redirect(next_url)
                        else:
                            login_form.add_error('email', 'کلمه عبور اشتباه است')
                    else:
                        login_form.add_error('email', 'حساب شما فعال نشده است')

                else:
                    login_form.add_error('email', 'کاربری با مشخصات وارد شده یافت نشد')
            else:
                login_form.add_error('email', 'کاربری با مشخصات وارد شده یافت نشد')

        context = {
            'login_form': login_form
        }

        return render(request, 'doctor_module/login.html', context)


class ForgetPasswordView(View):
    def get(self, request: HttpRequest):
        forget_pass_form = ForgotPasswordForm()
        # reset_pass_form = ResetPasswordForm()
        context = {
            'forget_pass_form': forget_pass_form,
            # 'reset_code_form': reset_pass_form,
            'email_sent': False  # وضعیت ارسال ایمیل
        }
        return render(request, 'doctor_module/forgot_password.html', context)

    def post(self, request: HttpRequest):
        forget_pass_form = ForgotPasswordForm(request.POST)

        if 'email' in request.POST:
            if forget_pass_form.is_valid():
                user_email = forget_pass_form.cleaned_data.get('email')
                user: Doctors = Doctors.objects.filter(user__email__iexact=user_email).first()
                if user is not None:
                    if user.activate_account_doctor:
                        activate_code = user.user
                        activate_code.email_code_doctor = get_random_number()
                        activate_code.save()
                        send_email('بازیابی کلمه عبور', user_email, {'user': activate_code}, 'forgot_code_temp.html')
                        return redirect('verify_reset_code_doctor', email=user_email)

                    else:
                        forget_pass_form.add_error('email', 'حساب کاربری فعال نشده است.')

                else:
                    forget_pass_form.add_error('email', 'کاربری با این ایمیل وجود ندارد.')

        context = {
            'forget_pass_form': forget_pass_form,
            # 'reset_code_form': reset_pass_form,
            'email_sent': False  # اگر ایمیل ارسال نشده باشد
        }
        return render(request, 'doctor_module/forgot_password.html', context)


class VerifyResetCodeView(View):
    def get(self, request, email):
        form = ResetPasswordForm()
        context = {
            'reset_code_form': form,
            'email': email
        }
        return render(request, 'doctor_module/verify_reset_code.html', context)

    def post(self, request, email):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            user = Doctors.objects.filter(user__email__iexact=email).first()

            if user:
                code_email = user.user
                if code.isdigit() and code_email.email_code_doctor.isdigit() and code == code_email.email_code_doctor:
                    return redirect('set_new_password_doctor', email=email)

                else:
                    form.add_error('code', 'کد وارد شده صحیح نیست.')
            else:
                form.add_error('code', 'حساب کاربری یافت نشد')

        context = {
            'reset_code_form': form,
            'email': email
        }
        return render(request, 'doctor_module/verify_reset_code.html', context)


class SetNewPasswordView(View):
    def get(self, request, email):
        form = SetPasswordForm()
        context = {
            'set_pass_form': form,
            'email': email
        }
        return render(request, 'doctor_module/set_pass.html', context)

    def post(self, request, email):
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')
            user = Doctors.objects.filter(user__email__iexact=email).first()
            if user is not None:
                if password == confirm_password and user.user.role == "doctor":
                # if password.isdigit() and confirm_password.isdigit() and password == confirm_password and :
                    user_set = user.user
                    user_set.set_password(password)
                    user_set.save()
                    return redirect('reset_password_success_doctor')
                else:
                    form.add_error('confirm_password', 'اعداد وارد شده یکی نیست')
            else:
                form.add_error('password', 'یوزر یافت نشد')
        context = {
            'set_pass_form': form,
            'email': email
        }
        return render(request, 'doctor_module/set_pass.html', context)


def reset_password_success(request):
    return render(request, 'doctor_module/success_message.html')


class MoreInformationDoctorView(View):
    def get(self, request):
        more_info = MoreInformationDoctorForm()
        return render(request, 'doctor_module/more_information_doctors.html', {'more_info': more_info})

    def post(self, request):
        users = request.user
        more_info = MoreInformationDoctorForm(request.POST, request.FILES)
        if users.is_authenticated:
            if more_info.is_valid():
                user_doctor = Doctors.objects.filter(user__email__iexact=users).first()
                name = more_info.cleaned_data.get('first_name')
                last_name = more_info.cleaned_data.get('last_name')
                password = more_info.cleaned_data.get('password')
                medical_degree_picture = more_info.cleaned_data.get('medical_degree_picture')
                proficiency = more_info.cleaned_data.get('proficiency')
                pass_user = user_doctor.user
                pass_user.set_password(password)
                user_doctor.first_name = name
                user_doctor.last_name = last_name
                user_doctor.medical_degree_picture = medical_degree_picture
                user_doctor.proficiency = proficiency
                user_doctor.save()
                pass_user.save()  # ذخیره تغییرات در دیتابیس

                return redirect('success_register_doctor')
        else:
            return redirect('login_doctor')

        context = {
            "more_info": more_info
        }
        return render(request, 'doctor_module/more_information_doctors.html', context)


class DoctorsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            dr_users = Doctors.objects.filter(user__email__iexact=user).first()
            first_name = dr_users.first_name if dr_users.first_name else "_"
            last_name = dr_users.last_name if dr_users.last_name else "_"
            proficiency = dr_users.proficiency if dr_users.proficiency else "_"
            referral_time = dr_users.referral_time if dr_users.referral_time else "_"
            today = timezone.now().date()
            week_ago = today - timedelta(days=1)
            reserve = ReserveDoctor.objects.filter(doctor__user__email=user, created_at__gt=week_ago).order_by(
                '-created_at')

            past_reserves = ReserveDoctor.objects.filter(created_at__lt=week_ago, doctor__user__email=user)
            all_reserves = chain(reserve, past_reserves)

            for r in all_reserves:
                # تبدیل تاریخ تولد هر کاربر به شمسی
                birth_date = jdatetime.datetime.fromgregorian(
                    date=r.user.birth_date).strftime('%Y/%m/%d') if r.user.birth_date else "_"

                # ترجمه روز هفته به فارسی
                r.date = DAYS_TRANSLATION.get(r.date, r.date)

                # تبدیل زمان به 24 ساعته
                r.time = r.time.strftime('%H:%M')

                # شما می‌توانید تاریخ تولد را به صورت جداگانه به هر رکورد اضافه کنید یا در صفحه HTML استفاده کنید.
                r.user_birth_date = birth_date
            if reserve.exists() or past_reserves.exists():
                daily_current_reserves = reserve.annotate(day=TruncDay('created_at')).values('day').annotate(
                    count=Count('id')).order_by('day')
                daily_past_reserves = past_reserves.annotate(day=TruncDay('created_at')).values('day').annotate(
                    count=Count('id')).order_by('day')

                current_reserves_dates = [JalaliDate(entry['day']).strftime('%Y-%m-%d') if entry['day'] else '' for
                                          entry in daily_current_reserves]
                current_reserves_counts = [entry['count'] for entry in daily_current_reserves]
                past_reserves_dates = [JalaliDate(entry['day']).strftime('%Y-%m-%d') if entry['day'] else '' for entry
                                       in daily_past_reserves]
                past_reserves_counts = [entry['count'] for entry in daily_past_reserves]
            else:
                current_reserves_dates = []
                current_reserves_counts = []
                past_reserves_dates = []
                past_reserves_counts = []
            return render(request, 'doctor_module/doctor_dashboard.html', {'first_name': first_name,
                                                                           'last_name': last_name,
                                                                           'proficiency': proficiency,
                                                                           'dr_users': dr_users,
                                                                           'referral_time': referral_time,
                                                                           'reserve': reserve,
                                                                           'past_reserve': past_reserves,
                                                                           'current_reserves_dates': current_reserves_dates,
                                                                           'current_reserves_counts': current_reserves_counts,
                                                                           'past_reserves_dates': past_reserves_dates,
                                                                           'past_reserves_counts': past_reserves_counts,
                                                                           })
        else:
            return redirect('login_doctor')


def success_register_doctor(request):
    return render(request, 'doctor_module/success_register.html')


class DoctorAppointmentsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            dr_users = Doctors.objects.filter(user__email__iexact=user).first()
            first_name = dr_users.first_name if dr_users.first_name else "_"
            last_name = dr_users.last_name if dr_users.last_name else "_"
            proficiency = dr_users.proficiency if dr_users.proficiency else "_"
            referral_time = dr_users.referral_time if dr_users.referral_time else "_"
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            reserve = ReserveDoctor.objects.filter(doctor__user__email=user, created_at__gt=week_ago).order_by(
                '-created_at')
            # صفحه‌بندی
            paginator = Paginator(reserve, 10)  # 10 رزرو در هر صفحه

            # شماره صفحه فعلی را از درخواست URL دریافت کنید، پیش‌فرض 1 است
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            # در حلقه به رزروهای کاربر دسترسی پیدا می‌کنیم
            for r in page_obj:
                # تبدیل تاریخ تولد هر کاربر به شمسی
                birth_date = jdatetime.datetime.fromgregorian(
                    date=r.user.birth_date).strftime('%Y/%m/%d') if r.user.birth_date else "_"

                r.date = DAYS_TRANSLATION.get(r.date, r.date)

                r.time = r.time.strftime('%H:%M')

                r.user_birth_date = birth_date

            return render(request, 'doctor_module/doctor_appointment.html', {
                'first_name': first_name,
                'last_name': last_name,
                'proficiency': proficiency,
                'dr_users': dr_users,
                'referral_time': referral_time,
                'reserve': page_obj  # ارسال صفحه‌بندی شده به قالب
            })
        else:
            return redirect('login_doctor')

    def post(self, request):
        return render(request, 'doctor_module/doctor_appointment.html')


class DoctorMessagesView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            dr_users = Doctors.objects.filter(user__email__iexact=user).first()
            first_name = dr_users.first_name if dr_users.first_name else "_"
            last_name = dr_users.last_name if dr_users.last_name else "_"
            proficiency = dr_users.proficiency if dr_users.proficiency else "_"
            referral_time = dr_users.referral_time if dr_users.referral_time else "_"

            return render(request, 'doctor_module/doctor_messages.html', {'first_name': first_name,
                                                                          'last_name': last_name,
                                                                          'proficiency': proficiency,
                                                                          'dr_users': dr_users,
                                                                          'referral_time': referral_time})
        else:
            return redirect('login_doctor')

    def post(self, request):
        return render(request, 'doctor_module/doctor_messages.html')


class DoctorProfileSettingView(View):
    def get(self, request):
        profile_form = DoctorProfileForm()
        change_password_form = DoctorChangePasswordForm()
        user = Doctors.objects.filter(user__email__iexact=request.user).first()
        # age = calculate_age(user.birth_date)  if user.birth_date else "-"
        phone = user.phone_number if user.phone_number else "-"
        # birth_date = convert_gregorian_to_jalali(user.birth_date) if user.birth_date else "-"
        # gender = user.gender if user.gender else "-"
        context = {
            'profile_form': profile_form,
            'change_password_form': change_password_form,
            'show_profile': user,
            'phone': phone,
            # 'gender':gender
        }
        return render(request, 'doctor_module/doctor_profile_setting.html', context)

    def post(self, request):
        profile_form = DoctorProfileForm(request.POST, request.FILES)
        change_password_form = DoctorChangePasswordForm(request.POST)
        user: Doctors = Doctors.objects.filter(user__email__iexact=request.user).first()
        if profile_form.is_valid():
            if profile_form.cleaned_data.get('phone_number'):
                user.phone_number = profile_form.cleaned_data.get('phone_number')
            if profile_form.cleaned_data.get('bio'):
                user.bio = profile_form.cleaned_data.get('bio')
            if profile_form.cleaned_data.get('image_profile'):
                user.profile_image = profile_form.cleaned_data.get('image_profile')
            user.save()
            profile_form.add_error(None, 'تغییرات پروفایل با موفقیت ذخیره شد.')
        else:
            profile_form.add_error(None, 'خطایی در ذخیره پروفایل رخ داده است.')

        if change_password_form.is_valid():
            old_password = change_password_form.cleaned_data['old_password']
            new_password1 = change_password_form.cleaned_data['new_password1']
            new_password2 = change_password_form.cleaned_data['new_password2']
            pass_ = user.user
            if not pass_.check_password(old_password):
                change_password_form.add_error('old_password', 'رمز عبور فعلی نادرست است.')
            elif new_password1 != new_password2:
                change_password_form.add_error('new_password2', 'رمز عبور جدید و تکرار آن مطابقت ندارند.')
            else:
                pass_.set_password(new_password1)
                pass_.save()
                update_session_auth_hash(request, request.user)
                change_password_form.add_error(None, 'رمز عبور با موفقیت تغییر کرد.')
        else:
            change_password_form.add_error(None, 'خطایی در تغییر رمز عبور رخ داده است.')
        user = Doctors.objects.filter(user__email__iexact=request.user).first()
        phone = user.phone_number if user.phone_number else "-"
        context = {
            'profile_form': profile_form,
            'change_password_form': change_password_form,
            'show_profile': user,
            'phone': phone,
        }
        return render(request, 'doctor_module/doctor_profile_setting.html', context)


class PatientListView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            reserve = ReserveDoctor.objects.filter(doctor__user__email=user, created_at__gt=week_ago).order_by(
                '-created_at')
            dr_users = Doctors.objects.filter(user__email__iexact=user).first()
            first_name = dr_users.first_name if dr_users.first_name else "_"
            last_name = dr_users.last_name if dr_users.last_name else "_"
            proficiency = dr_users.proficiency if dr_users.proficiency else "_"
            referral_time = dr_users.referral_time if dr_users.referral_time else "_"
            paginator = Paginator(reserve, 10)  # 10 رزرو در هر صفحه

            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            for r in page_obj:
                birth_date = jdatetime.datetime.fromgregorian(
                    date=r.user.birth_date).strftime('%Y/%m/%d') if r.user.birth_date else "_"
                r.user_birth_date = birth_date
            return render(request, 'doctor_module/patient_list.html', {'first_name': first_name,
                                                                       'last_name': last_name,
                                                                       'proficiency': proficiency,
                                                                       'dr_users': dr_users,
                                                                       'referral_time': referral_time,
                                                                       'reserve': page_obj})

    def post(self, request):
        if request.user.is_authenticated:
            pass
        return render(request, 'doctor_module/patient_list.html')


@login_required()
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        print(user)
        users = Doctors.objects.filter(user__email__iexact=user).first()
        user.delete()
        users.delete()
        return redirect('login_doctor')
    return render(request, 'doctor_module/doctor_profile_setting.html')


@method_decorator(login_required, name='dispatch')
class DoctorAvailabilityView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login_doctor')

        days_of_week = {
            'SA': 'شنبه',
            'SU': 'یک‌شنبه',
            'MO': 'دوشنبه',
            'TU': 'سه‌شنبه',
            'WE': 'چهارشنبه',
            'TH': 'پنج‌شنبه'
        }

        doctor = get_object_or_404(Doctors, user=request.user)

        forms = {}
        for day in days_of_week.keys():
            try:
                availability = Availability.objects.get(doctor=doctor, day_of_week=day)
                form = AvailabilityForm(initial={
                    'start_time': availability.start_time,
                    'end_time': availability.end_time,
                    'day_of_week': day
                }, prefix=day)
            except Availability.DoesNotExist:
                form = AvailabilityForm(initial={'day_of_week': day}, prefix=day)

            forms[day] = form

        days_forms = [(day, days_of_week[day], forms[day]) for day in days_of_week.keys()]

        return render(request, 'doctor_module/doctor_schedule.html', {
            'days_forms': days_forms
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login_doctor')
        days_of_week = {
            'SA': 'شنبه',
            'SU': 'یک‌شنبه',
            'MO': 'دوشنبه',
            'TU': 'سه‌شنبه',
            'WE': 'چهارشنبه',
            'TH': 'پنج‌شنبه'
        }

        doctor = get_object_or_404(Doctors, user=request.user)

        forms = {}
        is_valid = True
        for day in days_of_week.keys():
            form = AvailabilityForm(request.POST, prefix=day)
            if form.is_valid():
                if form.cleaned_data['start_time'] and form.cleaned_data['end_time'] is not None:
                    Availability.objects.update_or_create(
                        doctor=doctor,
                        day_of_week=day,
                        defaults={
                            'start_time': form.cleaned_data['start_time'],
                            'end_time': form.cleaned_data['end_time'],
                        }
                    )
            else:
                is_valid = False
                print(f"Form errors for {day}: {form.errors}")
            forms[day] = form
        if is_valid:
            messages.success(request, 'با موفقیت ذخیره شد')

        days_forms = [(day, days_of_week[day], forms[day]) for day in days_of_week.keys()]
        return render(request, 'doctor_module/doctor_schedule.html', {'days_forms': days_forms})


@csrf_exempt
def clear_availability(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        doctor = get_object_or_404(Doctors, user=request.user)

        try:
            availability = Availability.objects.get(doctor=doctor, day_of_week=day)
            availability.delete()

            return JsonResponse({'success': True})
        except Availability.DoesNotExist:
            return JsonResponse({'success': False})

    return JsonResponse({'success': False})


class CancelAppointmentView(View):
    def post(self, request, reserve_id):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.user.is_authenticated:
            try:
                reserve = ReserveDoctor.objects.get(id=reserve_id, doctor__user=request.user)
                reserve.delete()
                return JsonResponse({'status': 'success', 'message': 'رزرو با موفقیت حذف شد'})
            except ReserveDoctor.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'رزرو یافت نشد'})
        return JsonResponse({'status': 'error', 'message': 'خطای احراز هویت یا درخواست غیرمجاز'})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login_doctor')


class DoctorChatView(View):
    @method_decorator(login_required)
    def get(self, request, recipient_id=None):
        if request.user.is_authenticated:
            user = request.user
            dr_users = Doctors.objects.filter(user__email__iexact=user).first()
            first_name = dr_users.first_name if dr_users.first_name else "_"
            last_name = dr_users.last_name if dr_users.last_name else "_"
            proficiency = dr_users.proficiency if dr_users.proficiency else "_"
            referral_time = dr_users.referral_time if dr_users.referral_time else "_"
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            p_reserve = ReserveDoctor.objects.filter(
                doctor__user__email=user,
                created_at__gt=week_ago
            ).select_related('user').distinct()
            unique_doctors = {}
            for reserve in p_reserve:
                unique_doctors[reserve.doctor.user_id] = reserve
            p_reserve_unique = list(unique_doctors.values())
            # p_reserve = ReserveDoctor.objects.filter(doctor__user__email=user, created_at__gt=week_ago).values('user_id','user__first_name','user__last_name').distinct()
            if recipient_id:
                recipient = get_object_or_404(Users, id=recipient_id)
                chat_messages = ChatMessage.objects.filter(
                    Q(sender=user, recipient=recipient) |
                    Q(sender=recipient, recipient=user)
                ).order_by('timestamp')
            else:
                recipient = None
                chat_messages = None

            form = ChatForm()

            context = {
                'first_name': first_name,
                'last_name': last_name,
                'proficiency': proficiency,
                'dr_users': dr_users,
                'referral_time': referral_time,
                'recipient': recipient,
                'chat_messages': chat_messages,
                'form': form,
                'reserve': p_reserve_unique
            }
            return render(request, 'doctor_module/doctor_chat.html', context)
        else:
            return redirect('login_doctor')

    @method_decorator(login_required)
    def post(self, request, recipient_id=None):
        user = request.user
        recipient = get_object_or_404(Users, id=recipient_id)

        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            ChatMessage.objects.create(sender=user, recipient=recipient, message=message)
            return redirect('chat_view', recipient_id=recipient.id)

        # If form is invalid, re-render the page with the form errors
        dr_users = Doctors.objects.filter(user__email__iexact=user).first()
        first_name = dr_users.first_name if dr_users.first_name else "_"
        last_name = dr_users.last_name if dr_users.last_name else "_"
        proficiency = dr_users.proficiency if dr_users.proficiency else "_"
        referral_time = dr_users.referral_time if dr_users.referral_time else "_"

        chat_messages = ChatMessage.objects.filter(
            Q(sender=user, recipient=recipient) |
            Q(sender=recipient, recipient=user)
        ).order_by('timestamp')

        context = {
            'first_name': first_name,
            'last_name': last_name,
            'proficiency': proficiency,
            'dr_users': dr_users,
            'referral_time': referral_time,
            'recipient': recipient,
            'chat_messages': chat_messages,
            'form': form,
        }
        return render(request, 'doctor_module/doctor_chat.html', context)
