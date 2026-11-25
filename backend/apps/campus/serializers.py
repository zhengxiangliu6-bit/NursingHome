from rest_framework import serializers
from .models import Building, Area, Device, DeviceMaintenanceLog, Notice


class BuildingSerializer(serializers.ModelSerializer):
    room_count = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = ['id', 'name', 'code', 'address', 'floors', 'description', 'floor_plan_image', 'room_count']

    def get_room_count(self, obj):
        return obj.rooms.count()


class AreaSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'building', 'building_name', 'floor', 'area_type', 'map_coordinates']


class DeviceMaintenanceLogSerializer(serializers.ModelSerializer):
    maintainer_name = serializers.CharField(source='maintained_by.get_full_name', read_only=True)

    class Meta:
        model = DeviceMaintenanceLog
        fields = [
            'id', 'device', 'maintained_by', 'maintainer_name',
            'maintenance_type', 'description', 'result', 'cost', 'created_at'
        ]


class DeviceSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    area_name = serializers.CharField(source='area.name', read_only=True)

    class Meta:
        model = Device
        fields = [
            'id', 'device_sn', 'name', 'device_category', 'model_name',
            'manufacturer', 'building', 'building_name', 'area', 'area_name',
            'ip_address', 'status', 'installed_at', 'last_maintenance', 'config'
        ]


class NoticeSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content', 'notice_type', 'target_roles',
            'is_published', 'published_at', 'expires_at',
            'author', 'author_name', 'attachments', 'created_at'
        ]
