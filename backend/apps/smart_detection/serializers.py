from rest_framework import serializers
from .models import (
    DetectionDevice, VitalSign, FallAlert, HealthCheckRecord, PositionRecord,
    MQTTDeviceMapping, AlertRule, Alert, AlertHandleLog,
)


class DetectionDeviceSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source='bound_resident.name', read_only=True)

    class Meta:
        model = DetectionDevice
        fields = [
            'id', 'device_sn', 'device_type', 'bound_resident', 'resident_name',
            'location', 'status', 'battery_level', 'last_heartbeat'
        ]


class VitalSignSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source='resident.name', read_only=True)

    class Meta:
        model = VitalSign
        fields = [
            'id', 'resident', 'resident_name', 'device', 'measured_at',
            'heart_rate', 'systolic_bp', 'diastolic_bp', 'blood_oxygen',
            'temperature', 'respiratory_rate', 'is_abnormal', 'abnormal_items'
        ]


class FallAlertSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source='resident.name', read_only=True)
    handler_name = serializers.CharField(source='handled_by.get_full_name', read_only=True)

    class Meta:
        model = FallAlert
        fields = [
            'id', 'resident', 'resident_name', 'device', 'alert_time',
            'location_x', 'location_y', 'floor', 'location_description',
            'severity', 'status', 'handled_by', 'handler_name', 'handle_time', 'notes'
        ]


class HealthCheckRecordSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source='resident.name', read_only=True)
    checker_name = serializers.CharField(source='checked_by.get_full_name', read_only=True)

    class Meta:
        model = HealthCheckRecord
        fields = [
            'id', 'resident', 'resident_name', 'checked_by', 'checker_name',
            'check_time', 'check_type', 'vital_sign',
            'mental_status', 'skin_condition', 'appetite', 'sleep_quality', 'notes'
        ]


class PositionRecordSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source='resident.name', read_only=True)

    class Meta:
        model = PositionRecord
        fields = [
            'id', 'resident', 'resident_name', 'device', 'timestamp',
            'x', 'y', 'floor', 'area', 'is_in_restricted_zone'
        ]


# ==================== Phase 2 新增序列化器 ====================


class MQTTDeviceMappingSerializer(serializers.ModelSerializer):
    device_sn = serializers.CharField(source='detection_device.device_sn', read_only=True)
    device_type = serializers.CharField(source='detection_device.device_type', read_only=True)

    class Meta:
        model = MQTTDeviceMapping
        fields = [
            'id', 'detection_device', 'device_sn', 'device_type',
            'mqtt_client_id', 'mqtt_topic', 'protocol_type', 'parser_config'
        ]


class AlertRuleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True, default=''
    )

    class Meta:
        model = AlertRule
        fields = [
            'id', 'name', 'description', 'metric', 'operator', 'threshold',
            'duration', 'severity', 'enabled', 'cooldown',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['created_by']


class AlertHandleLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(
        source='operator.get_full_name', read_only=True, default=''
    )

    class Meta:
        model = AlertHandleLog
        fields = [
            'id', 'action', 'from_status', 'to_status',
            'operator', 'operator_name', 'remark', 'created_at'
        ]


class AlertSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source='resident.name', read_only=True, default='')
    device_sn = serializers.CharField(source='device.device_sn', read_only=True, default='')
    rule_name = serializers.CharField(source='rule.name', read_only=True, default='')
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name', read_only=True, default=''
    )
    processed_by_name = serializers.CharField(
        source='processed_by.get_full_name', read_only=True, default=''
    )
    handle_logs = AlertHandleLogSerializer(many=True, read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'alert_type', 'severity', 'status', 'title', 'content',
            'resident', 'resident_name', 'device', 'device_sn',
            'rule', 'rule_name',
            'location_description', 'alert_time',
            'assigned_to', 'assigned_to_name', 'assigned_at',
            'processed_by', 'processed_by_name', 'processed_at',
            'resolution', 'extra_data',
            'handle_logs', 'created_at'
        ]
        read_only_fields = ['status', 'assigned_at', 'processed_at']


class AlertListSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source='resident.name', read_only=True, default='')
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name', read_only=True, default=''
    )

    class Meta:
        model = Alert
        fields = [
            'id', 'alert_type', 'severity', 'status', 'title',
            'resident', 'resident_name', 'location_description',
            'alert_time', 'assigned_to_name'
        ]
