import re

from django.contrib.auth import authenticate
from django.db import connection
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attempt, ContextAssignment, ExamContext
from .serializers import AttemptCreateSerializer, AttemptSerializer, ContextSerializer, LoginSerializer
from .services import AttemptConflict, start_attempt


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok', 'phase': 'M1', 'profile': 'draft'})


class ReadyView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            tables = set(connection.introspection.table_names())
            migrated = {
                'foundation_examcontext', 'foundation_rosterbatch',
                'foundation_checkin', 'foundation_syncsubmission',
            }.issubset(tables)
        except Exception:
            migrated = False
        if not migrated:
            return Response({'status': 'not_ready', 'database': 'unavailable'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'status': 'ready', 'database': 'ready'})


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        incoming = LoginSerializer(data=request.data)
        incoming.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=incoming.validated_data['username'],
            password=incoming.validated_data['password'],
        )
        if user is None or not user.is_active:
            return Response({'code': 'INVALID_CREDENTIALS'}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.get_username()})


class LogoutView(APIView):
    def post(self, request):
        if isinstance(request.auth, Token):
            request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContextListView(APIView):
    def get(self, request):
        contexts = ExamContext.objects.filter(assignments__user=request.user).distinct().order_by('key')
        return Response(ContextSerializer(contexts, many=True).data)


class AttemptListCreateView(APIView):
    def get(self, request):
        attempts = Attempt.objects.filter(actor=request.user).select_related('context')[:50]
        return Response(AttemptSerializer(attempts, many=True).data)

    def post(self, request):
        incoming = AttemptCreateSerializer(data=request.data)
        incoming.is_valid(raise_exception=True)
        key = request.headers.get('Idempotency-Key', '')
        if not re.fullmatch(r'[A-Za-z0-9._:-]{8,128}', key):
            return Response({'code': 'IDEMPOTENCY_KEY_REQUIRED'}, status=status.HTTP_400_BAD_REQUEST)

        context = get_object_or_404(
            ExamContext.objects.filter(assignments__user=request.user).distinct(),
            key=incoming.validated_data['context_key'],
        )
        try:
            attempt, created = start_attempt(
                actor=request.user,
                context=context,
                declared_code=incoming.validated_data['declared_code'],
                idempotency_key=key,
            )
        except AttemptConflict as exc:
            code = status.HTTP_403_FORBIDDEN if exc.code == 'OPERATOR_REQUIRED' else status.HTTP_409_CONFLICT
            return Response({'code': exc.code}, status=code)
        return Response(AttemptSerializer(attempt).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class AttemptDetailView(APIView):
    def get(self, request, attempt_id):
        attempt = get_object_or_404(
            Attempt.objects.select_related('context'), id=attempt_id, actor=request.user,
        )
        return Response(AttemptSerializer(attempt).data)
