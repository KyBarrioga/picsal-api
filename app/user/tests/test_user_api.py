from django.test import TestCase
from rest_framework.test import APIRequestFactory

from core.models import UserProfile
from user.views import ManageUserView


class ManageUserViewTests(TestCase):
    def test_get_returns_current_user_profile(self):
        user = UserProfile.objects.create(
            id="11111111-1111-1111-1111-111111111111",
            email="person@example.com",
            display_name="Person",
        )

        request = APIRequestFactory().get("/api/user/me/")
        request.user = user

        response = ManageUserView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "person@example.com")

