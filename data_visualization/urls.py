from django.urls import path
from . import views

urlpatterns = [
    path('', views.dv_home, name="dv_home"),

]