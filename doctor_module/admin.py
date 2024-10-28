from django.contrib import admin
from doctor_module.models import Doctors,Availability


@admin.register(Doctors)
class DemoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Doctors._meta.fields]


@admin.register(Availability)
class DemoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Availability._meta.fields]