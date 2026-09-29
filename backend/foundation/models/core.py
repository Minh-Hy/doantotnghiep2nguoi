import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ExamContext(models.Model):
    class Status(models.TextChoices):
        SETUP = 'SETUP', 'Đang chuẩn bị'
        OPEN = 'OPEN', 'Đang tiếp nhận'
        CLOSED = 'CLOSED', 'Đã đóng'

    key = models.CharField(max_length=80, unique=True)
    session = models.ForeignKey('foundation.ExamSession', on_delete=models.PROTECT)
    room = models.ForeignKey('foundation.Room', on_delete=models.PROTECT)
    active_roster = models.ForeignKey(
        'foundation.RosterBatch', null=True, blank=True, on_delete=models.PROTECT, related_name='active_for_contexts',
    )
    active_policy = models.ForeignKey(
        'foundation.PolicyVersion', null=True, blank=True, on_delete=models.PROTECT, related_name='active_for_contexts',
    )
    exam_key = models.CharField(max_length=80)
    session_key = models.CharField(max_length=80)
    room_key = models.CharField(max_length=80)
    roster_version = models.CharField(max_length=80)
    policy_version = models.CharField(max_length=80)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SETUP)
    policy_approved_at = models.DateTimeField(null=True, blank=True)
    policy_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
        related_name='approved_exam_contexts',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.session_id and self.exam_key != self.session.exam.key:
            raise ValidationError({'exam_key': 'Exam snapshot không khớp session.'})
        if self.session_id and self.session_key != self.session.key:
            raise ValidationError({'session_key': 'Session snapshot không khớp session.'})
        if self.room_id and self.room_key != self.room.key:
            raise ValidationError({'room_key': 'Room snapshot không khớp room.'})
        if self.active_roster_id and (
            self.active_roster.context_id != self.pk or self.active_roster.version != self.roster_version
        ):
            raise ValidationError({'active_roster': 'Roster active phải thuộc context và đúng version.'})
        if self.active_policy_id and (
            self.active_policy.context_id != self.pk or self.active_policy.version != self.policy_version
        ):
            raise ValidationError({'active_policy': 'Policy active phải thuộc context và đúng version.'})

    def __str__(self):
        return self.key


class ContextAssignment(models.Model):
    class Role(models.TextChoices):
        OPERATOR = 'OPERATOR', 'Nhân sự tại cửa'
        REVIEWER = 'REVIEWER', 'Người nhận case'
        ROSTER_MANAGER = 'ROSTER_MANAGER', 'Quản lý roster'
        POLICY_APPROVER = 'POLICY_APPROVER', 'Duyệt policy'
        RECONCILER = 'RECONCILER', 'Đối soát'
        AUDITOR = 'AUDITOR', 'Đọc audit'

    context = models.ForeignKey(ExamContext, on_delete=models.PROTECT, related_name='assignments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='exam_assignments')
    role = models.CharField(max_length=24, choices=Role.choices)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['context', 'user', 'role'], name='one_context_role_per_user')]


class Registration(models.Model):
    context = models.ForeignKey(ExamContext, on_delete=models.PROTECT, related_name='registrations')
    candidate = models.ForeignKey('foundation.Candidate', on_delete=models.PROTECT)
    roster_batch = models.ForeignKey('foundation.RosterBatch', on_delete=models.PROTECT)
    source_key = models.CharField(max_length=80)
    declared_code = models.CharField(max_length=80, db_index=True)
    roster_version = models.CharField(max_length=80)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['context', 'roster_version', 'source_key'], name='one_registration_per_roster_version',
        )]

    def clean(self):
        if self.roster_batch_id and (
            self.roster_batch.context_id != self.context_id or self.roster_batch.version != self.roster_version
        ):
            raise ValidationError({'roster_batch': 'Registration phải thuộc đúng context và roster version.'})


class Attempt(models.Model):
    class Status(models.TextChoices):
        STARTED = 'STARTED', 'Đã bắt đầu'
        IN_PROGRESS = 'IN_PROGRESS', 'Đang xử lý'
        CONCLUDED = 'CONCLUDED', 'Đã kết thúc'
        INTERRUPTED = 'INTERRUPTED', 'Bị gián đoạn'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context = models.ForeignKey(ExamContext, on_delete=models.PROTECT, related_name='attempts')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='exam_attempts')
    device = models.ForeignKey('foundation.Device', null=True, blank=True, on_delete=models.PROTECT)
    previous_attempt = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)
    client_event_id = models.UUIDField(null=True, blank=True, unique=True)
    observed_at = models.DateTimeField(null=True, blank=True)
    registration = models.ForeignKey(Registration, null=True, blank=True, on_delete=models.PROTECT)
    declared_code = models.CharField(max_length=80)
    roster_version = models.CharField(max_length=80)
    policy_version = models.CharField(max_length=80)
    idempotency_key = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.STARTED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['context', 'actor', 'idempotency_key'], name='one_attempt_per_idempotency_key',
        )]
        ordering = ['-created_at']


class ReviewCase(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Đang chờ'
        IN_REVIEW = 'IN_REVIEW', 'Đang xử lý'
        CLOSED = 'CLOSED', 'Đã xử lý'

    attempt = models.ForeignKey(Attempt, on_delete=models.PROTECT, related_name='review_cases')
    reason_code = models.CharField(max_length=80)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    assigned_role = models.CharField(max_length=24, default=ContextAssignment.Role.REVIEWER)
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    next_action = models.CharField(max_length=160, blank=True)
    resolution_code = models.CharField(max_length=80, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AuditEvent(models.Model):
    attempt = models.ForeignKey(Attempt, null=True, blank=True, on_delete=models.PROTECT, related_name='audit_events')
    context = models.ForeignKey(ExamContext, on_delete=models.PROTECT, related_name='audit_events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    action = models.CharField(max_length=80)
    actor_role = models.CharField(max_length=24, blank=True)
    subject_type = models.CharField(max_length=80, blank=True)
    subject_key = models.CharField(max_length=80, blank=True)
    occurred_at = models.DateTimeField(null=True, blank=True)
    request_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['context', 'created_at'], name='audit_context_time_idx')]
