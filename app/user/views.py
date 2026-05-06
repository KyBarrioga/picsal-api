"""User API views."""
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import IntegrityError, DataError

from core.authentication import SupabaseUser
from core.services import SupabaseProfileService
from user.serializers import (
    SupabaseAuthUserSerializer,
    SupabaseProfileEnvelopeSerializer,
    SupabaseProfileUpdateSerializer,
    UserSetupRequestSerializer,
    UserSetupResponseSerializer,
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

class UserSetupView(APIView):
    """Finalize profile setup for the authenticated Supabase user."""

    permission_classes = [permissions.IsAuthenticated]
    profile_service = SupabaseProfileService()

    @extend_schema(
        request=UserSetupRequestSerializer,
        responses={200: UserSetupResponseSerializer},
    )
    def patch(self, request):
        user: SupabaseUser = request.user
        serializer = UserSetupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            profile = self.profile_service.update_profile(
                user=user,
                data={"username": serializer.validated_data["username"]},
            )
            if profile is None:
                return Response(
                    {"detail": "Profile not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            response_serializer = UserSetupResponseSerializer(
                {"profile": profile},
            )
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )
        except IntegrityError as exc:
            constraint_name = getattr(
                getattr(exc.__cause__, "diag", None),
                "constraint_name",
                "",
            )

            if constraint_name == "profiles_username_check":
                return Response(
                    {
                        "username": [
                            "Display name must be lowercase, 1-30 characters, and may only contain _ or - after the first character."
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if constraint_name == "profiles_username_key":
                return Response(
                    {"username": ["This username is already taken."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"detail": "Profile update violates a database constraint."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DataError:
            return Response(
                {"detail": "Invalid profile data."},
                status=status.HTTP_400_BAD_REQUEST,
            )