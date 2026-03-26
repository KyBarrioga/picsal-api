from uuid import uuid4

from django.test import SimpleTestCase

from core.serializers import build_r2_key


class R2KeyTests(SimpleTestCase):
    def test_build_r2_key_keeps_extension(self):
        key = build_r2_key(uuid4(), "avatar.png")

        self.assertTrue(key.startswith("users/"))
        self.assertTrue(key.endswith(".png"))
