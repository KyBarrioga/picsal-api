"""Core API views."""
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import UserProfile
from core.serializers import StoragePresignRequestSerializer
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

    def post(self, request):
        serializer = StoragePresignRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: UserProfile = request.user
        object_key = UserProfile.build_r2_key(
            user_id=user.id,
            filename=serializer.validated_data["file_name"],
            folder=serializer.validated_data["folder"],
        )

        service = R2StorageService()
        try:
            upload_url = service.generate_upload_url(
                object_key=object_key,
                content_type=serializer.validated_data["content_type"],
            )
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

        return Response(
            {
                "upload_url": upload_url,
                "object_key": object_key,
                "public_url": service.build_public_url(object_key),
            },
            status=status.HTTP_201_CREATED,
        )
