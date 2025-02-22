from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Example URL pattern:
    # path('example/', views.example_view, name='example'),
    path("", views.IndexView.as_view(), name="index"),
    path("add_item/", views.add_item, name="add_item"),
    path("update_picture/", views.update_profile_picture, name='update_profile_picture'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)