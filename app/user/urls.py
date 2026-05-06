from django.urls import path

from user.views import ManageUserView, UserSetupView


urlpatterns = [
    path("me/", ManageUserView.as_view(), name="me"),
    path("setup/", UserSetupView.as_view(), name="user-setup"),
]
