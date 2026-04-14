from django.urls import path
from uploads.views import MediaCreateView

urlpatterns = [
    path("", MediaCreateView.as_view(), name="media-create"),
]
