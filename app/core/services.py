"""Infrastructure service helpers."""
from __future__ import annotations

from functools import lru_cache
from urllib.parse import quote

import boto3
from django.conf import settings
from django.db import connection

from core.authentication import SupabaseUser


class R2StorageService:
    """Generate signed Cloudflare R2 upload URLs."""

    def __init__(self) -> None:
        self.bucket = settings.CLOUDFLARE_R2_BUCKET
        self.endpoint_url = (
            "https://"
            f"{settings.CLOUDFLARE_R2_ACCOUNT_ID}"
            ".r2.cloudflarestorage.com"
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
            raise ValueError(
                "Cloudflare R2 credentials are not fully configured.")

        return boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            region_name="auto",
        )

    def generate_upload_url(
        self, object_key: str, content_type: str, expires_in: int = 900
    ) -> str:
        """Generate a presigned PUT URL for browser uploads."""
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
            return (
                f"{settings.CLOUDFLARE_R2_PUBLIC_BASE_URL
                    .rstrip('/')}/{quote(object_key)}"
            )
        return f"{self.endpoint_url}/{self.bucket}/{quote(object_key)}"


class SupabaseProfileService:
    """Thin data-access layer for the existing Supabase profiles table."""

    def __init__(self) -> None:
        self.schema = settings.PROFILE_SCHEMA_NAME
        self.table = settings.PROFILE_TABLE_NAME

    @property
    def qualified_table(self) -> str:
        return f'"{self.schema}"."{self.table}"'

    @staticmethod
    def _fetchone_as_dict(cursor) -> dict | None:
        """Convert the current cursor row to a dictionary."""
        row = cursor.fetchone()
        if not row:
            return None
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))

    @lru_cache(maxsize=1)
    def get_columns(self) -> set[str]:
        """Load available profile columns from the connected database."""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select column_name
                from information_schema.columns
                where table_schema = %s and table_name = %s
                """,
                [self.schema, self.table],
            )
            return {row[0] for row in cursor.fetchall()}

    def get_profile(self, user: SupabaseUser) -> dict | None:
        """Return the matching profile row from Supabase."""
        with connection.cursor() as cursor:
            cursor.execute(
                f"select * from {self.qualified_table} where id = %s limit 1",
                [str(user.id)],
            )
            return self._fetchone_as_dict(cursor)

    def update_profile(self, user: SupabaseUser, data: dict) -> dict | None:
        """Update editable profile fields and return the updated row."""
        allowed_columns = (
            self.get_columns()
            - settings.PROFILE_PROTECTED_COLUMNS
        )
        updates = {key: value for key,
                   value in data.items() if key in allowed_columns}
        if not updates:
            return self.get_profile(user)

        assignments = ", ".join(f'"{column}" = %s' for column in updates)
        values = list(updates.values()) + [str(user.id)]

        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                update {self.qualified_table}
                set {assignments}
                where id = %s
                returning *
                """,
                values,
            )
            return self._fetchone_as_dict(cursor)

    def get_media_for_user(self, user: SupabaseUser) -> list[dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select *
                from public.media
                where user_id = %s
                order by created_at desc
                """,
                [str(user.id)],
            )
            rows = cursor.fetchall()
            if not rows:
                return []

            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
