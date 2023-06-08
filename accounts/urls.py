from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name="login"),
    path('signup/', views.signup, name="signup"),
    path('doctor_signup/', views.doctor_signup, name="doctor_signup"),
    path('signout/', views.signout, name="signout"),
    path('patientprofile/', views.showPatientProfile, name="showPatientProfile"),
    path('doctorprofile/', views.showDoctorProfile, name="showDoctorProfile"),
]
