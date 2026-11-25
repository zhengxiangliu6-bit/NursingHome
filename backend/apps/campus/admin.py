from django.contrib import admin
from .models import Building, Area, Device, DeviceMaintenanceLog, Notice


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'floors']


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'building', 'floor', 'area_type']
    list_filter = ['area_type', 'building']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_sn', 'device_category', 'status', 'building']
    list_filter = ['device_category', 'status']
    search_fields = ['name', 'device_sn']


@admin.register(DeviceMaintenanceLog)
class DeviceMaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ['device', 'maintenance_type', 'result', 'created_at']


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'notice_type', 'is_published', 'published_at']
    list_filter = ['notice_type', 'is_published']
