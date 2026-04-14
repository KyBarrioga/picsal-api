from rest_framework import serializers

"""Serializers for media upload endpoints."""
class MediaCreateSerializer(serializers.Serializer):
    object_key = serializers.CharField()
    public_url = serializers.URLField()
    kind = serializers.CharField()
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    preview_object_key = serializers.CharField()
    preview_public_url = serializers.URLField()

class MediaResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    object_key = serializers.CharField()
    public_url = serializers.URLField()
    kind = serializers.CharField()
    title = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    description = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    preview_object_key = serializers.CharField()
    preview_public_url = serializers.URLField()
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)