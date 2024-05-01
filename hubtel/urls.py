from django.urls import path

from . import views

urlpatterns = [
    path('', views.otp_form, name='otp_form'),
    path('resent/', views.resend_otp, name='resend_otp'),
    path('sms/activation/', views.send_activation_link_via_sms, name='sms')
]