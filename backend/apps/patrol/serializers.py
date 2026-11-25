from rest_framework import serializers
from .models import (
    PatrolCheckpoint, PatrolRoute, PatrolRouteCheckpoint,
    PatrolTask, PatrolRecord, PatrolException,
)


class PatrolCheckpointSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)

    class Meta:
        model = PatrolCheckpoint
        fields = [
            'id', 'name', 'code', 'building', 'building_name', 'floor',
            'area', 'location_x', 'location_y', 'description', 'is_active'
        ]


class PatrolRouteCheckpointSerializer(serializers.ModelSerializer):
    checkpoint_detail = PatrolCheckpointSerializer(source='checkpoint', read_only=True)

    class Meta:
        model = PatrolRouteCheckpoint
        fields = ['id', 'checkpoint', 'checkpoint_detail', 'sequence', 'expected_duration']


class PatrolRouteSerializer(serializers.ModelSerializer):
    checkpoint_list = PatrolRouteCheckpointSerializer(
        source='patrolroutecheckpoint_set', many=True, read_only=True
    )

    class Meta:
        model = PatrolRoute
        fields = [
            'id', 'name', 'description', 'estimated_duration',
            'is_active', 'checkpoint_list'
        ]


class PatrolRecordSerializer(serializers.ModelSerializer):
    checkpoint_name = serializers.CharField(source='checkpoint.name', read_only=True)

    class Meta:
        model = PatrolRecord
        fields = [
            'id', 'task', 'checkpoint', 'checkpoint_name', 'scanned_at',
            'is_on_time', 'photo', 'notes', 'location_x', 'location_y'
        ]


class PatrolExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatrolException
        fields = [
            'id', 'task', 'checkpoint', 'exception_type', 'description',
            'photo', 'severity', 'status', 'handled_by'
        ]


class PatrolTaskSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(source='route.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    records = PatrolRecordSerializer(many=True, read_only=True)
    exceptions = PatrolExceptionSerializer(many=True, read_only=True)

    class Meta:
        model = PatrolTask
        fields = [
            'id', 'task_number', 'route', 'route_name', 'assigned_to',
            'assigned_to_name', 'scheduled_start', 'scheduled_end',
            'actual_start', 'actual_end', 'status', 'records', 'exceptions'
        ]
        read_only_fields = ['task_number']


class PatrolTaskListSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(source='route.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = PatrolTask
        fields = [
            'id', 'task_number', 'route_name', 'assigned_to_name',
            'scheduled_start', 'scheduled_end', 'status', 'progress'
        ]

    def get_progress(self, obj):
        total = obj.route.checkpoints.count()
        scanned = obj.records.count()
        return f'{scanned}/{total}'
