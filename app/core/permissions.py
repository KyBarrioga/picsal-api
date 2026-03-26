"""Custom API permissions."""
from rest_framework import permissions


class IsAdminOrSuperuser(permissions.BasePermission):
    """Allow access only to admin and superuser profiles."""

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and getattr(user, "is_authenticated", False)
            and getattr(user, "role", None) in {"admin", "superuser"}
        )
