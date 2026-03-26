from django.urls import path

from authn.views import LoginView


urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
]

