import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import DatabaseError, IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import AuditEvent, Attempt, CheckIn, ContextAccess, ExamSession, IntakeContext, Registration, ReviewCase, Room


class AttemptApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="operator", password="test-password")
        self.other_user = get_user_model().objects.create_user(username="other", password="test-password")
        self.session = ExamSession.objects.create(code="EXAM-A", name="Kỳ thi giả lập")
        self.room = Room.objects.create(code="R-01", name="Phòng 01")
        self.other_room = Room.objects.create(code="R-02", name="Phòng 02")
        self.context = IntakeContext.objects.create(
            session=self.session,
            room=self.room,
            roster_version="fixture-v1",
            roster_confirmed_at=timezone.now(),
            roster_confirmed_by=self.user,
            policy_version="fixture-policy-v1",
            policy_approved_at=timezone.now(),
            policy_approved_by=self.user,
            review_role="fixture-reviewer",
            status=IntakeContext.Status.OPEN,
        )
        ContextAccess.objects.create(user=self.user, context=self.context, role=ContextAccess.Role.OPERATOR)
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def post_attempt(self, code, key=None, context=None):
        return self.client.post(
            "/api/v1/attempts/",
            {
                "context_id": (context or self.context).pk,
                "candidate_code": code,
                "idempotency_key": str(key or uuid.uuid4()),
            },
            format="json",
        )

    def add_registration(self, source_key, code, room=None):
        return Registration.objects.create(
            session=self.session,
            room=room or self.room,
            roster_version="fixture-v1",
            source_key=source_key,
            candidate_code=code,
        )

    def test_resolved_lookup_starts_attempt_without_checkin(self):
        self.add_registration("source-1", "TS-001")
        response = self.post_attempt("TS-001")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["lookup_outcome"], "FOUND")
        self.assertEqual(response.data["status"], "IN_PROGRESS")
        self.assertEqual(response.data["next_action"], "VERIFY_IDENTITY")
        self.assertEqual(Attempt.objects.count(), 1)
        self.assertEqual(CheckIn.objects.count(), 0)
        self.assertEqual(AuditEvent.objects.count(), 2)

    def test_missing_or_ambiguous_registration_opens_review_without_fabricating_record(self):
        missing = self.post_attempt("UNKNOWN")
        self.add_registration("source-1", "DUPLICATE")
        self.add_registration("source-2", "DUPLICATE")
        ambiguous = self.post_attempt("DUPLICATE")

        self.assertEqual(missing.status_code, 201)
        self.assertEqual(missing.data["lookup_outcome"], "NOT_FOUND")
        self.assertEqual(ambiguous.data["lookup_outcome"], "AMBIGUOUS")
        self.assertEqual(missing.data["next_action"], "REVIEW")
        self.assertEqual(ambiguous.data["next_action"], "REVIEW")
        self.assertEqual(ReviewCase.objects.count(), 2)
        self.assertEqual(Registration.objects.count(), 2)
        self.assertIsNone(Attempt.objects.get(pk=missing.data["id"]).registration_id)
        self.assertIsNone(Attempt.objects.get(pk=ambiguous.data["id"]).registration_id)

    def test_wrong_room_keeps_registration_but_opens_review(self):
        registration = self.add_registration("source-1", "TS-002", self.other_room)
        response = self.post_attempt("TS-002")

        self.assertEqual(response.data["lookup_outcome"], "WRONG_ROOM")
        self.assertEqual(response.data["status"], "REVIEW_PENDING")
        self.assertEqual(Attempt.objects.get(pk=response.data["id"]).registration, registration)
        self.assertEqual(ReviewCase.objects.get(attempt_id=response.data["id"]).assigned_role, "fixture-reviewer")
        self.assertEqual(CheckIn.objects.count(), 0)

    def test_idempotency_preserves_one_attempt_and_detects_payload_change(self):
        self.add_registration("source-1", "TS-003")
        key = uuid.uuid4()
        first = self.post_attempt("TS-003", key)
        repeated = self.post_attempt("TS-003", key)
        conflict = self.post_attempt("TS-OTHER", key)

        self.assertEqual(first.status_code, 201)
        self.assertEqual(repeated.status_code, 200)
        self.assertFalse(repeated.data["created"])
        self.assertEqual(repeated.data["id"], first.data["id"])
        self.assertEqual(conflict.status_code, 409)
        self.assertEqual(conflict.data["code"], "IDEMPOTENCY_KEY_REUSED")
        self.assertEqual(Attempt.objects.count(), 1)
        self.assertEqual(AuditEvent.objects.count(), 2)

    def test_requires_context_access_and_open_status(self):
        other_token = Token.objects.create(user=self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {other_token.key}")
        forbidden = self.post_attempt("TS-004")
        self.assertEqual(forbidden.status_code, 403)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.get(user=self.user).key}")
        self.context.status = IntakeContext.Status.CLOSED
        self.context.save(update_fields=["status"])
        closed = self.post_attempt("TS-004")
        self.assertEqual(closed.status_code, 409)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_other_user_cannot_read_attempt(self):
        response = self.post_attempt("UNKNOWN")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=self.other_user).key}")
        detail = self.client.get(f"/api/v1/attempts/{response.data['id']}/")
        self.assertEqual(detail.status_code, 404)

    def test_unauthenticated_can_only_read_health(self):
        self.client.credentials()
        self.assertEqual(self.client.get("/api/v1/health/").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/ready/").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/ready/", HTTP_HOST="10.0.2.2:8000").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/contexts/").status_code, 401)
        self.assertEqual(self.post_attempt("TS-001").status_code, 401)

    def test_readiness_reports_database_failure_without_details(self):
        self.client.credentials()
        with patch("entry.views.connection.cursor", side_effect=DatabaseError("secret connection detail")):
            response = self.client.get("/api/v1/ready/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data, {"status": "unavailable"})

    def test_login_context_roles_and_logout(self):
        self.client.credentials()
        bad = self.client.post("/api/v1/auth/login/", {"username": "operator", "password": "wrong"}, format="json")
        self.assertEqual(bad.status_code, 401)
        missing = self.client.post("/api/v1/auth/login/", {"username": "operator"}, format="json")
        self.assertEqual(missing.status_code, 400)
        login = self.client.post(
            "/api/v1/auth/login/", {"username": "operator", "password": "test-password"}, format="json"
        )
        self.assertEqual(login.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        contexts = self.client.get("/api/v1/contexts/")
        self.assertEqual(contexts.status_code, 200)
        self.assertEqual(len(contexts.data), 1)
        self.assertEqual(contexts.data[0]["roles"], ["OPERATOR"])
        self.assertEqual(self.client.post("/api/v1/auth/logout/").status_code, 204)
        self.assertEqual(self.client.get("/api/v1/contexts/").status_code, 401)

    def test_database_rejects_open_context_without_approved_references(self):
        other_session = ExamSession.objects.create(code="EXAM-B", name="Kỳ thi khác")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                IntakeContext.objects.create(session=other_session, room=self.room, status=IntakeContext.Status.OPEN)

    def test_database_prevents_duplicate_effective_checkin(self):
        registration = self.add_registration("source-1", "TS-005")
        first = self.post_attempt("TS-005")
        second = self.post_attempt("TS-005")
        CheckIn.objects.create(
            session=self.session,
            registration=registration,
            attempt=Attempt.objects.get(pk=first.data["id"]),
            recorded_by=self.user,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CheckIn.objects.create(
                    session=self.session,
                    registration=registration,
                    attempt=Attempt.objects.get(pk=second.data["id"]),
                    recorded_by=self.user,
                )

    def test_demo_seed_is_repeatable_and_keeps_context_closed(self):
        call_command("seed_demo", operator=self.user.username, verbosity=0)
        call_command("seed_demo", operator=self.user.username, verbosity=0)
        context = IntakeContext.objects.get(session__code="DEMO-T018-HOC-PHAN")
        self.assertEqual(context.status, IntakeContext.Status.SETUP)
        self.assertEqual(
            Registration.objects.filter(session=context.session, roster_version="demo-v1").count(), 2
        )
        self.assertEqual(CheckIn.objects.count(), 0)
