from django.conf import settings
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from core.authentication import SupabaseJWTAuthentication


class CookieSupabaseJWTAuthentication(SupabaseJWTAuthentication):
    def decode_token(self, token: str) -> dict:
        self.token = token
        return {
            "sub": "11111111-1111-1111-1111-111111111111",
            "email": "person@example.com",
            "user_metadata": {"display_name": "Person"},
        }


class SupabaseJWTAuthenticationTests(SimpleTestCase):
    def test_authenticates_from_access_token_cookie(self):
        request = APIRequestFactory().get("/api/user/me/")
        request.COOKIES[settings.AUTH_ACCESS_COOKIE_NAME] = "cookie-token"

        authenticator = CookieSupabaseJWTAuthentication()
        user, claims = authenticator.authenticate(request)

        self.assertEqual(authenticator.token, "cookie-token")
        self.assertEqual(user.email, "person@example.com")
        self.assertEqual(user.display_name, "Person")
        self.assertEqual(claims["sub"], str(user.id))
