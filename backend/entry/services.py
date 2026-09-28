from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from .models import Attempt, AuditEvent, ContextAccess, IntakeContext, Registration, ReviewCase


class ContextNotOpen(Exception):
    pass


class ContextAccessDenied(Exception):
    pass


class IdempotencyConflict(Exception):
    pass


@dataclass(frozen=True)
class StartAttemptResult:
    attempt: Attempt
    created: bool


def can_start_attempt(user, context: IntakeContext) -> bool:
    return user.is_superuser or ContextAccess.objects.filter(
        user=user, context=context, role=ContextAccess.Role.OPERATOR
    ).exists()


@transaction.atomic
def start_attempt(*, user, context: IntakeContext, candidate_code: str, idempotency_key: UUID) -> StartAttemptResult:
    if not can_start_attempt(user, context):
        raise ContextAccessDenied

    existing = Attempt.objects.filter(context=context, idempotency_key=idempotency_key).first()
    if existing:
        if existing.claimed_code != candidate_code:
            raise IdempotencyConflict
        return StartAttemptResult(existing, False)

    if context.status != IntakeContext.Status.OPEN:
        raise ContextNotOpen

    attempt, created = Attempt.objects.get_or_create(
        context=context,
        idempotency_key=idempotency_key,
        defaults={
            "claimed_code": candidate_code,
            "roster_version": context.roster_version,
            "policy_version": context.policy_version,
            "created_by": user,
        },
    )
    if not created:
        if attempt.claimed_code != candidate_code:
            raise IdempotencyConflict
        return StartAttemptResult(attempt, False)

    AuditEvent.objects.create(
        context=context, attempt=attempt, actor=user, event_type=AuditEvent.Type.ATTEMPT_STARTED
    )
    matches = list(
        Registration.objects.filter(
            session=context.session,
            roster_version=context.roster_version,
            candidate_code=candidate_code,
        )[:2]
    )
    if not matches:
        outcome = Attempt.LookupOutcome.NOT_FOUND
        reason = ReviewCase.Reason.NOT_FOUND
    elif len(matches) > 1:
        outcome = Attempt.LookupOutcome.AMBIGUOUS
        reason = ReviewCase.Reason.AMBIGUOUS
    elif matches[0].room_id != context.room_id:
        attempt.registration = matches[0]
        outcome = Attempt.LookupOutcome.WRONG_ROOM
        reason = ReviewCase.Reason.WRONG_ROOM
    else:
        attempt.registration = matches[0]
        attempt.lookup_outcome = Attempt.LookupOutcome.FOUND
        attempt.status = Attempt.Status.IN_PROGRESS
        attempt.save(update_fields=["registration", "lookup_outcome", "status"])
        AuditEvent.objects.create(
            context=context, attempt=attempt, actor=user, event_type=AuditEvent.Type.LOOKUP_RESOLVED
        )
        return StartAttemptResult(attempt, True)

    attempt.lookup_outcome = outcome
    attempt.status = Attempt.Status.REVIEW_PENDING
    attempt.save(update_fields=["registration", "lookup_outcome", "status"])
    ReviewCase.objects.create(attempt=attempt, reason=reason, assigned_role=context.review_role)
    AuditEvent.objects.create(
        context=context,
        attempt=attempt,
        actor=user,
        event_type=AuditEvent.Type.REVIEW_OPENED,
        details={"reason": reason},
    )
    return StartAttemptResult(attempt, True)
