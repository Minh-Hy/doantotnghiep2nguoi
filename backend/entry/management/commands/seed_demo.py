from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from entry.models import ContextAccess, ExamSession, IntakeContext, Registration, Room


class Command(BaseCommand):
    help = "Create a synthetic T-018 exam context in SETUP without approving policy."

    def add_arguments(self, parser):
        parser.add_argument("--operator", required=True, help="Existing username assigned as demo operator")

    @transaction.atomic
    def handle(self, *args, **options):
        user = get_user_model().objects.filter(username=options["operator"], is_active=True).first()
        if user is None:
            raise CommandError("Active user not found. Create the account first.")

        session, _ = ExamSession.objects.get_or_create(
            code="DEMO-T018-HOC-PHAN",
            defaults={"name": "Ca thi học phần giả lập T-018"},
        )
        room, _ = Room.objects.get_or_create(code="DEMO-P101", defaults={"name": "Phòng giả lập P101"})
        context, _ = IntakeContext.objects.get_or_create(session=session, room=room)
        ContextAccess.objects.get_or_create(user=user, context=context, role=ContextAccess.Role.OPERATOR)
        for source_key, candidate_code in [("demo-001", "DEMO-001"), ("demo-002", "DEMO-002")]:
            Registration.objects.get_or_create(
                session=session,
                roster_version="demo-v1",
                source_key=source_key,
                defaults={"room": room, "candidate_code": candidate_code},
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Prepared synthetic context {context} in {context.status}; no check-in or policy approval was created."
            )
        )
