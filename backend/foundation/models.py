import uuid

from django.conf import settings
from django.db import models


class ExamContext(models.Model):
    class Status(models.TextChoices):
        SETUP = 'SETUP', 'Đang chuẩn bị'
        OPEN = 'OPEN', 'Đang tiếp nhận'
        CLOSED = 'CLOSED', 'Đã đóng'

    key = models.CharField(max_length=80, unique=True)
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

    def __str__(self):
        return self.key


class ContextAssignment(models.Model):
    class Role(models.TextChoices):
        OPERATOR = 'OPERATOR', 'Nhân sự tại cửa'
        REVIEWER = 'REVIEWER', 'Người nhận case'

    context = models.ForeignKey(ExamContext, on_delete=models.PROTECT, related_name='assignments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='exam_assignments')
    role = models.CharField(max_length=12, choices=Role.choices)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['context', 'user', 'role'], name='one_context_role_per_user')]


class Registration(models.Model):
    context = models.ForeignKey(ExamContext, on_delete=models.PROTECT, related_name='registrations')
    source_key = models.CharField(max_length=80)
    declared_code = models.CharField(max_length=80, db_index=True)
    roster_version = models.CharField(max_length=80)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['context', 'roster_version', 'source_key'], name='one_registration_per_roster_version',
        )]


class Attempt(models.Model):
    class Status(models.TextChoices):
        STARTED = 'STARTED', 'Đã bắt đầu'
        IN_PROGRESS = 'IN_PROGRESS', 'Đang xử lý'
        CONCLUDED = 'CONCLUDED', 'Đã kết thúc'
        INTERRUPTED = 'INTERRUPTED', 'Bị gián đoạn'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context = models.ForeignKey(ExamContext, on_delete=models.PROTECT, related_name='attempts')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='exam_attempts')
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
        CLOSED = 'CLOSED', 'Đã xử lý'

    attempt = models.ForeignKey(Attempt, on_delete=models.PROTECT, related_name='review_cases')
    reason_code = models.CharField(max_length=80)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    assigned_role = models.CharField(max_length=12, default=ContextAssignment.Role.REVIEWER)
    created_at = models.DateTimeField(auto_now_add=True)


class AuditEvent(models.Model):
    attempt = models.ForeignKey(Attempt, null=True, blank=True, on_delete=models.PROTECT, related_name='audit_events')
    context = models.ForeignKey(ExamContext, on_delete=models.PROTECT, related_name='audit_events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    action = models.CharField(max_length=80)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
