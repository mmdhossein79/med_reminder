# Generated by Django 5.0.7 on 2024-08-23 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account_module', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='referral_time_patient',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاریخ نوبت بیمار'),
        ),
    ]
