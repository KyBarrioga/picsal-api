"""Serializers for auth endpoints."""
from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
                                     trim_whitespace=False,
                                     style={"input_type": "password"}
                                     )


class SignupRequestSerializer(LoginRequestSerializer):
    email_redirect_to = serializers.URLField(required=False)
    data = serializers.DictField(required=False)


class SetupUserRequestSerializer(serializers.Serializer):
    display_name = serializers.CharField(max_length=150)


class AuthUserSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.EmailField(allow_blank=True, required=False)
    phone = serializers.CharField(allow_blank=True, required=False)
    role = serializers.CharField(allow_blank=True, required=False)
    aud = serializers.CharField(allow_blank=True, required=False)
    display_name = serializers.CharField(allow_blank=True, required=False)


class AuthUserResponseSerializer(serializers.Serializer):
    user = AuthUserSerializer()


class SessionSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    expires_in = serializers.IntegerField()
    expires_at = serializers.IntegerField(required=False)
    token_type = serializers.CharField()
    user = AuthUserSerializer()


class AuthResponseSerializer(serializers.Serializer):
    user = AuthUserSerializer()
    expires_in = serializers.IntegerField(required=False)
    expires_at = serializers.IntegerField(required=False)
    token_type = serializers.CharField(required=False)
    session_created = serializers.BooleanField(default=False)
