"""Supabase Auth service integration."""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
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
            raise exceptions.ValidationError(
                {"detail": "SUPABASE_URL is not configured."})
        if not self.anon_key:
            raise exceptions.ValidationError(
                {"detail": "SUPABASE_ANON_KEY is not configured."})

    def _request(
        self,
        path: str,
        *,
        method: str = "POST",
        payload: dict | None = None,
        bearer_token: str | None = None,
    ) -> dict:
        """Send a request to Supabase Auth and normalize errors."""
        self._validate_settings()
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "apikey": self.anon_key,
        }
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        request = Request(
            url=f"{self.base_url}/auth/v1/{path.lstrip('/')}",
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=15) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except HTTPError as exc:
            try:
                error_body = json.loads(exc.read().decode("utf-8"))
            except json.JSONDecodeError:
                error_body = {}
            message = (
                error_body.get("msg")
                or error_body.get("error_description")
                or error_body.get("error")
                or "Supabase Auth request failed."
            )
            raise exceptions.AuthenticationFailed(message) from exc
        except URLError as exc:
            raise exceptions.APIException(
                "Unable to reach Supabase Auth.") from exc

    def login(self, email: str, password: str) -> dict:
        """Exchange credentials for a Supabase session."""
        return self._request(
            "token?grant_type=password",
            payload={
                "email": email,
                "password": password,
            },
        )

    def signup(
        self,
        email: str,
        password: str,
        *,
        email_redirect_to: str | None = None,
        data: dict | None = None,
    ) -> dict:
        """Create a Supabase Auth user."""
        query = ""
        if email_redirect_to:
            query = f"?{urlencode({'redirect_to': email_redirect_to})}"

        payload = {
            "email": email,
            "password": password,
        }
        if data:
            payload["data"] = data

        return self._request(f"signup{query}", payload=payload)

    def logout(self, access_token: str) -> dict:
        """Invalidate the current Supabase session."""
        return self._request(
            "logout",
            method="POST",
            bearer_token=access_token,
        )

    def refresh(self, refresh_token: str) -> dict:
        """Exchange a Supabase refresh token for a new session."""
        return self._request(
            "token?grant_type=refresh_token",
            payload={
                "refresh_token": refresh_token,
            },
        )
