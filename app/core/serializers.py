"""Serializers for core endpoints."""
import uuid

from rest_framework import serializers


class StoragePresignRequestSerializer(serializers.Serializer):
    image = serializers.FileField(write_only=True)

    def validate(self, attrs):
        image = attrs.get("image")
        content_type = getattr(image, "content_type", "")
        if not content_type.startswith("image/"):
            raise serializers.ValidationError(
                {"image": "Only image uploads are supported."})

        attrs["file_name"] = image.name
        attrs["content_type"] = content_type
        return attrs


class StoragePresignResponseSerializer(serializers.Serializer):
    upload_url = serializers.URLField()
    object_key = serializers.CharField()
    public_url = serializers.URLField()


def build_r2_key(
            user_id: uuid.UUID, filename: str, folder: str = "users"
        ) -> str:
    """Build a namespaced R2 object key for a user-owned file."""
    extension = ""
    if "." in filename:
        extension = f".{filename.rsplit('.', 1)[-1].lower()}"
    return f"{folder}/{user_id}/{uuid.uuid4()}{extension}"
