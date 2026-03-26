"""Serializers for core endpoints."""
import uuid

from rest_framework import serializers


class StoragePresignRequestSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    content_type = serializers.CharField(max_length=255)
    folder = serializers.CharField(max_length=100, required=False, default="users")


def build_r2_key(user_id: uuid.UUID, filename: str, folder: str = "users") -> str:
    """Build a namespaced R2 object key for a user-owned file."""
    extension = ""
    if "." in filename:
        extension = f".{filename.rsplit('.', 1)[-1].lower()}"
    return f"{folder}/{user_id}/{uuid.uuid4()}{extension}"
