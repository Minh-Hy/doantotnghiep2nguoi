from django.contrib.auth import authenticate
from django.db import DatabaseError, connection
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import Attempt, ContextAccess, IntakeContext
from .serializers import AttemptSerializer, ContextSerializer, LoginSerializer, StartAttemptSerializer
from .services import ContextAccessDenied, ContextNotOpen, IdempotencyConflict, start_attempt


def visible_contexts(user):
    contexts = IntakeContext.objects.select_related("session", "room").prefetch_related(
        Prefetch("access_grants", queryset=ContextAccess.objects.filter(user=user), to_attr="current_user_grants")
    )
    if user.is_superuser:
        return contexts
    return contexts.filter(access_grants__user=user).distinct()


class HealthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "exam-entry-api"})


class ReadinessView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except DatabaseError:
            return Response({"status": "unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"status": "ready"})


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth-login"

    def post(self, request):
        input_serializer = LoginSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user = authenticate(request, **input_serializer.validated_data)
        if user is None or not user.is_active:
            return Response({"code": "INVALID_CREDENTIALS"}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.get_username()})


class LogoutView(APIView):
    def post(self, request):
        if isinstance(request.auth, Token):
            request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContextListView(APIView):
    def get(self, request):
        return Response(ContextSerializer(visible_contexts(request.user), many=True, context={"request": request}).data)


class AttemptListCreateView(APIView):
    def post(self, request):
        input_serializer = StartAttemptSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        context = get_object_or_404(IntakeContext, pk=data["context_id"])
        try:
            result = start_attempt(
                user=request.user,
                context=context,
                candidate_code=data["candidate_code"],
                idempotency_key=data["idempotency_key"],
            )
        except ContextAccessDenied:
            return Response({"code": "CONTEXT_ACCESS_DENIED"}, status=status.HTTP_403_FORBIDDEN)
        except ContextNotOpen:
            return Response({"code": "CONTEXT_NOT_OPEN"}, status=status.HTTP_409_CONFLICT)
        except IdempotencyConflict:
            return Response({"code": "IDEMPOTENCY_KEY_REUSED"}, status=status.HTTP_409_CONFLICT)

        output = AttemptSerializer(result.attempt).data
        output["created"] = result.created
        return Response(output, status=status.HTTP_201_CREATED if result.created else status.HTTP_200_OK)


class AttemptDetailView(APIView):
    def get(self, request, attempt_id):
        attempt = get_object_or_404(
            Attempt.objects.select_related("context").filter(context__in=visible_contexts(request.user)),
            pk=attempt_id,
        )
        return Response(AttemptSerializer(attempt).data)
