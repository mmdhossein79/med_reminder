from django.urls import path
from . import views
from account_module.views import *


urlpatterns = [
    path('',views.RegisterView.as_view(),name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('forget-password/', views.ForgetPasswordView.as_view(), name='forget_password'),
    path('get_code/<str:username>/',views.GetCodeView.as_view(),name='get_code'),
    path('patient_dashboard/',views.PatientDashboardView.as_view(),name='patient_dashboard'),
    path('verify_reset_code/<str:email>/',views.VerifyResetCodeView.as_view(),name='verify_reset_code'),
    path('set_new_password/<str:email>/',views.SetNewPasswordView.as_view(),name='set_new_password'),
    path('reset-password/success/', reset_password_success, name='reset_password_success'),
    path('user-profile/',views.UserProfileView.as_view(), name='user-profile'),
    path('delete-user/',views.delete_account, name='delete-user'),
    path('logout/', views.LogoutView.as_view(), name='logout_page'),
    path('chat-page/', views.PatientChatView.as_view(), name='patient_chat'),
    path('chat/<int:recipient_id>/', views.PatientChatView.as_view(), name='chat_view_patient'),
    path('cancel-appointment-patient/<int:reserve_id>/', views.CancelAppointmentPatientView.as_view(), name='cancel_appointment_patient'),
    path('cancel-med/<int:med_id>/', views.CancelMedicinePatientView.as_view(), name='cancel_med'),
    path('more_information_patient/', views.MoreInformationPatientView.as_view(), name='more_information_patient'),


]