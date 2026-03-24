"""Authentication classes for Supabase JWTs."""
from __future__ import annotations

import uuid

import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions

from core.models import UserProfile


def extract_display_name(claims: dict) -> str:
    """Pick the best available display name from Supabase claims."""
    user_metadata = claims.get("user_metadata") or {}
    return (
        user_metadata.get("display_name")
        or user_metadata.get("full_name")
        or user_metadata.get("name")
        or user_metadata.get("username")
        or ""
    )


def extract_role(claims: dict) -> str:
    """Resolve the Picsal role from JWT claims."""
    app_metadata = claims.get("app_metadata") or {}
    role = app_metadata.get("picsal_role") or app_metadata.get("role")
    return UserProfile.normalize_role(role)


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    """Authenticate requests with Supabase-issued bearer tokens."""

    keyword = "Bearer"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1]
        claims = self.decode_token(token)
        user = self.sync_profile(claims)
        return (user, claims)

    def decode_token(self, token: str) -> dict:
        """Decode a Supabase JWT."""
        if not settings.SUPABASE_JWT_SECRET:
            raise exceptions.AuthenticationFailed("SUPABASE_JWT_SECRET is not configured.")

        options = {"verify_aud": bool(settings.SUPABASE_JWT_AUDIENCE)}

        try:
            return jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=[settings.SUPABASE_JWT_ALGORITHM],
                audience=settings.SUPABASE_JWT_AUDIENCE or None,
                options=options,
            )
        except jwt.InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed("Invalid Supabase access token.") from exc

    def sync_profile(self, claims: dict) -> UserProfile:
        """Create or update the local profile row from token claims."""
        user_id = claims.get("sub")
        email = claims.get("email")
        if not user_id or not email:
            raise exceptions.AuthenticationFailed("Supabase token missing user identity claims.")

        try:
            profile_id = uuid.UUID(user_id)
        except ValueError as exc:
            raise exceptions.AuthenticationFailed("Supabase token contains an invalid user id.") from exc

        profile, created = UserProfile.objects.get_or_create(
            id=profile_id,
            defaults={
                "email": email,
                "display_name": extract_display_name(claims),
                "role": extract_role(claims),
                "metadata": claims.get("user_metadata") or {},
            },
        )

        updates = []
        display_name = extract_display_name(claims)
        role = extract_role(claims)
        metadata = claims.get("user_metadata") or {}

        if profile.email != email:
            profile.email = email
            updates.append("email")
        if display_name and profile.display_name != display_name:
            profile.display_name = display_name
            updates.append("display_name")
        if profile.role != role:
            profile.role = role
            updates.append("role")
        if metadata and profile.metadata != metadata:
            profile.metadata = metadata
            updates.append("metadata")

        profile.last_login_at = timezone.now()
        updates.append("last_login_at")

        if created:
            profile.save()
        else:
            profile.save(update_fields=updates)

        return profile
