"""Core data models."""
import uuid

from django.db import models


class UserProfile(models.Model):
    """Profile row mirrored from Supabase Auth users."""

    ROLE_USER = "user"
    ROLE_ADMIN = "admin"
    ROLE_SUPERUSER = "superuser"
    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_SUPERUSER, "Superuser"),
    ]

    id = models.UUIDField(primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=255, blank=True, default="")
    avatar_path = models.CharField(max_length=512, blank=True, default="")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)
    metadata = models.JSONField(default=dict, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_admin(self) -> bool:
        return self.role in {self.ROLE_ADMIN, self.ROLE_SUPERUSER}

    @property
    def is_superuser_role(self) -> bool:
        return self.role == self.ROLE_SUPERUSER

    @classmethod
    def normalize_role(cls, value: str | None) -> str:
        """Normalize role values coming from JWT metadata."""
        if value in {cls.ROLE_ADMIN, cls.ROLE_SUPERUSER}:
            return value
        return cls.ROLE_USER

    @classmethod
    def build_r2_key(cls, user_id: uuid.UUID, filename: str, folder: str = "users") -> str:
        """Build a namespaced R2 object key for a user-owned file."""
        extension = ""
        if "." in filename:
            extension = f".{filename.rsplit('.', 1)[-1].lower()}"
        return f"{folder}/{user_id}/{uuid.uuid4()}{extension}"
