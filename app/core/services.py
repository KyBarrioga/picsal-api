"""Infrastructure service helpers."""
from __future__ import annotations

from urllib.parse import quote

import boto3
from django.conf import settings


class R2StorageService:
    """Generate signed Cloudflare R2 upload URLs."""

    def __init__(self) -> None:
        self.bucket = settings.CLOUDFLARE_R2_BUCKET
        self.endpoint_url = (
            f"https://{settings.CLOUDFLARE_R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
            if settings.CLOUDFLARE_R2_ACCOUNT_ID
            else ""
        )

    def client(self):
        """Return an S3-compatible client for Cloudflare R2."""
        if not all(
            [
                self.bucket,
                self.endpoint_url,
                settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
                settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            ]
        ):
            raise ValueError("Cloudflare R2 credentials are not fully configured.")

        return boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            region_name="auto",
        )

    def generate_upload_url(self, object_key: str, content_type: str, expires_in: int = 900) -> str:
        """Generate a presigned PUT URL for direct browser uploads."""
        client = self.client()
        return client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

    def build_public_url(self, object_key: str) -> str:
        """Build a public-facing URL for a stored object."""
        if settings.CLOUDFLARE_R2_PUBLIC_BASE_URL:
            return f"{settings.CLOUDFLARE_R2_PUBLIC_BASE_URL.rstrip('/')}/{quote(object_key)}"
        return f"{self.endpoint_url}/{self.bucket}/{quote(object_key)}"

