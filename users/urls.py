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
    path("", views.index_view, name="index"),
    path("logout", views.logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("playlists/", playlists_view, name="playlists"),
    path("recent-activity/", recent_activity_view, name="recent_activity"),
    path('collection/', views.collection_view, name='collection'),
    path('add_record/', views.add_record, name='add_record'),
    path('delete_record/<int:record_id>/', views.delete_record_view, name='delete_record'),
    path("ratings/", ratings_view, name="ratings"),
    path("profile/", profile_view, name="profile"),
    path("settings/", settings_view, name="settings"),
    path("upgrade_user/<int:user_id>/", views.upgrade_user_to_librarian, name="upgrade_user"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)