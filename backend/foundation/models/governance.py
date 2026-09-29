import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class PolicyVersion(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Nháp'
        APPROVED = 'APPROVED', 'Đã duyệt'
        RETIRED = 'RETIRED', 'Hết hiệu lực'

    context = models.ForeignKey('foundation.ExamContext', on_delete=models.PROTECT, related_name='policy_versions')
    version = models.CharField(max_length=80)
    schema_version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    rules = models.JSONField(default=dict, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    approved_at = models.DateTimeField(null=True, blank=True)
    source_note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['context', 'version'], name='one_policy_version'),
            models.CheckConstraint(
                condition=~Q(status='APPROVED') | (Q(approved_by__isnull=False) & Q(approved_at__isnull=False)),
                name='approved_policy_has_actor_and_time',
            ),
        ]

    def __str__(self):
        return f'{self.context_id}:{self.version}'


class AssetReference(models.Model):
    """Opaque pointer to protected storage; never contains face bytes or embeddings."""

    class Kind(models.TextChoices):
        FACE_REFERENCE = 'FACE_REFERENCE', 'Ảnh tham chiếu'
        VERIFICATION = 'VERIFICATION', 'Bằng chứng xác minh'
        MODEL = 'MODEL', 'Model AI'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=24, choices=Kind.choices)
    storage_key = models.CharField(max_length=240, unique=True)
    sha256 = models.CharField(max_length=64)
    candidate = models.ForeignKey('foundation.Candidate', null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.kind}:{self.id}'
