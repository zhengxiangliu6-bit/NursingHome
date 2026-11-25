from django.contrib import admin
from .models import CallDevice, CallRecord, CallAssignment, EscalationRule, CallEscalation


@admin.register(CallDevice)
class CallDeviceAdmin(admin.ModelAdmin):
    list_display = ['device_sn', 'device_type', 'bound_resident', 'status']
    list_filter = ['device_type', 'status']


@admin.register(CallRecord)
class CallRecordAdmin(admin.ModelAdmin):
    list_display = ['call_number', 'caller_resident', 'priority', 'status', 'call_time',
                    'current_escalation_level']
    list_filter = ['priority', 'status']
    search_fields = ['call_number']


@admin.register(CallAssignment)
class CallAssignmentAdmin(admin.ModelAdmin):
    list_display = ['call_record', 'assigned_to', 'status', 'assigned_at', 'role_at_assignment']


@admin.register(EscalationRule)
class EscalationRuleAdmin(admin.ModelAdmin):
    list_display = ['priority', 'escalation_order', 'target_role', 'timeout_seconds']
    list_filter = ['priority']
    ordering = ['priority', 'escalation_order']


@admin.register(CallEscalation)
class CallEscalationAdmin(admin.ModelAdmin):
    list_display = ['call_record', 'from_level', 'to_level', 'target_role', 'escalated_at', 'reason']
    list_filter = ['target_role', 'reason']
