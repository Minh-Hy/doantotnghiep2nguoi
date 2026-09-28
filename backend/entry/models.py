import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class ExamSession(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.code


class Room(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.code


class IntakeContext(models.Model):
    class Status(models.TextChoices):
        SETUP = "SETUP", "Đang chuẩn bị"
        OPEN = "OPEN", "Đang tiếp nhận"
        CLOSED = "CLOSED", "Đã đóng"

    session = models.ForeignKey(ExamSession, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    roster_version = models.CharField(max_length=80, blank=True)
    roster_confirmed_at = models.DateTimeField(null=True, blank=True)
    roster_confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="confirmed_rosters"
    )
    policy_version = models.CharField(max_length=80, blank=True)
    policy_approved_at = models.DateTimeField(null=True, blank=True)
    policy_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="approved_intake_policies"
    )
    review_role = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.SETUP)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "room"], name="one_context_per_session_room"),
            models.CheckConstraint(
                condition=(
                    ~Q(status="OPEN")
                    | (
                        ~Q(roster_version="")
                        & Q(roster_confirmed_at__isnull=False)
                        & Q(roster_confirmed_by__isnull=False)
                        & ~Q(policy_version="")
                        & Q(policy_approved_at__isnull=False)
                        & Q(policy_approved_by__isnull=False)
                        & ~Q(review_role="")
                    )
                ),
                name="open_context_has_readiness_references",
            ),
        ]

    def __str__(self):
        return f"{self.session.code}/{self.room.code}"


class ContextAccess(models.Model):
    class Role(models.TextChoices):
        OPERATOR = "OPERATOR", "Vận hành"
        REVIEWER = "REVIEWER", "Xử lý ngoại lệ"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    context = models.ForeignKey(IntakeContext, on_delete=models.CASCADE, related_name="access_grants")
    role = models.CharField(max_length=10, choices=Role.choices)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "context", "role"], name="one_grant_per_user_context_role")]


class Registration(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    roster_version = models.CharField(max_length=80)
    source_key = models.CharField(max_length=120)
    candidate_code = models.CharField(max_length=64)
    display_label = models.CharField(max_length=120, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "roster_version", "source_key"], name="unique_roster_source_record")
        ]
        indexes = [models.Index(fields=["session", "roster_version", "candidate_code"], name="registration_lookup_idx")]

    def __str__(self):
        return f"{self.session.code}/{self.source_key}"


class Attempt(models.Model):
    class Status(models.TextChoices):
        STARTED = "STARTED", "Đã bắt đầu"
        IN_PROGRESS = "IN_PROGRESS", "Đang kiểm tra"
        REVIEW_PENDING = "REVIEW_PENDING", "Chờ xử lý"
        CONCLUDED = "CONCLUDED", "Đã kết luận"
        INTERRUPTED = "INTERRUPTED", "Bị gián đoạn"

    class LookupOutcome(models.TextChoices):
        PENDING = "PENDING", "Chưa tra cứu"
        FOUND = "FOUND", "Một hồ sơ"
        NOT_FOUND = "NOT_FOUND", "Không tìm thấy"
        AMBIGUOUS = "AMBIGUOUS", "Nhiều hồ sơ"
        WRONG_ROOM = "WRONG_ROOM", "Sai phòng"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context = models.ForeignKey(IntakeContext, on_delete=models.PROTECT)
    idempotency_key = models.UUIDField()
    claimed_code = models.CharField(max_length=64)
    registration = models.ForeignKey(Registration, null=True, blank=True, on_delete=models.PROTECT)
    roster_version = models.CharField(max_length=80)
    policy_version = models.CharField(max_length=80)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.STARTED)
    lookup_outcome = models.CharField(max_length=12, choices=LookupOutcome.choices, default=LookupOutcome.PENDING)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["context", "idempotency_key"], name="unique_attempt_request_per_context")]


class ReviewCase(models.Model):
    class Reason(models.TextChoices):
        NOT_FOUND = "NOT_FOUND", "Không tìm thấy hồ sơ"
        AMBIGUOUS = "AMBIGUOUS", "Hồ sơ mơ hồ"
        WRONG_ROOM = "WRONG_ROOM", "Sai phòng"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Đang mở"
        RESOLVED = "RESOLVED", "Đã xử lý"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.OneToOneField(Attempt, on_delete=models.PROTECT, related_name="review_case")
    reason = models.CharField(max_length=12, choices=Reason.choices)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.OPEN)
    assigned_role = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)


class CheckIn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ExamSession, on_delete=models.PROTECT)
    registration = models.ForeignKey(Registration, on_delete=models.PROTECT)
    attempt = models.OneToOneField(Attempt, on_delete=models.PROTECT)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["session", "registration"], name="one_effective_checkin_per_session")]


class AuditEvent(models.Model):
    class Type(models.TextChoices):
        ATTEMPT_STARTED = "ATTEMPT_STARTED", "Bắt đầu lượt"
        LOOKUP_RESOLVED = "LOOKUP_RESOLVED", "Tìm thấy hồ sơ"
        REVIEW_OPENED = "REVIEW_OPENED", "Mở ngoại lệ"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context = models.ForeignKey(IntakeContext, on_delete=models.PROTECT)
    attempt = models.ForeignKey(Attempt, on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    event_type = models.CharField(max_length=24, choices=Type.choices)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
