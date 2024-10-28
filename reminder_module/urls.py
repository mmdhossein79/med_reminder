from django.urls import path
from . import views
from account_module.views import *
from django.conf.urls.static import static
urlpatterns = [
    path('create/', views.CreateReminderView.as_view(), name='create-reminder'),
    path('update/<int:reminder_id>/', views.UpdateReminderView.as_view(), name='update_reminder'),
    path('reserve_patient/', views.ReserveDoctorView.as_view(), name='reserve_patient'),
    path('get-available-times/<int:doctor_id>/<str:day>/', views.get_available_times, name='get_available_times'),
    path('get-available-days/<int:doctor_id>/', views.get_available_days, name='get_available_days'),

]