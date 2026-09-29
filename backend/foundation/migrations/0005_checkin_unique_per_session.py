import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ('foundation', '0004_alter_examcontext_room_alter_examcontext_session_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='checkin',
            name='one_effective_checkin_per_candidate_context',
        ),
        migrations.AddField(
            model_name='checkin',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='foundation.examsession'),
        ),
        migrations.AddConstraint(
            model_name='checkin',
            constraint=models.UniqueConstraint(
                fields=['session', 'candidate'],
                condition=Q(status__in=['RECORDED', 'DISPUTED']),
                name='one_effective_checkin_per_candidate_session',
            ),
        ),
    ]
