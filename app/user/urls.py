from django.urls import path

from user.views import ManageUserView


urlpatterns = [
    path("me/", ManageUserView.as_view(), name="me"),
]

