from django import forms
# from .models import Medication
#
# class MedicationForm(forms.ModelForm):
#     start_time = forms.DateTimeField()
#     times_per_day = forms.IntegerField(min_value=1, max_value=24)
#
#     class Meta:
#         model = Medication
#         fields = ['medication_name', 'dosage', 'interval_hours', 'start_time', 'times_per_day']
from django import forms
from django.core import validators
from .models import MedicineReminder
from django.core.exceptions import ValidationError
from doctor_module.models import Availability
from reminder_module.models import ReserveDoctor


class MedicineReminderForm(forms.Form):
    ROUTE_OF_ADMINISTRATION_CHOICES = [
        ('خوراکی', 'خوراکی'),
        ('عضلانی', 'عضلانی'),
        ('زیر جلدی', 'زیر جلدی'),
    ]
    DOSAGE_FORM_CHOICES = [
        ('قرص', 'قرص',),
        ('کپسول', 'کپسول',),
        ('شربت', 'شربت',),
        ('تزریقی', 'تزریقی',)

    ]
    DOSAGE_UNIT_OF_MEASURE_CHOICES = [
        ('قرص', 'قرص',), ('کپسول', 'کپسول',), ('میلی ‌لیتر', 'میلی ‌لیتر',),

    ]
    PERIODIC_INTERVAL_CHOICES = [
        ('روزانه', 'روزانه',), ('هفتگی', 'هفتگی',), ('ماهانه', 'ماهانه',)
    ]
    medicine_name = forms.CharField(
        label='نام دارو (اجباری)',
        widget=forms.TextInput(attrs={'placeholder': 'نام دارو را وارد کنید', 'class': 'form-control'}),
        validators=[validators.MaxLengthValidator(256)],
        required=True
    )

    route_of_administration = forms.ChoiceField(
        label='نحوه استفاده دارو',
        choices=ROUTE_OF_ADMINISTRATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    dosage_form = forms.ChoiceField(
        label='فرم دارو',
        choices=DOSAGE_FORM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    dosage_unit_of_measure = forms.ChoiceField(
        label='دوز دارو(مقدار مصرف)',
        choices=DOSAGE_UNIT_OF_MEASURE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    dosage_quantity_of_units_per_time = forms.IntegerField(
        label='تعداد واحدی که درهر بار باید مصرف شود',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=True
    )

    periodic_interval = forms.ChoiceField(
        label='دوره زمانی بین هر بار مصرف دارو',
        choices=PERIODIC_INTERVAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    dosage_frequency = forms.IntegerField(
        label='تعداد دفعات مصرف دارو در یک بازه زمانی مشخص',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=True
    )

    first_time_of_intake = forms.DateTimeField(
        label='زمان شروع',
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        required=True
    )
    stopped_by_datetime = forms.DateTimeField(
        label='زمان پایان',
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        required=True
    )
    # body = models.TextField(null=True, blank=True)
    regimen_note = forms.CharField(
        label='توضیحات اضافی',
        widget=forms.Textarea(attrs={'placeholder': '', 'class': 'form-control'}),
        required=False)

    is_chronic_or_acute = forms.BooleanField(
        label='آیا بیماری شما حاد است؟'
        , required=False,
    )

    class Meta:
        model = MedicineReminder
        fields = '__all__'  # class Meta:
    #     model = MedicineReminder
    #     fields = [
    #         'medicine_name', 'route_of_administration', 'dosage_form',
    #         'dosage_unit_of_measure', 'dosage_quantity_of_units_per_time',
    #         'periodic_interval', 'dosage_frequency', 'first_time_of_intake',
    #         'stopped_by_datetime'
    #     ]


class ReserveDoctorForm(forms.ModelForm):

    class Meta:
        model = ReserveDoctor
        fields = ['doctor', 'date', 'time', 'comments']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'flatpickr form-control', 'placeholder': 'تاریخ را انتخاب کنید'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'ساعت را انتخاب کنید'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'پیام شما'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        day = cleaned_data.get('day')

        if doctor and date and time:
            # تبدیل تاریخ به روز هفته
            day_of_week = date.strftime('%a').upper()[:2]

            # بررسی در دسترس بودن دکتر در روز انتخاب شده
            availabilities = Availability.objects.filter(doctor=doctor, day_of_week=day_of_week)

            if not availabilities.exists():
                raise ValidationError('پزشک در این روز از هفته در دسترس نیست.')

            # بررسی اینکه آیا زمان انتخاب شده در بازه‌های کاری دکتر قرار دارد
            is_time_valid = any(
                availability.start_time <= time <= availability.end_time for availability in availabilities
            )

            if not is_time_valid:
                raise ValidationError('زمان انتخاب شده در دسترس نمی‌باشد.')

            # بررسی اینکه آیا این زمان قبلاً توسط بیمار دیگری رزرو شده است یا خیر
            if ReserveDoctor.objects.filter(doctor=doctor, date=date, time=time).exists():
                raise ValidationError('این زمان قبلاً رزرو شده است. لطفاً ساعت دیگری انتخاب کنید.')

        return cleaned_data