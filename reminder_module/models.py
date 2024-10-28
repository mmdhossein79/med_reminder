# your_app/models.py
from django.db import models
from account_module.models import Users
from datetime import timedelta
from django.utils import timezone

from doctor_module.models import Doctors


class MedicineReminder(models.Model):
    # make sure that every user has its own reminders isolated from others
    user = models.ForeignKey(Users, on_delete=models.CASCADE,
                             related_name="reminder_user")  # cascade behaviour means that whenever the related user gets deleted, its respective profile gets also deleted
    medicine_name = models.CharField(null=True, blank=False, max_length=256)
    route_of_administration = models.CharField(null=True, blank=False, choices=(
    ('خوراکی', 'خوراکی',), ('عضلانی', 'عضلانی',), ('زیر جلدی', 'زیر جلدی',),), max_length=256)
    dosage_form = models.CharField(null=True, blank=False, choices=(
    ('قرص', 'قرص',), ('کپسول', 'کپسول',), ('شربت', 'شربت',), ('عضلانی', 'عضلانی',),),
                                   max_length=256)  # select menu in the frontend
    dosage_unit_of_measure = models.CharField(null=True, blank=False, choices=(
    ('قرص', 'قرص',), ('شربت', 'شربت',), ('میلی لیتر', 'میلی لیتر',),),
                                              max_length=256)  # select menu in the frontend
    dosage_quantity_of_units_per_time = models.FloatField(null=True, blank=False)
    regimen_note = models.CharField(null=True, blank=True, max_length=256)
    update_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)
    last_sent_time = models.DateTimeField(null=True, blank=True, default=None)

    equally_distributed_regimen = models.BooleanField(default=True, null=True, blank=False)
    periodic_interval = models.CharField(null=True, blank=False, choices=(
    ('روزانه', 'روزانه',), ('هفتگی', 'هفتگی',), ('ماهانه', 'ماهانه',),), max_length=256)
    dosage_frequency = models.PositiveIntegerField(null=True,
                                                   blank=False)
    first_time_of_intake = models.DateTimeField(null=True, blank=False,
                                                default=timezone.now)
    is_chronic_or_acute = models.BooleanField(default=False, null=True, blank=False)
    stopped_by_datetime = models.DateTimeField(null=True, blank=True)

    # Second Approach

    # customDistributedRegimen/BooleanField
    # customDailyTime1/TimeField
    # customDailyTime1=2/TimeField
    # customDailyTime3/TimeField

    def __str__(self):
        return str(self.medicine_name) if self.medicine_name else ''


class ReserveDoctor(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE,default=None)

    date = models.CharField(
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
    time = models.TimeField()
    comments = models.TextField(null=True,blank=True)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserve for {self.doctor} on {self.date} at {self.time}"