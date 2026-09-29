import uuid
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from .models import (
    Attempt, CheckIn, Correction, Device, ExamContext, PolicyVersion,
    Registration, Room, RosterBatch, SyncSubmission, VerificationTry,
)


class DomainConstraintTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='schema-operator', password='only-for-test')
        call_command('seed_demo', operator=self.user.username, stdout=StringIO())
        self.context = ExamContext.objects.get(key='CTX-SIM-01')
        self.registration = Registration.objects.get(context=self.context, source_key='REG-SIM-001')
        self.attempt = Attempt.objects.create(
            context=self.context, actor=self.user, registration=self.registration,
            declared_code='SIM001', roster_version=self.context.roster_version,
            policy_version=self.context.policy_version, idempotency_key='schema-attempt-1',
        )

    def test_one_effective_checkin_per_candidate_session_even_if_room_changes(self):
        CheckIn.objects.create(
            session=self.context.session, context=self.context, candidate=self.registration.candidate,
            registration=self.registration, attempt=self.attempt,
            confirmed_by=self.user, confirmed_at=timezone.now(),
        )
        other_room = Room.objects.create(key='ROOM-SIM-02')
        other_context = ExamContext.objects.create(
            key='CTX-SIM-02', exam_key=self.context.exam_key, session_key=self.context.session_key,
            room_key=other_room.key, session=self.context.session, room=other_room,
            roster_version='R-SIM-002-draft', policy_version='P-SIM-002-draft',
        )
        batch = RosterBatch.objects.create(context=other_context, version='R-SIM-002-draft')
        moved_registration = Registration.objects.create(
            context=other_context, candidate=self.registration.candidate, roster_batch=batch,
            source_key='REG-MOVED-001', declared_code='SIM001', roster_version=batch.version,
        )
        moved_attempt = Attempt.objects.create(
            context=other_context, actor=self.user, registration=moved_registration,
            declared_code='SIM001', roster_version=batch.version,
            policy_version=other_context.policy_version, idempotency_key='schema-attempt-2',
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            CheckIn.objects.create(
                session=other_context.session, context=other_context, candidate=moved_registration.candidate,
                registration=moved_registration, attempt=moved_attempt,
                confirmed_by=self.user, confirmed_at=timezone.now(),
            )

    def test_retry_is_limited_to_two_and_sync_event_is_idempotent(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            VerificationTry.objects.create(
                attempt=self.attempt, try_no=3, outcome=VerificationTry.Outcome.UNAVAILABLE,
                pipeline_version='B0-test', model_version='test', observed_at=timezone.now(),
            )
        device = Device.objects.create(client_key=uuid.uuid4(), registered_by=self.user)
        event_id = uuid.uuid4()
        payload = dict(
            device=device, context=self.context, actor=self.user, client_event_id=event_id,
            event_type='ATTEMPT', payload_sha256='a' * 64, observed_at=timezone.now(),
        )
        SyncSubmission.objects.create(**payload)
        with self.assertRaises(IntegrityError), transaction.atomic():
            SyncSubmission.objects.create(**payload)

    def test_policy_approval_and_active_roster_require_consistent_records(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            PolicyVersion.objects.create(
                context=self.context, version='P-INVALID', status=PolicyVersion.Status.APPROVED,
            )
        RosterBatch.objects.filter(pk=self.context.active_roster_id).update(status=RosterBatch.Status.ACTIVE)
        with self.assertRaises(IntegrityError), transaction.atomic():
            RosterBatch.objects.create(
                context=self.context, version='R-SIM-SECOND', status=RosterBatch.Status.ACTIVE,
            )

    def test_correction_must_point_to_exactly_one_record(self):
        base = dict(
            context=self.context, requested_by=self.user, reason='fixture test',
            before_state={}, proposed_state={},
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Correction.objects.create(**base)
        Correction.objects.create(**base, registration=self.registration)
        self.assertEqual(Correction.objects.count(), 1)
