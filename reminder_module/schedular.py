from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from account_module.utility import DAYS_TRANSLATION
from med_reminder.settings import EMAIL_HOST_USER
from .models import MedicineReminder, ReserveDoctor
from django.core.mail import send_mail
from django.db import transaction
from account_module.models import Users


def send_medication_reminders():
    now = timezone.now()
    reminders = MedicineReminder.objects.filter(
        first_time_of_intake__lte=now,
        stopped_by_datetime__gte=now
    )

    for reminder in reminders:
        try:
            user_email = reminder.user.email
        except Users.DoesNotExist:
            continue  # اگر کاربر مرتبط وجود ندارد، این یادآوری را نادیده بگیر

        interval = reminder.periodic_interval
        frequency = reminder.dosage_frequency
        first_time = reminder.first_time_of_intake

        if interval == 'روزانه':
            interval_minutes = 1440 // frequency
        elif interval == 'هفتگی':
            interval_minutes = 10080 // frequency  # 168 * 60
        elif interval == 'ماهانه':
            interval_minutes = 43200 // frequency  # 720 * 60
        else:
            continue

        last_sent_time = reminder.last_sent_time

        if last_sent_time is None or now >= last_sent_time + timezone.timedelta(minutes=interval_minutes):
            send_mail(
                'ارسال دارو',
                f'تایم خوردن دارو ها : {reminder.medicine_name}',
                EMAIL_HOST_USER,
                [user_email],
            )
            # به‌روزرسانی زمان آخرین ارسال
            reminder.last_sent_time = now
            reminder.save(update_fields=['last_sent_time'])  # به‌روزرسانی سریع‌تر با `update_fields`

    return HttpResponse('یادآوری‌ها با موفقیت ارسال شدند!')


def send_reservation_reminders():
    now = timezone.now()

    start_of_week = now - timedelta(days=(now.weekday() + 2) % 7)
    print(start_of_week)
    one_time_later = (now + timedelta(hours=4.5)).replace(second=0, microsecond=0)
    # معادل روزهای هفته به فرمت اختصاری
    days_mapping = {
        'Saturday': 'SA',
        'Sunday': 'SU',
        'Monday': 'MO',
        'Tuesday': 'TU',
        'Wednesday': 'WE',
        'Thursday': 'TH',
        'Friday': 'FR'
    }

    # روز فعلی به فرمت اختصاری (مانند MO برای Monday)
    today = days_mapping[timezone.localtime().strftime('%A')]
    # فیلتر کردن رزروهایی که در هفته جاری ایجاد شده‌اند، برای امروز هستند و دقیقاً یک ساعت بعد است
    reservations = ReserveDoctor.objects.filter(
        created_at__gte=start_of_week,  # رزروهای هفته جاری
        time=one_time_later.time(),  # دقیقاً یک ساعت بعد
        date=today  # فقط رزروهای امروز بر اساس فرمت اختصاری
    )

    for reserve in reservations:
        try:
            patient_email = reserve.user.email
            doctor_email = reserve.doctor.user.email

        except Users.DoesNotExist:
            continue  # در صورت عدم وجود ایمیل، ادامه بده

        appointment_time = reserve.time
        appointment_day = DAYS_TRANSLATION.get(reserve.date, reserve.date)

        # ارسال ایمیل به دکتر
        send_mail(
            'یادآوری پزشک محترم',
            f'''
               پزشک محترم جناب {' '} {reserve.doctor.first_name}{' '}{reserve.doctor.last_name} شما در روز {' '}{appointment_day} 
                بیماری به نام{' '}{reserve.user.first_name}{' '}{reserve.user.last_name} در ساعت  {appointment_time}   دارید
            ''',
            EMAIL_HOST_USER,
            [doctor_email],
        )

        # ارسال ایمیل به بیمار
        send_mail(
            'یادآوری بیمار محترم',
            f'''
                بیمار محترم جناب{' '}{reserve.user.first_name}{' '}{reserve.user.last_name} شما در روز {' '}{appointment_day}
                نوبت با دکتر{' '}{reserve.doctor.first_name}{' '}{reserve.doctor.last_name} در ساعت {appointment_time}دارید
                 
                ''',
            EMAIL_HOST_USER,
            [patient_email],
        )

    return HttpResponse('یادآوری رزرو‌ها با موفقیت ارسال شد!')
