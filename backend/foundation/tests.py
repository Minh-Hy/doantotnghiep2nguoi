import json
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from .models import (
    Attempt, AuditEvent, ContextAssignment, Exam, ExamContext, ExamSession,
    PolicyVersion, Registration, Room, RosterBatch,
)


class FoundationApiTests(TestCase):
    def setUp(self):
        self.operator = get_user_model().objects.create_user(username='operator-test', password='only-for-test')
        exam = Exam.objects.create(key='EXAM-SIM-01', title='Kỳ thi giả lập')
        session = ExamSession.objects.create(exam=exam, key='SESSION-SIM-01')
        room = Room.objects.create(key='ROOM-SIM-01')
        self.context = ExamContext.objects.create(
            key='CTX-SIM-01', exam_key='EXAM-SIM-01', session_key='SESSION-SIM-01',
            room_key='ROOM-SIM-01', roster_version='R-SIM-001-draft',
            policy_version='P-SIM-001-draft', session=session, room=room,
        )
        self.context.active_roster = RosterBatch.objects.create(
            context=self.context, version=self.context.roster_version,
        )
        self.context.active_policy = PolicyVersion.objects.create(
            context=self.context, version=self.context.policy_version,
        )
        self.context.save(update_fields=['active_roster', 'active_policy'])
        ContextAssignment.objects.create(
            context=self.context, user=self.operator, role=ContextAssignment.Role.OPERATOR,
        )

    def _open_context(self):
        self.context.status = ExamContext.Status.OPEN
        self.context.policy_approved_at = timezone.now()
        self.context.policy_approved_by = self.operator
        self.context.save()
        self.context.active_roster.status = RosterBatch.Status.ACTIVE
        self.context.active_roster.save(update_fields=['status'])
        self.context.active_policy.status = PolicyVersion.Status.APPROVED
        self.context.active_policy.approved_at = self.context.policy_approved_at
        self.context.active_policy.approved_by = self.operator
        self.context.active_policy.save(update_fields=['status', 'approved_at', 'approved_by'])

    def _post_attempt(self, *, key='request-0001', code='SIM001'):
        return self.client.post(
            '/api/v1/attempts/',
            data=json.dumps({'context_key': self.context.key, 'declared_code': code}),
            content_type='application/json',
            HTTP_IDEMPOTENCY_KEY=key,
        )

    def test_public_health_and_database_readiness(self):
        self.assertEqual(self.client.get('/api/v1/health/').json()['status'], 'ok')
        self.assertEqual(self.client.get('/api/v1/ready/').json()['status'], 'ready')

    @override_settings(CORS_ALLOWED_ORIGINS=['http://127.0.0.1:7357'])
    def test_edge_preview_origin_is_allowed_only_on_local_port(self):
        response = self.client.options(
            '/api/v1/auth/login/',
            HTTP_ORIGIN='http://127.0.0.1:7357',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS='content-type',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Origin'], 'http://127.0.0.1:7357')
        other = self.client.options(
            '/api/v1/auth/login/',
            HTTP_ORIGIN='http://example.test',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
        )
        self.assertNotIn('Access-Control-Allow-Origin', other)

    def test_context_list_requires_login_and_assignment(self):
        self.assertIn(self.client.get('/api/v1/contexts/').status_code, (401, 403))
        outsider = get_user_model().objects.create_user(username='outsider-test', password='only-for-test')
        self.client.force_login(outsider)
        self.assertEqual(self.client.get('/api/v1/contexts/').json(), [])
        self.client.force_login(self.operator)
        self.assertEqual(self.client.get('/api/v1/contexts/').json()[0]['key'], self.context.key)

    def test_draft_policy_blocks_attempt(self):
        self.client.force_login(self.operator)
        response = self._post_attempt()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['code'], 'CONTEXT_NOT_READY')
        self.assertFalse(Attempt.objects.exists())

    def test_idempotent_attempt_keeps_one_audit_event(self):
        self._open_context()
        self.client.force_login(self.operator)

        first = self._post_attempt()
        self.context.status = ExamContext.Status.CLOSED
        self.context.save(update_fields=['status'])
        retry = self._post_attempt()
        conflict = self._post_attempt(code='SIM002')

        self.assertEqual((first.status_code, retry.status_code, conflict.status_code), (201, 200, 409))
        self.assertEqual(first.json()['id'], retry.json()['id'])
        self.assertEqual(first.json()['roster_version'], 'R-SIM-001-draft')
        self.assertEqual(Attempt.objects.count(), 1)
        self.assertEqual(AuditEvent.objects.filter(action='ATTEMPT_STARTED').count(), 1)

    def test_reviewer_cannot_create_attempt(self):
        ContextAssignment.objects.filter(user=self.operator).update(role=ContextAssignment.Role.REVIEWER)
        self._open_context()
        self.client.force_login(self.operator)
        self.assertEqual(self._post_attempt().status_code, 403)
        self.assertFalse(Attempt.objects.exists())

    def test_login_context_and_logout(self):
        login = self.client.post(
            '/api/v1/auth/login/',
            data=json.dumps({'username': 'operator-test', 'password': 'only-for-test'}),
            content_type='application/json',
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()['token']
        contexts = self.client.get('/api/v1/contexts/', HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(contexts.status_code, 200)
        self.assertEqual(contexts.json()[0]['status'], 'SETUP')
        self.assertFalse(contexts.json()[0]['policy_approved'])
        self.assertEqual(
            self.client.post('/api/v1/auth/logout/', HTTP_AUTHORIZATION=f'Token {token}').status_code,
            204,
        )
        self.assertIn(
            self.client.get('/api/v1/contexts/', HTTP_AUTHORIZATION=f'Token {token}').status_code,
            (401, 403),
        )

    def test_seed_demo_is_repeatable_and_does_not_approve_policy(self):
        output = StringIO()
        call_command('seed_demo', operator='operator-test', stdout=output)
        call_command('seed_demo', operator='operator-test', stdout=output)
        context = ExamContext.objects.get(key='CTX-SIM-01')
        self.assertEqual(context.status, ExamContext.Status.SETUP)
        self.assertIsNone(context.policy_approved_at)
        self.assertEqual(Registration.objects.filter(context=context).count(), 2)
