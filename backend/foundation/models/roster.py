import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class Candidate(models.Model):
    """Pseudonymous identity; no face image or embedding is stored here."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=120, unique=True)
    display_name = models.CharField(max_length=160, blank=True)
    is_synthetic = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.key


class RosterBatch(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Nháp'
        ACTIVE = 'ACTIVE', 'Có hiệu lực'
        SUPERSEDED = 'SUPERSEDED', 'Đã thay thế'

    class SourceFormat(models.TextChoices):
        DEMO = 'DEMO', 'Dữ liệu giả'
        CSV = 'CSV', 'CSV'
        XLSX = 'XLSX', 'Excel'

    context = models.ForeignKey('foundation.ExamContext', on_delete=models.PROTECT, related_name='roster_batches')
    version = models.CharField(max_length=80)
    format_version = models.PositiveIntegerField(default=1)
    source_format = models.CharField(max_length=8, choices=SourceFormat.choices, default=SourceFormat.DEMO)
    source_sha256 = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    imported_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    imported_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['context', 'version'], name='one_roster_batch_version'),
            models.UniqueConstraint(fields=['context'], condition=Q(status='ACTIVE'), name='one_active_roster_per_context'),
        ]

    def __str__(self):
        return f'{self.context_id}:{self.version}'


class RosterImportIssue(models.Model):
    """Per-row import error without retaining the row's personal data."""

    batch = models.ForeignKey(RosterBatch, on_delete=models.PROTECT, related_name='issues')
    row_number = models.PositiveIntegerField()
    error_code = models.CharField(max_length=80)
    source_key_sha256 = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['batch', 'row_number'], name='roster_issue_row_idx')]
