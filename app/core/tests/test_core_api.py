import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from core.authentication import SupabaseUser
from core.views import StoragePresignView


class StoragePresignViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.original_storage_service_class = (
            StoragePresignView.storage_service_class
        )
        self.user = SupabaseUser(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            email="person@example.com",
            role="user",
            display_name="Person",
        )

    def tearDown(self):
        StoragePresignView.storage_service_class = (
            self.original_storage_service_class
        )

    def test_post_accepts_multipart_image_payload(self):
        image = SimpleUploadedFile(
            "avatar.png", b"fake-image-bytes", content_type="image/png")
        request = self.factory.post(
            "/api/core/storage/presign/",
            {
                "image": image,
            },
            format="multipart",
        )
        force_authenticate(request, user=self.user)

        captured = {}

        class StorageServiceStub:
            def generate_upload_url(self, object_key, content_type):
                captured["object_key"] = object_key
                captured["content_type"] = content_type
                return f"https://upload.example.com/{object_key}"

            def build_public_url(self, object_key):
                return f"https://cdn.example.com/{object_key}"

        view = StoragePresignView.as_view()
        StoragePresignView.storage_service_class = StorageServiceStub

        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertIn("/users/", response.data["public_url"])
        self.assertTrue(captured["object_key"].endswith(".png"))
        self.assertEqual(captured["content_type"], "image/png")

    def test_post_rejects_non_image_upload(self):
        document = SimpleUploadedFile(
            "notes.txt", b"hello", content_type="text/plain")
        request = self.factory.post(
            "/api/core/storage/presign/",
            {
                "image": document,
            },
            format="multipart",
        )
        force_authenticate(request, user=self.user)

        view = StoragePresignView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("image", response.data)
