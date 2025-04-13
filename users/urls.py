from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import dashboard_view
from .views import (
    recent_activity_view, collection_view, ratings_view, 
    profile_view, settings_view, dashboard_view
)

urlpatterns = [
    path("", views.index_view, name="index"),
    path("logout", views.logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("recent-activity/", views.recent_activity_view, name="recent_activity"),
    path('add_record/', views.add_record, name='add_record'),
    path('delete_record/<int:record_id>/', views.delete_record_view, name='delete_record'),
    path("ratings/", views.ratings_view, name="ratings"),
    path("profile/", profile_view, name="profile"),
    path("settings/", settings_view, name="settings"),
    path("upgrade_user/<int:user_id>/", views.upgrade_user_to_librarian, name="upgrade_user"),
    path('add-friend/<int:user_id>/', views.add_friend, name='add_friend'),
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('friends/', views.friends_view, name='friends'),
    path("collection/", views.my_collections_view, name="collection"),
    path("collection/add/", views.add_collection_view, name="add_collection"),
    path("collection/<int:collection_id>/", views.collection_detail_view, name="collection_detail"),
    path("collection/<int:collection_id>/remove/<int:cd_id>/", views.remove_cd_from_collection, name="remove_cd_from_collection"),
    path("collection/<int:collection_id>/delete/", views.delete_collection_view, name="delete_collection"),
    path("collection/<int:collection_id>/toggle-privacy/", views.toggle_collection_privacy, name="toggle_collection_privacy"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)