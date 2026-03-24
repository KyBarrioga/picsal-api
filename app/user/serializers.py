"""Serializers for user endpoints."""
from rest_framework import serializers

from core.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "email",
            "display_name",
            "avatar_path",
            "role",
            "metadata",
            "last_login_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "role",
            "metadata",
            "last_login_at",
            "created_at",
            "updated_at",
        ]

