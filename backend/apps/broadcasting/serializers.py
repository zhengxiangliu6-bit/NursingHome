from rest_framework import serializers
from .models import BroadcastZone, BroadcastDevice, BroadcastTask, BroadcastSchedule, BroadcastLog


class BroadcastZoneSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    device_count = serializers.SerializerMethodField()

    class Meta:
        model = BroadcastZone
        fields = ['id', 'name', 'building', 'building_name', 'floor', 'description', 'device_count']

    def get_device_count(self, obj):
        return obj.devices.count()


class BroadcastDeviceSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)

    class Meta:
        model = BroadcastDevice
        fields = ['id', 'device_sn', 'name', 'zone', 'zone_name', 'status', 'volume']


class BroadcastTaskSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by_user.get_full_name', read_only=True)

    class Meta:
        model = BroadcastTask
        fields = [
            'id', 'title', 'broadcast_type', 'source_type', 'content_text',
            'audio_file', 'zones', 'priority', 'status', 'scheduled_time',
            'started_at', 'ended_at', 'created_by_user', 'created_by_name'
        ]


class BroadcastScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastSchedule
        fields = [
            'id', 'name', 'cron_expression', 'source_type', 'content_text',
            'audio_file', 'zones', 'is_active'
        ]


class BroadcastLogSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = BroadcastLog
        fields = ['id', 'task', 'task_title', 'action', 'device', 'timestamp', 'details']
