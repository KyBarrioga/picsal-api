"""Authentication API views."""
from django.conf import settings
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import exceptions, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from authn.serializers import (
    AuthResponseSerializer,
    LoginRequestSerializer,
    SignupRequestSerializer,
)
from authn.services import SupabaseAuthService


def _cookie_options() -> dict:
    """Return shared auth cookie options."""
    return {
        "httponly": True,
        "secure": settings.AUTH_COOKIE_SECURE,
        "samesite": settings.AUTH_COOKIE_SAMESITE,
        "domain": settings.AUTH_COOKIE_DOMAIN or None,
        "path": settings.AUTH_COOKIE_PATH,
    }


def _session_from_payload(payload: dict) -> dict:
    """Normalize Supabase Auth responses into one session-shaped dict."""
    session = payload.get("session") or payload
    user = payload.get("user") or session.get("user")
    if user:
        session["user"] = user
    return session


def _auth_response_data(payload: dict) -> dict:
    """Build a client-safe auth response without exposing JWTs."""
    session = _session_from_payload(payload)
    response_data = {
        "user": session.get("user"),
        "session_created": bool(session.get("access_token")),
    }
    for key in ("expires_in", "expires_at", "token_type"):
        value = session.get(key)
        if value is not None:
            response_data[key] = value
    return response_data


def _set_auth_cookies(response: Response, payload: dict) -> None:
    """Persist Supabase JWTs as http-only cookies."""
    session = _session_from_payload(payload)
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")
    if not access_token or not refresh_token:
        return

    access_max_age = session.get("expires_in")
    response.set_cookie(
        settings.AUTH_ACCESS_COOKIE_NAME,
        access_token,
        max_age=access_max_age,
        **_cookie_options(),
    )
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        refresh_token,
        max_age=settings.AUTH_REFRESH_COOKIE_AGE,
        **_cookie_options(),
    )


def _delete_auth_cookies(response: Response) -> None:
    """Remove auth cookies from the browser."""
    cookie_options = _cookie_options()
    delete_options = {
        "path": cookie_options["path"],
        "domain": cookie_options["domain"],
        "samesite": cookie_options["samesite"],
    }
    response.delete_cookie(
        settings.AUTH_ACCESS_COOKIE_NAME,
        **delete_options,
    )
    response.delete_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        **delete_options,
    )


def _access_token_from_request(request) -> str:
    authorization = request.headers.get("Authorization", "")
    prefix = "Bearer "
    if authorization.startswith(prefix):
        return authorization[len(prefix):].strip()
    return request.COOKIES.get(settings.AUTH_ACCESS_COOKIE_NAME, "")


def _refresh_token_from_request(request) -> str:
    return request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME, "")


class LoginView(APIView):
    """Log a user in through Supabase Auth."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    service = SupabaseAuthService()

    @extend_schema(
        operation_id="auth_login",
        tags=["auth"],
        request=LoginRequestSerializer,
        responses={200: AuthResponseSerializer},
        examples=[
            OpenApiExample(
                "Password login",
                value={"email": "user@example.com", "password": "secret123"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = self.service.login(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        response_serializer = AuthResponseSerializer(
            data=_auth_response_data(session),
        )
        response_serializer.is_valid(raise_exception=True)
        response = Response(
            response_serializer.validated_data,
            status=status.HTTP_200_OK,
        )
        _set_auth_cookies(response, session)
        return response


class SignupView(APIView):
    """Create a user through Supabase Auth."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    service = SupabaseAuthService()

    @extend_schema(
        operation_id="auth_signup",
        tags=["auth"],
        request=SignupRequestSerializer,
        responses={201: AuthResponseSerializer},
        examples=[
            OpenApiExample(
                "Email signup",
                value={
                    "email": "user@example.com",
                    "password": "secret123",
                    "email_redirect_to": "http://localhost:3000/auth/confirm",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = self.service.signup(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            email_redirect_to=serializer.validated_data.get(
                "email_redirect_to",
            ),
            data=serializer.validated_data.get("data"),
        )
        response_serializer = AuthResponseSerializer(
            data=_auth_response_data(session),
        )
        response_serializer.is_valid(raise_exception=True)
        response = Response(
            response_serializer.validated_data,
            status=status.HTTP_201_CREATED,
        )
        _set_auth_cookies(response, session)
        return response


class LogoutView(APIView):
    """Log out and clear Supabase auth cookies."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    service = SupabaseAuthService()

    @extend_schema(
        operation_id="auth_logout",
        tags=["auth"],
        responses={204: None},
    )
    def post(self, request):
        access_token = _access_token_from_request(request)
        if access_token:
            try:
                self.service.logout(access_token)
            except exceptions.APIException:
                pass

        response = Response(status=status.HTTP_204_NO_CONTENT)
        _delete_auth_cookies(response)
        return response


class RefreshView(APIView):
    """Refresh the Supabase access token from the refresh cookie."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    service = SupabaseAuthService()

    @extend_schema(
        operation_id="auth_refresh",
        tags=["auth"],
        responses={200: AuthResponseSerializer},
    )
    def post(self, request):
        refresh_token = _refresh_token_from_request(request)
        if not refresh_token:
            raise exceptions.AuthenticationFailed(
                "Missing refresh token cookie.")

        session = self.service.refresh(refresh_token)
        response_serializer = AuthResponseSerializer(
            data=_auth_response_data(session),
        )
        response_serializer.is_valid(raise_exception=True)
        response = Response(
            response_serializer.validated_data,
            status=status.HTTP_200_OK,
        )
        _set_auth_cookies(response, session)
        return response
