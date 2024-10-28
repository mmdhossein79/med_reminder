from django.contrib import admin
from home_module.models import AboutMe, Service


# Register your models here.
@admin.register(AboutMe)
class DemoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in AboutMe._meta.fields]


@admin.register(Service)
class DemoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Service._meta.fields]
