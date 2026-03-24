"""URL configuration for the Picsal API project."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs-swagger"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="api-schema"), name="api-docs-redoc"),
    path("api/", include("core.urls")),
    path("api/user/", include("user.urls")),
]
