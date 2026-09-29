import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Device(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Đang dùng'
        REVOKED = 'REVOKED', 'Đã thu hồi'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_key = models.UUIDField(unique=True)
    label = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)


class SyncSubmission(models.Model):
    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', 'Đã nhận'
        APPLIED = 'APPLIED', 'Đã áp dụng'
        REJECTED = 'REJECTED', 'Bị từ chối'
        REVIEW = 'REVIEW', 'Cần xem xét'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name='sync_submissions')
    context = models.ForeignKey('foundation.ExamContext', on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    attempt = models.ForeignKey('foundation.Attempt', null=True, blank=True, on_delete=models.PROTECT)
    client_event_id = models.UUIDField()
    event_type = models.CharField(max_length=60)
    payload_sha256 = models.CharField(max_length=64)
    observed_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.RECEIVED)
    error_code = models.CharField(max_length=80, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['device', 'client_event_id'], name='one_submission_per_device_event')]
        indexes = [models.Index(fields=['context', 'status', 'received_at'], name='sync_context_status_idx')]


class VerificationTry(models.Model):
    class Outcome(models.TextChoices):
        SATISFIED = 'satisfied', 'Đáp ứng'
        UNMET = 'unmet', 'Không đáp ứng'
        UNAVAILABLE = 'unavailable', 'Không khả dụng'
        INCONCLUSIVE = 'inconclusive', 'Chưa rõ'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey('foundation.Attempt', on_delete=models.PROTECT, related_name='verification_tries')
    try_no = models.PositiveSmallIntegerField()
    outcome = models.CharField(max_length=16, choices=Outcome.choices)
    reason_code = models.CharField(max_length=80, blank=True)
    pipeline_version = models.CharField(max_length=80)
    model_version = models.CharField(max_length=80)
    evidence_ref = models.ForeignKey('foundation.AssetReference', null=True, blank=True, on_delete=models.PROTECT)
    observed_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['attempt', 'try_no'], name='one_verification_per_try_number'),
            models.CheckConstraint(condition=Q(try_no__gte=1) & Q(try_no__lte=2), name='verification_try_number_1_or_2'),
        ]


class CheckIn(models.Model):
    class Status(models.TextChoices):
        RECORDED = 'RECORDED', 'Đã ghi nhận'
        DISPUTED = 'DISPUTED', 'Đang tranh chấp'
        VOIDED = 'VOIDED', 'Đã hủy qua correction'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey('foundation.ExamSession', on_delete=models.PROTECT)
    context = models.ForeignKey('foundation.ExamContext', on_delete=models.PROTECT, related_name='checkins')
    candidate = models.ForeignKey('foundation.Candidate', on_delete=models.PROTECT)
    registration = models.ForeignKey('foundation.Registration', on_delete=models.PROTECT)
    attempt = models.ForeignKey('foundation.Attempt', on_delete=models.PROTECT)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.RECORDED)
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    confirmed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['session', 'candidate'],
            condition=Q(status__in=['RECORDED', 'DISPUTED']),
            name='one_effective_checkin_per_candidate_session',
        )]

    def clean(self):
        if self.context_id and self.session_id != self.context.session_id:
            raise ValidationError({'session': 'Session check-in phải khớp context.'})
        if self.registration_id and (
            self.registration.context_id != self.context_id or self.registration.candidate_id != self.candidate_id
        ):
            raise ValidationError({'registration': 'Registration check-in phải khớp context và candidate.'})
        if self.attempt_id and self.attempt.context_id != self.context_id:
            raise ValidationError({'attempt': 'Attempt check-in phải thuộc context.'})


class ReviewDecision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey('foundation.ReviewCase', on_delete=models.PROTECT, related_name='decisions')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    decision_code = models.CharField(max_length=80)
    reason = models.TextField()
    policy_version = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)


class EntryDecision(models.Model):
    class Outcome(models.TextChoices):
        NOT_APPLICABLE = 'NOT_APPLICABLE', 'Ngoài phạm vi'
        ALLOWED = 'ALLOWED', 'Được phép'
        DENIED = 'DENIED', 'Không được phép'
        UNRESOLVED = 'UNRESOLVED', 'Chưa kết luận'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context = models.ForeignKey('foundation.ExamContext', on_delete=models.PROTECT)
    candidate = models.ForeignKey('foundation.Candidate', on_delete=models.PROTECT)
    attempt = models.ForeignKey('foundation.Attempt', null=True, blank=True, on_delete=models.PROTECT)
    outcome = models.CharField(max_length=16, choices=Outcome.choices, default=Outcome.NOT_APPLICABLE)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    decided_at = models.DateTimeField(null=True, blank=True)
    policy_version = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AttendanceReport(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Nháp'
        FINALIZED = 'FINALIZED', 'Đã xác nhận'
        REOPENED = 'REOPENED', 'Mở lại'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey('foundation.ExamSession', on_delete=models.PROTECT, related_name='attendance_reports')
    version = models.PositiveIntegerField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_attendance_reports')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['session', 'version'], name='one_attendance_report_version')]


class AttendanceResult(models.Model):
    class Status(models.TextChoices):
        UNFINALIZED = 'UNFINALIZED', 'Chưa chốt'
        PRESENT_CONFIRMED = 'PRESENT_CONFIRMED', 'Có mặt'
        ABSENT_CONFIRMED = 'ABSENT_CONFIRMED', 'Vắng mặt'
        UNDETERMINED = 'UNDETERMINED', 'Chưa xác định'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(AttendanceReport, on_delete=models.PROTECT, related_name='results')
    candidate = models.ForeignKey('foundation.Candidate', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNFINALIZED)
    evidence_summary = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['report', 'candidate'], name='one_attendance_result_per_report')]


class Correction(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Đã yêu cầu'
        APPROVED = 'APPROVED', 'Đã duyệt'
        REJECTED = 'REJECTED', 'Không duyệt'
        APPLIED = 'APPLIED', 'Đã áp dụng'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context = models.ForeignKey('foundation.ExamContext', on_delete=models.PROTECT)
    checkin = models.ForeignKey(CheckIn, null=True, blank=True, on_delete=models.PROTECT)
    entry_decision = models.ForeignKey(EntryDecision, null=True, blank=True, on_delete=models.PROTECT)
    attendance_result = models.ForeignKey(AttendanceResult, null=True, blank=True, on_delete=models.PROTECT)
    registration = models.ForeignKey('foundation.Registration', null=True, blank=True, on_delete=models.PROTECT)
    before_state = models.JSONField(default=dict)
    proposed_state = models.JSONField(default=dict)
    reason = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.REQUESTED)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='requested_corrections')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=(
                Q(checkin__isnull=False, entry_decision__isnull=True, attendance_result__isnull=True, registration__isnull=True)
                | Q(checkin__isnull=True, entry_decision__isnull=False, attendance_result__isnull=True, registration__isnull=True)
                | Q(checkin__isnull=True, entry_decision__isnull=True, attendance_result__isnull=False, registration__isnull=True)
                | Q(checkin__isnull=True, entry_decision__isnull=True, attendance_result__isnull=True, registration__isnull=False)
            ),
            name='correction_has_one_target',
        )]
