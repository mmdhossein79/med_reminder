from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
# Create your models here.
from jalali_date import date2jalali
# from account_module.models import Users
from account_module.models import Users


class Doctors(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=200, null=True, blank=True, verbose_name='تخصص')
    first_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='نام پزشک')
    last_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='نام خانوادگی')
    referral_time = models.DateTimeField(verbose_name='تاریخ نوبت بیماران', null=True,blank=True)
    medical_degree_picture = models.ImageField(upload_to='medical_degree_picture/', blank=True, null=True)
    activate_account_doctor = models.BooleanField(default=False, verbose_name='فعال/غیر فعال شدن اکانت دکتر ها')
    profile_image = models.ImageField(upload_to='profile_image_doctor/', blank=True, null=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره همراه')
    bio = models.TextField(blank=True, null=True)
    price_doctor = models.CharField(max_length=200, null=True, blank=True, verbose_name='هزینه ویزیت')
    address_doctor = models.CharField(max_length=200, null=True, blank=True, verbose_name='آدرس مطب دکتر')

    def __str__(self):
        # Return the email or a string representation of the associated user
        return self.user.email if self.user.email else "No Email"


class Availability(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ('SA', 'شنبه'),
            ('SU', 'یکشنبه'),
            ('MO', 'دوشنبه'),
            ('TU', 'سه شنبه'),
            ('WE', 'چهارشنبه'),
            ('TH', 'پنج شنبه'),
        ],
        verbose_name='روز هفته'
    )
    start_time = models.TimeField(verbose_name='ساعت شروع',blank=True,null=True)
    end_time = models.TimeField(verbose_name='ساعت پایان',blank=True,null=True)

    def __str__(self):
        return f"{self.doctor.user.first_name} {self.doctor.user.last_name} - {self.get_day_of_week_display()} {self.start_time} - {self.end_time}"


class ChatMessage(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField(verbose_name='پیام')
    timestamp = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.email} to {self.recipient.email}: {self.message[:30]}"