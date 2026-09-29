from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from foundation.models import ContextAssignment, ExamContext, Registration


class Command(BaseCommand):
    help = 'Tạo context/roster giả ở SETUP và gán operator đã tồn tại; không duyệt policy.'

    def add_arguments(self, parser):
        parser.add_argument('--operator', required=True, help='Username nhân sự demo đã tạo trước đó')

    @transaction.atomic
    def handle(self, *args, **options):
        operator = get_user_model().objects.filter(username=options['operator']).first()
        if operator is None:
            raise CommandError('Không tìm thấy username. Tạo user trước rồi chạy lại.')

        context, _ = ExamContext.objects.get_or_create(
            key='CTX-SIM-01',
            defaults={
                'exam_key': 'EXAM-SIM-01',
                'session_key': 'SESSION-SIM-01',
                'room_key': 'ROOM-SIM-01',
                'roster_version': 'R-SIM-001-draft',
                'policy_version': 'P-SIM-001-draft',
                'status': ExamContext.Status.SETUP,
            },
        )
        for source_key, code in [('REG-SIM-001', 'SIM001'), ('REG-SIM-002', 'SIM002')]:
            Registration.objects.get_or_create(
                context=context, source_key=source_key, roster_version='R-SIM-001-draft',
                defaults={'declared_code': code},
            )
        ContextAssignment.objects.get_or_create(
            context=context, user=operator, role=ContextAssignment.Role.OPERATOR,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Fixture {context.key}: {context.status}; operator={operator.get_username()}; '
            'policy vẫn là bản nháp.'
        ))
