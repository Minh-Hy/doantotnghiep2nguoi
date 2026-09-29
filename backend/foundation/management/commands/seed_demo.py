from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from foundation.models import (
    Candidate, ContextAssignment, Course, Exam, ExamContext, ExamSession,
    PolicyVersion, Registration, Room, RosterBatch,
)


class Command(BaseCommand):
    help = 'Tạo context/roster giả ở SETUP và gán operator đã tồn tại; không duyệt policy.'

    def add_arguments(self, parser):
        parser.add_argument('--operator', required=True, help='Username nhân sự demo đã tạo trước đó')

    @transaction.atomic
    def handle(self, *args, **options):
        operator = get_user_model().objects.filter(username=options['operator']).first()
        if operator is None:
            raise CommandError('Không tìm thấy username. Tạo user trước rồi chạy lại.')

        course, _ = Course.objects.get_or_create(
            code='COURSE-SIM-01', defaults={'title': 'Học phần giả lập'},
        )
        exam, _ = Exam.objects.get_or_create(
            key='EXAM-SIM-01', defaults={'title': 'Kỳ thi học phần giả lập', 'course': course},
        )
        if exam.course_id is None:
            exam.course = course
            exam.save(update_fields=['course'])
        session, _ = ExamSession.objects.get_or_create(
            exam=exam, key='SESSION-SIM-01', defaults={'label': 'Ca thi giả lập'},
        )
        room, _ = Room.objects.get_or_create(
            key='ROOM-SIM-01', defaults={'label': 'Phòng giả lập'},
        )
        context, _ = ExamContext.objects.get_or_create(
            key='CTX-SIM-01',
            defaults={
                'exam_key': 'EXAM-SIM-01',
                'session_key': 'SESSION-SIM-01',
                'room_key': 'ROOM-SIM-01',
                'roster_version': 'R-SIM-001-draft',
                'policy_version': 'P-SIM-001-draft',
                'status': ExamContext.Status.SETUP,
                'session': session,
                'room': room,
            },
        )
        if context.session_id is None or context.room_id is None:
            context.session = session
            context.room = room
            context.save(update_fields=['session', 'room'])
        roster, _ = RosterBatch.objects.get_or_create(
            context=context, version='R-SIM-001-draft',
            defaults={'source_format': RosterBatch.SourceFormat.DEMO},
        )
        policy, _ = PolicyVersion.objects.get_or_create(
            context=context, version='P-SIM-001-draft',
        )
        updates = []
        if context.active_roster_id is None:
            context.active_roster = roster
            updates.append('active_roster')
        if context.active_policy_id is None:
            context.active_policy = policy
            updates.append('active_policy')
        if updates:
            context.save(update_fields=updates)
        for source_key, code in [('REG-SIM-001', 'SIM001'), ('REG-SIM-002', 'SIM002')]:
            exists = Registration.objects.filter(
                context=context, source_key=source_key, roster_version='R-SIM-001-draft',
            ).exists()
            if not exists:
                candidate, _ = Candidate.objects.get_or_create(
                    key=f'SIM-CAND-{source_key}', defaults={'is_synthetic': True},
                )
                Registration.objects.create(
                    context=context, source_key=source_key, roster_version='R-SIM-001-draft',
                    declared_code=code, candidate=candidate, roster_batch=roster,
                )
        ContextAssignment.objects.get_or_create(
            context=context, user=operator, role=ContextAssignment.Role.OPERATOR,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Fixture {context.key}: {context.status}; operator={operator.get_username()}; '
            'policy vẫn là bản nháp.'
        ))
