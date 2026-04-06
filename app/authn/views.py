"""Authentication API views."""
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from authn.serializers import LoginRequestSerializer, SessionSerializer
from authn.services import SupabaseAuthService


class LoginView(APIView):
    """Log a user in through Supabase Auth."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    service = SupabaseAuthService()

    @extend_schema(
        operation_id="auth_login",
        tags=["auth"],
        request=LoginRequestSerializer,
        responses={200: SessionSerializer},
        examples=[
            OpenApiExample(
                "Password login",
                value={"email": "user@example.com", "password": "secret123"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = self.service.login(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        response_serializer = SessionSerializer(data=session)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.validated_data,
                        status=status.HTTP_200_OK)
