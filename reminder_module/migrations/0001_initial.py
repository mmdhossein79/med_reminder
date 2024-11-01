# Generated by Django 5.0.7 on 2024-09-02 20:20

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('doctor_module', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicineReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine_name', models.CharField(max_length=256, null=True)),
                ('route_of_administration', models.CharField(choices=[('خوراکی', 'خوراکی'), ('عضلانی', 'عضلانی'), ('زیر جلدی', 'زیر جلدی')], max_length=256, null=True)),
                ('dosage_form', models.CharField(choices=[('قرص', 'قرص'), ('کپسول', 'کپسول'), ('شربت', 'شربت'), ('عضلانی', 'عضلانی')], max_length=256, null=True)),
                ('dosage_unit_of_measure', models.CharField(choices=[('قرص', 'قرص'), ('شربت', 'شربت'), ('میلی لیتر', 'میلی لیتر')], max_length=256, null=True)),
                ('dosage_quantity_of_units_per_time', models.FloatField(null=True)),
                ('regimen_note', models.CharField(blank=True, max_length=256, null=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_sent_time', models.DateTimeField(blank=True, default=None, null=True)),
                ('equally_distributed_regimen', models.BooleanField(default=True, null=True)),
                ('periodic_interval', models.CharField(choices=[('روزانه', 'روزانه'), ('هفتگی', 'هفتگی'), ('ماهانه', 'ماهانه')], max_length=256, null=True)),
                ('dosage_frequency', models.PositiveIntegerField(null=True)),
                ('first_time_of_intake', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('is_chronic_or_acute', models.BooleanField(default=False, null=True)),
                ('stopped_by_datetime', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminder_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReserveDoctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(choices=[('SA', 'شنبه'), ('SU', 'یکشنبه'), ('MO', 'دوشنبه'), ('TU', 'سه شنبه'), ('WE', 'چهارشنبه'), ('TH', 'پنج شنبه')], max_length=10, verbose_name='روز هفته')),
                ('time', models.TimeField()),
                ('comments', models.TextField(blank=True, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctor_module.doctors')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
