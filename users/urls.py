from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import dashboard_view
from .views import (
    playlists_view, recent_activity_view, collection_view, ratings_view, 
    profile_view, settings_view, dashboard_view
)

urlpatterns = [
    path('google/login/', views.google_login, name='google_login'),
    path("", views.index_view, name="index"),
    path("logout", views.logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("playlists/", playlists_view, name="playlists"),
    path("recent-activity/", recent_activity_view, name="recent_activity"),
    path("collection/", collection_view, name="collection"),
    path("ratings/", ratings_view, name="ratings"),
    path("profile/", profile_view, name="profile"),
    path("settings/", settings_view, name="settings"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)