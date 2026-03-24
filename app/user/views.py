"""User API views."""
from rest_framework import generics, permissions

from core.models import UserProfile
from user.serializers import UserProfileSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated Supabase user's profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> UserProfile:
        return self.request.user

