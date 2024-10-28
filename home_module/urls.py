from django.urls import path
from . import views
from account_module.views import *
from django.conf.urls.static import static
urlpatterns = [
    path('',views.HomeView.as_view(),name='home'),
    path('about_us',views.AboutView.as_view(),name='about_us'),
    path('services/', views.ServicesView.as_view(), name='service_detail'),
    path('doctor_team/', views.DoctorTeamView.as_view(), name='doctor_team')

]