from django.conf import settings
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from authn.views import (
    LoginView,
    LogoutView,
    RefreshView,
    SetupUserView,
    SignupView,
)
from core.authentication import SupabaseUser


class LoginServiceStub:
    def login(self, email, password):
        return session_payload(email)


class SignupWithSessionServiceStub:
    def signup(self, email, password, **kwargs):
        return session_payload(email)


class SignupWithoutSessionServiceStub:
    def signup(self, email, password, **kwargs):
        return {
            "user": session_payload(email)["user"],
        }


class SignupBareUserServiceStub:
    def signup(self, email, password, **kwargs):
        return session_payload(email)["user"]


class LogoutServiceStub:
    def __init__(self):
        self.logged_out_tokens = []

    def logout(self, access_token):
        self.logged_out_tokens.append(access_token)


class RefreshServiceStub:
    def __init__(self):
        self.refresh_tokens = []

    def refresh(self, refresh_token):
        self.refresh_tokens.append(refresh_token)
        payload = session_payload()
        payload["access_token"] = "new-access-token"
        payload["refresh_token"] = "new-refresh-token"
        return payload


class SetupUserServiceStub:
    def __init__(self):
        self.calls = []

    def update_user_metadata(self, access_token, data):
        self.calls.append((access_token, data))
        return {
            "id": "11111111-1111-1111-1111-111111111111",
            "email": "user@example.com",
            "role": "authenticated",
            "aud": "authenticated",
            "user_metadata": data,
        }


def session_payload(email="user@example.com"):
    return {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "expires_in": 3600,
        "expires_at": 1735689600,
        "token_type": "bearer",
        "user": {
            "id": "11111111-1111-1111-1111-111111111111",
            "email": email,
            "role": "authenticated",
            "aud": "authenticated",
        },
    }


class AuthViewTests(SimpleTestCase):
    def test_login_sets_auth_cookies_without_returning_tokens(self):
        request = APIRequestFactory().post(
            "/api/auth/login/",
            {"email": "user@example.com", "password": "secret123"},
            format="json",
        )

        original_service = LoginView.service
        LoginView.service = LoginServiceStub()

        try:
            response = LoginView.as_view()(request)
        finally:
            LoginView.service = original_service

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["email"], "user@example.com")
        self.assertTrue(response.data["session_created"])
        self.assertNotIn("access_token", response.data)
        self.assertNotIn("refresh_token", response.data)
        self.assertEqual(
            response.cookies[settings.AUTH_ACCESS_COOKIE_NAME].value,
            "access-token",
        )
        self.assertEqual(
            response.cookies[settings.AUTH_REFRESH_COOKIE_NAME].value,
            "refresh-token",
        )
        self.assertTrue(
            response.cookies[settings.AUTH_ACCESS_COOKIE_NAME]["httponly"])

    def test_signup_sets_cookies_when_supabase_returns_a_session(self):
        request = APIRequestFactory().post(
            "/api/auth/signup/",
            {
                "email": "new@example.com",
                "password": "secret123",
                "email_redirect_to": "http://localhost:3000/auth/confirm",
            },
            format="json",
        )

        original_service = SignupView.service
        SignupView.service = SignupWithSessionServiceStub()

        try:
            response = SignupView.as_view()(request)
        finally:
            SignupView.service = original_service

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["email"], "new@example.com")
        self.assertTrue(response.data["session_created"])
        self.assertIn(settings.AUTH_ACCESS_COOKIE_NAME, response.cookies)

    def test_signup_without_session_returns_user_without_cookies(self):
        request = APIRequestFactory().post(
            "/api/auth/signup/",
            {"email": "new@example.com", "password": "secret123"},
            format="json",
        )

        original_service = SignupView.service
        SignupView.service = SignupWithoutSessionServiceStub()

        try:
            response = SignupView.as_view()(request)
        finally:
            SignupView.service = original_service

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["email"], "new@example.com")
        self.assertFalse(response.data["session_created"])
        self.assertNotIn(settings.AUTH_ACCESS_COOKIE_NAME, response.cookies)

    def test_signup_accepts_bare_supabase_user_response(self):
        request = APIRequestFactory().post(
            "/api/auth/signup/",
            {"email": "new@example.com", "password": "secret123"},
            format="json",
        )

        original_service = SignupView.service
        SignupView.service = SignupBareUserServiceStub()

        try:
            response = SignupView.as_view()(request)
        finally:
            SignupView.service = original_service

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["email"], "new@example.com")
        self.assertFalse(response.data["session_created"])
        self.assertNotIn(settings.AUTH_ACCESS_COOKIE_NAME, response.cookies)

    def test_logout_calls_supabase_and_clears_auth_cookies(self):
        request = APIRequestFactory().post("/api/auth/logout/", format="json")
        request.COOKIES[settings.AUTH_ACCESS_COOKIE_NAME] = "access-token"

        original_service = LogoutView.service
        service_stub = LogoutServiceStub()
        LogoutView.service = service_stub

        try:
            response = LogoutView.as_view()(request)
        finally:
            LogoutView.service = original_service

        self.assertEqual(response.status_code, 204)
        self.assertEqual(service_stub.logged_out_tokens, ["access-token"])
        self.assertEqual(
            response.cookies[settings.AUTH_ACCESS_COOKIE_NAME].value,
            "",
        )
        self.assertEqual(
            response.cookies[settings.AUTH_REFRESH_COOKIE_NAME].value,
            "",
        )

    def test_refresh_uses_refresh_cookie_and_resets_auth_cookies(self):
        request = APIRequestFactory().post("/api/auth/refresh/",
                                           format="json")
        request.COOKIES[settings.AUTH_REFRESH_COOKIE_NAME] = "refresh-token"

        original_service = RefreshView.service
        service_stub = RefreshServiceStub()
        RefreshView.service = service_stub

        try:
            response = RefreshView.as_view()(request)
        finally:
            RefreshView.service = original_service

        self.assertEqual(response.status_code, 200)
        self.assertEqual(service_stub.refresh_tokens, ["refresh-token"])
        self.assertTrue(response.data["session_created"])
        self.assertNotIn("access_token", response.data)
        self.assertEqual(
            response.cookies[settings.AUTH_ACCESS_COOKIE_NAME].value,
            "new-access-token",
        )
        self.assertEqual(
            response.cookies[settings.AUTH_REFRESH_COOKIE_NAME].value,
            "new-refresh-token",
        )

    def test_refresh_rejects_missing_refresh_cookie(self):
        request = APIRequestFactory().post("/api/auth/refresh/",
                                           format="json")

        response = RefreshView.as_view()(request)

        self.assertEqual(response.status_code, 403)

    def test_setup_updates_supabase_display_name(self):
        request = APIRequestFactory().patch(
            "/api/auth/setup/",
            {"display_name": "Kymbiee"},
            format="json",
            HTTP_AUTHORIZATION="Bearer access-token",
        )
        force_authenticate(
            request,
            user=SupabaseUser(
                id="11111111-1111-1111-1111-111111111111",
                email="user@example.com",
            ),
        )

        original_service = SetupUserView.service
        service_stub = SetupUserServiceStub()
        SetupUserView.service = service_stub

        try:
            response = SetupUserView.as_view()(request)
        finally:
            SetupUserView.service = original_service

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            service_stub.calls,
            [("access-token", {"display_name": "Kymbiee"})],
        )
        self.assertEqual(response.data["user"]["display_name"], "Kymbiee")
