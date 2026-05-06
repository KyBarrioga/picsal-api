import uuid
from datetime import datetime, timezone

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from core.authentication import SupabaseUser
from user.views import ManageUserView, UserSetupView


class SetupProfileServiceStub:
    def __init__(self):
        self.calls = []

    def update_profile(self, user, data):
        self.calls.append((str(user.id), data))
        return {
            "id": user.id,
            "email": user.email,
            "username": data["username"],
            "created_at": datetime(2026, 5, 5, tzinfo=timezone.utc),
        }


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
                "id": str(request_user.id), "username": "person"},
             "get_media_for_user": lambda self, request_user: [
                {"id": "media-1", "user_id": str(request_user.id)}
            ]},
        )()

        response = view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["auth_user"]
                         ["email"], "person@example.com")
        self.assertEqual(response.data["profile"]["username"], "person")
        self.assertEqual(len(response.data["media"]), 1)

    def test_setup_updates_profile_username(self):
        user = SupabaseUser(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            email="person@example.com",
            role="user",
        )
        request = APIRequestFactory().patch(
            "/api/user/setup/",
            {"username": "Kymbiee"},
            format="json",
        )
        force_authenticate(request, user=user)

        original_profile_service = UserSetupView.profile_service
        profile_service_stub = SetupProfileServiceStub()
        UserSetupView.profile_service = profile_service_stub

        try:
            response = UserSetupView.as_view()(request)
        finally:
            UserSetupView.profile_service = original_profile_service

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            profile_service_stub.calls,
            [
                (
                    "11111111-1111-1111-1111-111111111111",
                    {"username": "Kymbiee"},
                )
            ],
        )
        self.assertEqual(response.data["profile"]["username"], "Kymbiee")
        self.assertEqual(response.data["profile"]["id"], user.id)
