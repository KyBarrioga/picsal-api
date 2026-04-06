"""Authentication classes for Supabase JWTs."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from functools import lru_cache

import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from urllib.parse import urljoin


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
    if role in {"admin", "superuser"}:
        return role
    return "user"


@dataclass
class SupabaseUser:
    """Authenticated user object built directly from Supabase JWT claims."""

    id: uuid.UUID
    email: str
    role: str = "user"
    display_name: str = ""
    claims: dict = field(default_factory=dict)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    """Authenticate requests with Supabase-issued bearer tokens."""

    keyword = "Bearer"

    def authenticate(self, request):
        header = (
            authentication.get_authorization_header(request)
            .decode("utf-8")
        )
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
        try:
            return self._decode_with_jwks_or_secret(token)
        except jwt.InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed(
                f"Invalid Supabase access token: {exc}") from exc

    def _decode_with_jwks_or_secret(self, token: str) -> dict:
        """Decode a Supabase JWT with JWKS first, then fallback."""
        headers = jwt.get_unverified_header(token)
        algorithm = headers.get("alg", settings.SUPABASE_JWT_ALGORITHM)
        options = {"verify_aud": bool(settings.SUPABASE_JWT_AUDIENCE)}
        issuer = self.get_expected_issuer()

        if settings.SUPABASE_JWKS_URL:
            signing_key = self.get_signing_key(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=[algorithm],
                audience=settings.SUPABASE_JWT_AUDIENCE or None,
                issuer=issuer,
                options=options,
            )

        if settings.SUPABASE_JWT_SECRET:
            return jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=[settings.SUPABASE_JWT_ALGORITHM],
                audience=settings.SUPABASE_JWT_AUDIENCE or None,
                issuer=issuer,
                options=options,
            )

        raise exceptions.AuthenticationFailed(
            "Neither SUPABASE_JWKS_URL nor SUPABASE_JWT_SECRET is configured."
        )

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_jwks_client():
        """Cache the JWKS client to avoid fetching keys on every request."""
        return jwt.PyJWKClient(settings.SUPABASE_JWKS_URL)

    @staticmethod
    def get_expected_issuer() -> str | None:
        """Return the expected issuer for Supabase tokens."""
        if settings.SUPABASE_JWT_ISSUER:
            return settings.SUPABASE_JWT_ISSUER.rstrip("/")
        if settings.SUPABASE_URL:
            return urljoin(
                f"{settings.SUPABASE_URL.rstrip('/')}/", "auth/v1"
            ).rstrip("/")
        return None

    def get_signing_key(self, token: str):
        """Resolve the signing key for a JWT from Supabase JWKS."""
        return self._get_jwks_client().get_signing_key_from_jwt(token)

    def sync_profile(self, claims: dict) -> SupabaseUser:
        """Build the authenticated request user from token claims."""
        user_id = claims.get("sub")
        email = claims.get("email")
        if not user_id or not email:
            raise exceptions.AuthenticationFailed(
                "Supabase token missing user identity claims.")

        try:
            profile_id = uuid.UUID(user_id)
        except ValueError as exc:
            raise exceptions.AuthenticationFailed(
                "Supabase token contains an invalid user id.") from exc

        return SupabaseUser(
            id=profile_id,
            email=email,
            role=extract_role(claims),
            display_name=extract_display_name(claims),
            claims=claims,
        )
