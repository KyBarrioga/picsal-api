from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from authn.views import LoginView


class LoginViewTests(SimpleTestCase):
    def test_login_returns_supabase_session_payload(self):
        request = APIRequestFactory().post(
            "/api/auth/login/",
            {"email": "user@example.com", "password": "secret123"},
            format="json",
        )

        view = LoginView()
        view.service = type(
            "AuthServiceStub",
            (),
            {
                "login": lambda self, email, password: {
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
            },
        )()

        response = view.post(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["email"], "user@example.com")
