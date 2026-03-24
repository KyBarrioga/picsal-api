"""Serializers for core endpoints."""
from rest_framework import serializers


class StoragePresignRequestSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    content_type = serializers.CharField(max_length=255)
    folder = serializers.CharField(max_length=100, required=False, default="users")

