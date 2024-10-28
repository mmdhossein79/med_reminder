from django.urls import path
from . import views
from account_module.views import *


urlpatterns = [
    path('',views.RegisterView.as_view(),name='register_doctor'),
    path('login/', views.LoginView.as_view(), name='login_doctor'),
    path('forget-password/', views.ForgetPasswordView.as_view(), name='forget_password_doctor'),
    path('get_code/<str:username>/',views.GetCodeView.as_view(),name='get_code_doctor'),
    path('more_information/', views.MoreInformationDoctorView.as_view(), name='more_information_doctor'),
    path('success_register_doctor/',views.success_register_doctor,name='success_register_doctor'),
    path('doctor_dashboard/',views.DoctorsView.as_view(),name='doctor_dashboard'),
    path('verify_reset_code/<str:email>/',views.VerifyResetCodeView.as_view(),name='verify_reset_code_doctor'),
    path('set_new_password/<str:email>/',views.SetNewPasswordView.as_view(),name='set_new_password_doctor'),
    path('reset-password/success/', reset_password_success, name='reset_password_success_doctor'),
    path('doctor_appointment/',views.DoctorAppointmentsView.as_view(),name='doctor_appointment'),
    path('doctor_messages/',views.DoctorMessagesView.as_view(),name='doctor_messages'),
    path('doctor_profile_setting/', views.DoctorProfileSettingView.as_view(), name='doctor_profile_setting'),
    path('patient_list/', views.PatientListView.as_view(), name='patient_list'),
    path('doctor_chat/', views.DoctorChatView.as_view(), name='doctor_chat'),
    path('delete-user-doctor/', views.delete_account, name='delete_user_doctor'),
    path('doctor-schedule/', views.DoctorAvailabilityView.as_view(), name='doctor-schedule'),
    path('clear_availability/', views.clear_availability, name='clear_availability'),
    path('cancel-appointment/<int:reserve_id>/', views.CancelAppointmentView.as_view(), name='cancel_appointment'),
    path('logout/', views.LogoutView.as_view(), name='logout_page_doctor'),
    path('chat/<int:recipient_id>/', views.DoctorChatView.as_view(), name='chat_view'),

]