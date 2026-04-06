"""Core API views."""
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, serializers, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import SupabaseUser
from core.serializers import (
    StoragePresignRequestSerializer,
    StoragePresignResponseSerializer,
    build_r2_key,
)
from core.services import R2StorageService


class HealthCheckView(APIView):
    """Basic application health endpoint."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "picsal-api",
                "modules": ["core", "user"],
            }
        )


class StoragePresignView(APIView):
    """Create signed upload URLs for authenticated users."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    storage_service_class = R2StorageService

    @extend_schema(
        operation_id="storage_presign",
        tags=["core"],
        request=StoragePresignRequestSerializer,
        responses={201: StoragePresignResponseSerializer},
        examples=[OpenApiExample("Multipart image upload", request_only=True)],
    )
    def post(self, request):
        serializer = StoragePresignRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: SupabaseUser = request.user
        object_key = build_r2_key(
            user_id=user.id,
            filename=serializer.validated_data["file_name"],
        )

        service = self.storage_service_class()
        try:
            upload_url = service.generate_upload_url(
                object_key=object_key,
                content_type=serializer.validated_data["content_type"],
            )
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

        response_serializer = StoragePresignResponseSerializer(
            data={
                "upload_url": upload_url,
                "object_key": object_key,
                "public_url": service.build_public_url(object_key),
            }
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.validated_data, status=status.HTTP_201_CREATED)
