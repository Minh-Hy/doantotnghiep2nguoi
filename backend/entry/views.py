from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attempt, IntakeContext
from .serializers import AttemptSerializer, ContextSerializer, StartAttemptSerializer
from .services import ContextAccessDenied, ContextNotOpen, IdempotencyConflict, start_attempt


def visible_contexts(user):
    contexts = IntakeContext.objects.select_related("session", "room")
    if user.is_superuser:
        return contexts
    return contexts.filter(access_grants__user=user).distinct()


class HealthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "exam-entry-api"})


class ContextListView(APIView):
    def get(self, request):
        return Response(ContextSerializer(visible_contexts(request.user), many=True).data)


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
