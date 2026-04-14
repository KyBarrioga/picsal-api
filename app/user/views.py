"""User API views."""
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import SupabaseUser
from core.services import SupabaseProfileService
from user.serializers import (
    SupabaseAuthUserSerializer,
    SupabaseProfileEnvelopeSerializer,
    SupabaseProfileUpdateSerializer,
)


class ManageUserView(APIView):
    """Retrieve or update the authenticated Supabase user."""

    permission_classes = [permissions.IsAuthenticated]
    profile_service = SupabaseProfileService()

    def get(self, request):
        user: SupabaseUser = request.user
        payload = {
            "auth_user": SupabaseAuthUserSerializer(user).data,
            "profile": self.profile_service.get_profile(user),
            "media": self.profile_service.get_media_for_user(user),
        }
        return Response(SupabaseProfileEnvelopeSerializer(payload).data)

    def patch(self, request):
        user: SupabaseUser = request.user
        serializer = SupabaseProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = self.profile_service.update_profile(
            user=user,
            data=serializer.validated_data.get("profile", {}),
        )
        payload = {
            "auth_user": SupabaseAuthUserSerializer(user).data,
            "profile": profile,
            "media": self.profile_service.get_media_for_user(user),
        }
        return Response(
            SupabaseProfileEnvelopeSerializer(payload).data,
            status=status.HTTP_200_OK
        )
