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
    path('dashboard/', dashboard_view, name='dashboard'),

    path("update_picture/", views.update_profile_picture, name='update_profile_picture'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)