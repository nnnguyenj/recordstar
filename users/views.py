from django.shortcuts import render, redirect
from django.contrib.auth import logout
from allauth.socialaccount.providers.google.views import oauth2_login

def index_view(request):
    return render(request, "users/index.html")

def logout_view(request):
    logout(request)
    return redirect("recordstar/")

def google_login(request):
    if request.method == 'POST':
        account_type = request.POST.get('account_type', 'P')
        request.session['account_type'] = account_type
    return oauth2_login(request)
