"""
URL patterns for the accounts app.

Covers login, logout, registration and profile pages.
"""

from django.contrib.auth import views as auth_views

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/"),
        name="logout",
    ),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
