from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.urls import reverse
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.account.utils import perform_login
from django.contrib.auth.decorators import login_required

# Create your views here.

def index_view(request):
    if request.method == "POST":
        account_type = request.POST.get("account_type", "P") #defaults to patron
        request.session["account_type"] = account_type #stores in session
        return redirect(reverse("socialaccount_login", args=["google"])) #redirects to Google login
    return render(request, "index.html")

def logout_view(request):
    logout(request)
    return redirect("recordstar/")

@login_required
def dashboard_view(request):
    return render(request, "dashboard.html", {"user": request.user})
