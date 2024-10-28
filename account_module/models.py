from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
from jalali_date import date2jalali


# Create your models here.

class Users(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name='نقش کاربر',default='patient')
    username = models.CharField(max_length=130, null=True, blank=True, verbose_name='یوزر نیم')
    first_name = models.CharField(max_length=255, verbose_name='نام')
    last_name = models.CharField(max_length=255, verbose_name='نام خانوادگی')
    email = models.EmailField(max_length=100, unique=True, null=False, blank=False, verbose_name='ایمیل')
    doctor_email = models.EmailField(max_length=100, unique=True, null=True, blank=True, verbose_name='ایمیل پزشکان')
    email_code_doctor = models.CharField(max_length=11, unique=True, null=True, blank=True,
                                         verbose_name='کد ارسالی ایمیل')

    email_code = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name='کد ارسالی ایمیل')
    password = models.CharField(max_length=255, blank=False, null=False, verbose_name='پسورد')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('-', '-'), ('مرد', 'مرد'), ('زن', 'زن')], blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    profile_completion = models.IntegerField(default=0)  # For tracking profile completion percentage
    location = models.CharField(max_length=100, blank=True, null=True)
    referral_time_patient = models.DateTimeField(verbose_name='تاریخ نوبت بیمار', null=True,blank=True)

    # login
    phone_number = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره همراه')
    phone_number_sms = models.CharField(max_length=11, null=True, blank=True, verbose_name='کد ارسالی تلفن همراه')
    last_login_request = models.DateTimeField(null=True, blank=True, verbose_name='آخرین ورود')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ اکانت ساخته شده')
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Is the user allowed to have access to the admin',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Is the user account currently active',
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_groups',
        blank=True,
        verbose_name='گروه‌ها'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_user_permissions',
        blank=True,
        verbose_name='دسترسی‌ها'
    )
    USERNAME_FIELD = "email"
    objects = UserManager()

    def get_jalali_create_date(self):
        return date2jalali(self.birth_date)

    def __str__(self):
        return self.email if self.email else "No Email"
