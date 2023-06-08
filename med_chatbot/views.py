from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
# from user_data.models import
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password

def index(request):
    return render(request, "index.html")