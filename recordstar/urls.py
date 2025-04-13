from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import dashboard_view


urlpatterns = [
    # Example URL pattern:
    # path('example/', views.example_view, name='example'),
    path("", views.IndexView.as_view(), name="index"),
    path("add_item/", views.add_item_view, name="add_item"),
    path("edit_cd/<int:cd_id>/", views.edit_cd_view, name="edit_cd"),
    path("delete_cd/<int:cd_id>/", views.delete_cd_view, name="delete_cd"),
    path('dashboard/', dashboard_view, name='dashboard'),
    path("update_picture/", views.update_profile_picture, name='update_profile_picture'),
    path("search_cd/", views.search_cd_by_code, name="search_cd"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)