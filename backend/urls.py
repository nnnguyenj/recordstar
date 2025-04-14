"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from allauth.account.views import LoginView, SignupView

urlpatterns = [
    path("", lambda request: redirect("account_login"), name="home_redirect"),  # always redirect root to login
    path("accounts/login/", LoginView.as_view(template_name="account/login.html"), name="account_login"),
    path("accounts/signup/", SignupView.as_view(template_name="account/signup.html"), name="account_signup"),
    path("google/login/", LoginView.as_view(template_name="account/google_login.html"), name="google_login"),
    path("admin/", admin.site.urls),
    path("recordstar/", include("recordstar.urls")),
    path("accounts/", include("allauth.urls")),
    path("", include("users.urls")),  # include your user views
]
