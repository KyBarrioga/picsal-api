"""Serializers for user endpoints."""
from rest_framework import serializers


class SupabaseAuthUserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    role = serializers.CharField()
    display_name = serializers.CharField(allow_blank=True, required=False)


class SupabaseProfileEnvelopeSerializer(serializers.Serializer):
    auth_user = SupabaseAuthUserSerializer()
    profile = serializers.JSONField(allow_null=True)
    media = serializers.ListField(
        child=serializers.JSONField(), required=False)


class SupabaseProfileUpdateSerializer(serializers.Serializer):
    profile = serializers.DictField(required=False)
