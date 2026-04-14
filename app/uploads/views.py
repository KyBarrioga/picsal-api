from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from uploads.serializers import MediaCreateSerializer, MediaResponseSerializer
from uploads.services import UploadMediaServices


class MediaCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id="media_create",
        tags=["media"],
        request=MediaCreateSerializer,
        responses={201: MediaResponseSerializer},
        examples=[
            OpenApiExample(
                "Create media",
                value={
                    "object_key": "media/user-123/file.jpg",
                    "public_url": "https://cdn.example.com/media/user-123/file.jpg",
                    "kind": "image",
                    "title": "Hero Image",
                    "description": "Homepage hero image",
                    "preview_object_key": "media/user-123/file-preview.jpg",
                    "preview_public_url": "https://cdn.example.com/media/user-123/file-preview.jpg",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = MediaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        media = UploadMediaServices.insert_media_record(
            user_id=request.user.id,
            object_key=serializer.validated_data["object_key"],
            public_url=serializer.validated_data["public_url"],
            kind=serializer.validated_data["kind"],
            title=serializer.validated_data.get("title"),
            description=serializer.validated_data.get("description"),
            preview_object_key=serializer.validated_data["preview_object_key"],
            preview_public_url=serializer.validated_data["preview_public_url"],
        )

        response_serializer = MediaResponseSerializer(media)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
