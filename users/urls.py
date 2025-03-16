from django.urls import path, include
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    playlists_view, recent_activity_view, collection_view, ratings_view, 
    profile_view, settings_view, dashboard_view, add_record_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('google/login/', views.google_login, name='google_login'),
    path('accounts/', include('allauth.urls')),
    path("", views.index_view, name="index"),
    path("logout", views.logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("playlists/", playlists_view, name="playlists"),
    path("recent-activity/", recent_activity_view, name="recent_activity"),
    path("collection/", collection_view, name="collection"),
    path("add-record/", add_record_view, name="add_record"),
    path("ratings/", ratings_view, name="ratings"),
    path("profile/", profile_view, name="profile"),
    path("settings/", settings_view, name="settings"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)