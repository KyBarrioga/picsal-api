"""Infrastructure service helpers."""
from __future__ import annotations
from django.db import connection

from core.authentication import SupabaseUser

class UploadMediaServices:
    """Media services when media is uploaded."""

    @staticmethod
    def insert_media_record(
        user_id: str,
        object_key: str,
        public_url: str,
        kind: str,
        preview_object_key: str,
        preview_public_url: str,
        title: str | None = None,
        description: str | None = None,
    ) -> dict | None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.media (
                    user_id,
                    object_key,
                    public_url,
                    kind,
                    title,
                    description,
                    preview_object_key,
                    preview_public_url
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s)
                returning *;
                """,
                [
                    str(user_id),
                    object_key,
                    public_url,
                    kind,
                    title,
                    description,
                    preview_object_key,
                    preview_public_url,
                ],
            )

            row = cursor.fetchone()
            if not row:
                return None

            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
