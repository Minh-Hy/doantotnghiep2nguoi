from django.contrib import admin

from .models import AuditEvent, Attempt, ContextAssignment, ExamContext, Registration, ReviewCase


@admin.register(ExamContext)
class ExamContextAdmin(admin.ModelAdmin):
    list_display = ('key', 'session_key', 'room_key', 'status', 'policy_version', 'policy_approved_at')
    search_fields = ('key', 'exam_key', 'session_key', 'room_key')


@admin.register(ContextAssignment)
class ContextAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'context', 'role')


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('source_key', 'declared_code', 'context', 'roster_version')


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'context', 'actor', 'status', 'created_at')
    readonly_fields = ('id', 'context', 'actor', 'declared_code', 'roster_version', 'policy_version', 'idempotency_key', 'status', 'created_at')


@admin.register(ReviewCase)
class ReviewCaseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'reason_code', 'status', 'assigned_role')


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ('action', 'context', 'actor', 'created_at')
    readonly_fields = ('attempt', 'context', 'actor', 'action', 'metadata', 'created_at')
