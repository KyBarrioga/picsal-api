import uuid

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from core.authentication import SupabaseUser
from user.views import ManageUserView


class ManageUserViewTests(SimpleTestCase):
    def test_get_returns_auth_user_payload(self):
        user = SupabaseUser(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            email="person@example.com",
            role="user",
            display_name="Person",
        )
        request = APIRequestFactory().get("/api/user/me/")
        request.user = user

        view = ManageUserView()
        view.profile_service = type(
            "ProfileServiceStub",
            (),
            {"get_profile": lambda self, request_user: {
                "id": str(request_user.id), "username": "person"}},
        )()

        response = view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["auth_user"]
                         ["email"], "person@example.com")
        self.assertEqual(response.data["profile"]["username"], "person")
