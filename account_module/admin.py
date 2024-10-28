from django.contrib import admin

from account_module.models import Users
from django.contrib import admin
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import path
import openpyxl
from django.contrib import messages


# Register your models here.
# @admin.register(Users)
# class DemoAdmin(admin.ModelAdmin):
#     list_display = [f.name for f in Users._meta.fields]


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()


from django.template.response import TemplateResponse


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')

    # افزودن لینک آپلود اکسل به URLها
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.admin_site.admin_view(self.upload_excel), name='upload_excel'),
        ]
        return custom_urls + urls

    # آپلود و پردازش اکسل
    def upload_excel(self, request):
        if request.method == 'POST':
            form = ExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['excel_file']

                # باز کردن فایل اکسل
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active

                # پردازش و ذخیره داده‌های اکسل در مدل Users
                for row in sheet.iter_rows(min_row=2, values_only=True):  # از ردیف دوم شروع کنید
                    first_name, last_name, email = row  # ستون اول و دوم را به عنوان نام و نام خانوادگی دریافت کنید
                    if first_name and last_name and email:  # بررسی برای جلوگیری از ورود داده‌های خالی
                        Users.objects.create(first_name=first_name, last_name=last_name, email=email)

                messages.success(request, "داده‌ها با موفقیت وارد شدند!")
                return HttpResponse("<h2>داده‌ها با موفقیت وارد شدند!</h2><a href='../'>بازگشت به لیست کاربران</a>")

        # اگر درخواست GET باشد یا فرم نامعتبر باشد
        form = ExcelUploadForm()
        context = {
            'form': form,
        }

        # استفاده از TemplateResponse برای نمایش قالب HTML
        return TemplateResponse(request, 'admin/upload_excel.html', context)
