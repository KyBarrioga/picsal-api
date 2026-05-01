from django.urls import path

from authn.views import (
    LoginView,
    LogoutView,
    RefreshView,
    SetupUserView,
    SignupView,
)


urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("setup/", SetupUserView.as_view(), name="auth-setup"),
    path("signup/", SignupView.as_view(), name="auth-signup"),
]
