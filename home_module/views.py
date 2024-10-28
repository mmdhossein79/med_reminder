from datetime import datetime

import jdatetime
from django.shortcuts import render
# views.py
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import TemplateView
from home_module.models import AboutMe, Service
from article_module.models import Article,ArticleComment
from django.views.generic.list import ListView
from doctor_module.models import Doctors ,Availability
from collections import defaultdict
import jdatetime


# Create your views here.
class HomeView(ListView):
    model = Article
    # paginate_by = 4
    template_name = 'home_module/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        latest_articles = self.get_queryset()[:3]
        for article in latest_articles:
            # Convert the Gregorian date to Jalali
            gregorian_date = article.create_date
            jalali_date = jdatetime.datetime.fromgregorian(datetime=gregorian_date)
            print(jalali_date)
            article.formatted_date = jalali_date.strftime('%d %B %Y')
            persian_months = {
                'Farvardin': 'فروردین',
                'Ordibehesht': 'اردیبهشت',
                'Khordad': 'خرداد',
                'Tir': 'تیر',
                'Mordad': 'مرداد',
                'Shahrivar': 'شهریور',
                'Mehr': 'مهر',
                'Aban': 'آبان',
                'Azar': 'آذر',
                'Dey': 'دی',
                'Bahman': 'بهمن',
                'Esfand': 'اسفند'
            }
            for eng, persian in persian_months.items():
                article.formatted_date = article.formatted_date.replace(eng, persian)
        context['latest_articles'] = latest_articles
        about: AboutMe = AboutMe.objects.filter(is_published=True).first()
        context['about'] = about
        services: Service = Service.objects.filter(is_active=True).order_by('-id')[:8]
        context['services'] = services
        doctors: Doctors = Doctors.objects.filter(activate_account_doctor=True)[:4]
        context['doctors'] = doctors
        article_comment: ArticleComment = ArticleComment.objects.all()
        if article_comment:
            context['article_comments'] = article_comment
        else:
            context['article_comments'] = article_comment
        availabilities = Availability.objects.filter(doctor__activate_account_doctor=True)
        if availabilities:
            week_days = {
                'SA': [],
                'SU': [],
                'MO': [],
                'TU': [],
                'WE': [],
                'TH': [],
            }

            for availability in availabilities:
                week_days[availability.day_of_week].append(availability)
            max_doctors = max(len(week_days[day]) for day in week_days)
            # for day in week_days:
            #     empty_slots = max_doctors - len(week_days[day])
            #     week_days[day].extend([None] * empty_slots)
            # context['max_doctors'] = max_doctors
            context['week_days'] = week_days
        else:
            context['week_days'] = []
            # context['max_doctors'] =[]

        return context


class AboutView(TemplateView):
    template_name = 'home_module/about_page.html'

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        about: AboutMe = AboutMe.objects.filter(is_published=True).first()
        context['about'] = about
        services: Service = Service.objects.filter(is_active=True)
        context['services'] = services
        doctors: Doctors = Doctors.objects.filter(activate_account_doctor=True)
        context['doctors'] = doctors
        return context


class ServicesView(TemplateView):
    template_name = 'home_module/services.html'

    def get_context_data(self, **kwargs):
        context = super(ServicesView, self).get_context_data(**kwargs)
        services: Service = Service.objects.filter(is_active=True)
        service = services if services else []
        context['services'] = service
        return context


class DoctorTeamView(TemplateView):
    template_name = 'home_module/doctor_team.html'

    def get_context_data(self, **kwargs):
        context = super(DoctorTeamView, self).get_context_data(**kwargs)
        doctors = Doctors.objects.filter(activate_account_doctor=True)

        availabilities = Availability.objects.filter(doctor__activate_account_doctor=True)

        grouped_availabilities = defaultdict(list)

        for availability in availabilities:
            grouped_availabilities[availability.doctor].append(availability)

        doctor_availability_list = []

        for doctor in doctors:
            times = grouped_availabilities[doctor] if doctor in grouped_availabilities else "-"
            doctor_availability_list.append((doctor, times))

        context['doctor_availability_list'] = doctor_availability_list
        return context
