from rest_framework import serializers
from .models import CallDevice, CallRecord, CallAssignment, EscalationRule, CallEscalation


class CallDeviceSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source='bound_resident.name', read_only=True)

    class Meta:
        model = CallDevice
        fields = [
            'id', 'device_sn', 'device_type', 'location', 'bound_resident',
            'resident_name', 'status'
        ]


class CallAssignmentSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    class Meta:
        model = CallAssignment
        fields = [
            'id', 'call_record', 'assigned_to', 'assigned_to_name',
            'assigned_at', 'responded_at', 'status', 'role_at_assignment', 'notes'
        ]


class CallEscalationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallEscalation
        fields = [
            'id', 'from_level', 'to_level', 'target_role',
            'escalated_at', 'reason'
        ]


class CallRecordSerializer(serializers.ModelSerializer):
    caller_name = serializers.CharField(source='caller_resident.name', read_only=True)
    assignments = CallAssignmentSerializer(many=True, read_only=True)
    escalations = CallEscalationSerializer(many=True, read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True, default='')

    class Meta:
        model = CallRecord
        fields = [
            'id', 'call_number', 'caller_resident', 'caller_name', 'call_device',
            'priority', 'status', 'call_time', 'accept_time', 'resolve_time',
            'response_duration', 'location_description', 'notes',
            'current_escalation_level', 'building', 'building_name',
            'assignments', 'escalations'
        ]
        read_only_fields = ['call_number', 'call_time', 'response_duration',
                           'current_escalation_level']


class CallRecordListSerializer(serializers.ModelSerializer):
    caller_name = serializers.CharField(source='caller_resident.name', read_only=True)

    class Meta:
        model = CallRecord
        fields = [
            'id', 'call_number', 'caller_name', 'priority', 'status',
            'call_time', 'response_duration', 'location_description',
            'current_escalation_level'
        ]


class EscalationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscalationRule
        fields = [
            'id', 'priority', 'escalation_order', 'target_role', 'timeout_seconds'
        ]
