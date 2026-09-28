from rest_framework import serializers

from .models import Attempt, IntakeContext


class StartAttemptSerializer(serializers.Serializer):
    context_id = serializers.IntegerField(min_value=1)
    candidate_code = serializers.CharField(max_length=64, trim_whitespace=True)
    idempotency_key = serializers.UUIDField()


class ContextSerializer(serializers.ModelSerializer):
    session_code = serializers.CharField(source="session.code", read_only=True)
    room_code = serializers.CharField(source="room.code", read_only=True)

    class Meta:
        model = IntakeContext
        fields = ["id", "session_code", "room_code", "status"]


class AttemptSerializer(serializers.ModelSerializer):
    context_id = serializers.IntegerField(read_only=True)
    next_action = serializers.SerializerMethodField()
    review_reason = serializers.SerializerMethodField()

    class Meta:
        model = Attempt
        fields = [
            "id",
            "context_id",
            "status",
            "lookup_outcome",
            "next_action",
            "review_reason",
            "created_at",
        ]

    def get_next_action(self, obj):
        if obj.status == Attempt.Status.IN_PROGRESS:
            return "VERIFY_IDENTITY"
        if obj.status == Attempt.Status.REVIEW_PENDING:
            return "REVIEW"
        return "NONE"

    def get_review_reason(self, obj):
        case = getattr(obj, "review_case", None)
        return case.reason if case else None
