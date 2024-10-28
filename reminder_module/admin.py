from django.contrib import admin
from reminder_module.models import MedicineReminder,ReserveDoctor
#
#
# # Register your models here.
# @admin.register(Medication)
# class DemoAdmin(admin.ModelAdmin):
#     list_display = [f.name for f in Medication._meta.fields]
#
# @admin.register(MedicationSchedule)
# class DemoAdmin(admin.ModelAdmin):
#     list_display = [f.name for f in MedicationSchedule._meta.fields]
@admin.register(MedicineReminder)
class DemoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MedicineReminder._meta.fields]

@admin.register(ReserveDoctor)
class DemoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ReserveDoctor._meta.fields]