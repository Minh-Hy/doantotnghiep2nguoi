from django.db import transaction

from .models import Attempt, AuditEvent, ContextAssignment, ExamContext


class AttemptConflict(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def start_attempt(*, actor, context: ExamContext, declared_code: str, idempotency_key: str):
    with transaction.atomic():
        context = ExamContext.objects.select_for_update().get(pk=context.pk)
        existing = Attempt.objects.filter(
            actor=actor, context=context, idempotency_key=idempotency_key,
        ).first()
        if existing:
            if existing.declared_code != declared_code:
                raise AttemptConflict('IDEMPOTENCY_CONFLICT')
            return existing, False

        if not ContextAssignment.objects.filter(
            user=actor, context=context, role=ContextAssignment.Role.OPERATOR,
        ).exists():
            raise AttemptConflict('OPERATOR_REQUIRED')
        if context.status != ExamContext.Status.OPEN or context.policy_approved_at is None:
            raise AttemptConflict('CONTEXT_NOT_READY')

        attempt = Attempt.objects.create(
            actor=actor,
            context=context,
            declared_code=declared_code,
            idempotency_key=idempotency_key,
            roster_version=context.roster_version,
            policy_version=context.policy_version,
        )
        AuditEvent.objects.create(
            attempt=attempt, context=context, actor=actor,
            action='ATTEMPT_STARTED',
            metadata={'roster_version': context.roster_version, 'policy_version': context.policy_version},
        )
        return attempt, True
