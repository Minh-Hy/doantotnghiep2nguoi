from django.contrib import admin

from .models import AuditEvent, Attempt, CheckIn, ContextAccess, ExamSession, IntakeContext, Registration, ReviewCase, Room


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ["code", "name"]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["code", "name"]


@admin.register(IntakeContext)
class IntakeContextAdmin(admin.ModelAdmin):
    list_display = ["session", "room", "status", "roster_version", "policy_version", "policy_approved_at"]
    list_filter = ["status"]


@admin.register(ContextAccess)
class ContextAccessAdmin(admin.ModelAdmin):
    list_display = ["user", "context", "role"]
    list_filter = ["role"]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["source_key", "candidate_code", "session", "room", "roster_version"]
    search_fields = ["source_key", "candidate_code"]


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Attempt)
class AttemptAdmin(ReadOnlyAdmin):
    list_display = ["id", "context", "status", "lookup_outcome", "created_at"]


@admin.register(ReviewCase)
class ReviewCaseAdmin(ReadOnlyAdmin):
    list_display = ["id", "reason", "status", "assigned_role", "created_at"]


@admin.register(CheckIn)
class CheckInAdmin(ReadOnlyAdmin):
    list_display = ["id", "session", "registration", "recorded_at"]


@admin.register(AuditEvent)
class AuditEventAdmin(ReadOnlyAdmin):
    list_display = ["id", "event_type", "context", "actor", "created_at"]
