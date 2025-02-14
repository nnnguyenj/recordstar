from django.shortcuts import render, redirect
from django.contrib.auth import logout


# Create your views here.

def index_view(request):
    return render(request, "users/index.html")

def logout_view(request):
    logout(request)
    return redirect("recordstar/")