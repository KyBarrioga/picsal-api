from django.urls import path

from core.views import HealthCheckView, StoragePresignView


urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("core/storage/presign/",
         StoragePresignView.as_view(), name="storage-presign"),
]
