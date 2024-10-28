from django.db import models

# Create your models here.
from django.db import models
from jalali_date import date2jalali
from django.urls import reverse


# Create your models here.
class AboutMe(models.Model):
    title = models.CharField(max_length=255, blank=False, verbose_name="عنوان ")
    text = models.TextField(blank=False, verbose_name="مقاله")
    image = models.ImageField(upload_to='images/about', verbose_name='تصویر مقاله')
    create_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='تاریخ ثبت')
    is_published = models.BooleanField(default=False, verbose_name='فعال/غیرفعال')

    def __str__(self):
        return self.title

    def get_jalali_create_date(self):
        return date2jalali(self.create_date)

    def get_jalali_create_time(self):
        return self.create_date.strftime('%H:%M')

    class Meta:
        verbose_name = 'درباره ما'



class Service(models.Model):
    title = models.CharField(max_length=255, blank=False, verbose_name="عنوان خدمات ")
    text = models.TextField(blank=False, verbose_name="خدمات")
    image = models.ImageField(upload_to='images/services', verbose_name='تصویر مقاله')
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=200, unique=True,
                            verbose_name='عنوان در url')
    description = models.TextField( verbose_name="توضیحات مختصر")
    is_active = models.BooleanField(default=False,verbose_name='فعال/غیرفعال')

    def save(self, *args, **kwargs):
        # self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'سرویس'
        verbose_name_plural = 'سرویس ها'
