from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import dashboard_view


urlpatterns = [
    path('google/login/', views.google_login, name='google_login'),
    path("", views.index_view, name="index"),
    path("logout", views.logout_view, name="logout"),
    path('dashboard/', dashboard_view, name='dashboard'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)