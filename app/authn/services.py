"""Supabase Auth service integration."""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from rest_framework import exceptions


class SupabaseAuthService:
    """Thin wrapper around Supabase Auth HTTP endpoints."""

    def __init__(self) -> None:
        self.base_url = settings.SUPABASE_URL.rstrip("/")
        self.anon_key = settings.SUPABASE_ANON_KEY

    def _validate_settings(self) -> None:
        if not self.base_url:
            raise exceptions.ValidationError({"detail": "SUPABASE_URL is not configured."})
        if not self.anon_key:
            raise exceptions.ValidationError({"detail": "SUPABASE_ANON_KEY is not configured."})

    def login(self, email: str, password: str) -> dict:
        """Exchange credentials for a Supabase session."""
        self._validate_settings()
        payload = json.dumps(
            {
                "email": email,
                "password": password,
            }
        ).encode("utf-8")
        request = Request(
            url=f"{self.base_url}/auth/v1/token?grant_type=password",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "apikey": self.anon_key,
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                error_body = json.loads(exc.read().decode("utf-8"))
            except json.JSONDecodeError:
                error_body = {}
            message = (
                error_body.get("msg")
                or error_body.get("error_description")
                or error_body.get("error")
                or "Unable to log in with Supabase."
            )
            raise exceptions.AuthenticationFailed(message) from exc
        except URLError as exc:
            raise exceptions.APIException("Unable to reach Supabase Auth.") from exc

