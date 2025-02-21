from django.urls import path
from . import views
from .views import dashboard_view

urlpatterns = [
    path("", views.index_view, name="index"),
    path("logout", views.logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
]