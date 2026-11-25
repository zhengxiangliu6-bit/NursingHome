from django.contrib import admin
from .models import (
    DetectionDevice, VitalSign, FallAlert, HealthCheckRecord, PositionRecord,
    MQTTDeviceMapping, AlertRule, Alert, AlertHandleLog,
)


@admin.register(DetectionDevice)
class DetectionDeviceAdmin(admin.ModelAdmin):
    list_display = ['device_sn', 'device_type', 'bound_resident', 'status', 'battery_level']
    list_filter = ['device_type', 'status']


@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ['resident', 'measured_at', 'heart_rate', 'blood_oxygen', 'temperature', 'is_abnormal']
    list_filter = ['is_abnormal']


@admin.register(FallAlert)
class FallAlertAdmin(admin.ModelAdmin):
    list_display = ['resident', 'alert_time', 'severity', 'status', 'handled_by']
    list_filter = ['severity', 'status']


@admin.register(HealthCheckRecord)
class HealthCheckRecordAdmin(admin.ModelAdmin):
    list_display = ['resident', 'checked_by', 'check_time', 'check_type']


@admin.register(PositionRecord)
class PositionRecordAdmin(admin.ModelAdmin):
    list_display = ['resident', 'timestamp', 'floor', 'is_in_restricted_zone']


@admin.register(MQTTDeviceMapping)
class MQTTDeviceMappingAdmin(admin.ModelAdmin):
    list_display = ['detection_device', 'mqtt_topic', 'protocol_type']
    list_filter = ['protocol_type']


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric', 'operator', 'threshold', 'duration', 'severity', 'enabled']
    list_filter = ['metric', 'severity', 'enabled']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'severity', 'status', 'resident', 'alert_time']
    list_filter = ['alert_type', 'severity', 'status']
    search_fields = ['title']


@admin.register(AlertHandleLog)
class AlertHandleLogAdmin(admin.ModelAdmin):
    list_display = ['alert', 'action', 'from_status', 'to_status', 'operator', 'created_at']
