from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("u/<str:username>/", views.profile_view, name="profile_view"),
    path("u/<str:username>/edit/", views.profile_edit, name="profile_edit"),
]
