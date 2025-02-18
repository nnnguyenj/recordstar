from django.urls import path
from . import views

urlpatterns = [
    # Example URL pattern:
    # path('example/', views.example_view, name='example'),
    path("", views.IndexView.as_view(), name="index"),
    path("add_item/", views.add_item, name="add_item"),
]