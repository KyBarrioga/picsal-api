import uuid

from django.test import TestCase

from core.models import UserProfile


class UserProfileModelTests(TestCase):
    def test_build_r2_key_keeps_extension(self):
        key = UserProfile.build_r2_key(uuid.uuid4(), "avatar.png")

        self.assertTrue(key.startswith("users/"))
        self.assertTrue(key.endswith(".png"))

    def test_normalize_role_defaults_to_user(self):
        self.assertEqual(UserProfile.normalize_role("unknown"), UserProfile.ROLE_USER)
        self.assertEqual(UserProfile.normalize_role(UserProfile.ROLE_ADMIN), UserProfile.ROLE_ADMIN)

