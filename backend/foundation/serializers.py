from rest_framework import serializers

from .models import Attempt, ExamContext


class ContextSerializer(serializers.ModelSerializer):
    policy_approved = serializers.SerializerMethodField()

    class Meta:
        model = ExamContext
        fields = ('key', 'exam_key', 'session_key', 'room_key', 'status',
                  'roster_version', 'policy_version', 'policy_approved')

    def get_policy_approved(self, obj):
        return obj.policy_approved_at is not None


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class AttemptCreateSerializer(serializers.Serializer):
    context_key = serializers.CharField(max_length=80)
    declared_code = serializers.CharField(max_length=80, trim_whitespace=True)


class AttemptSerializer(serializers.ModelSerializer):
    context_key = serializers.CharField(source='context.key')

    class Meta:
        model = Attempt
        fields = ('id', 'context_key', 'declared_code', 'status',
                  'roster_version', 'policy_version', 'created_at')
