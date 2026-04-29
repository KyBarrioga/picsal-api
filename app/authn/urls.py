from django.urls import path

from authn.views import LoginView, LogoutView, RefreshView, SignupView


urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("signup/", SignupView.as_view(), name="auth-signup"),
]
