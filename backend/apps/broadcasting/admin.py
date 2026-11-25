from django.contrib import admin
from .models import BroadcastZone, BroadcastDevice, BroadcastTask, BroadcastSchedule, BroadcastLog


@admin.register(BroadcastZone)
class BroadcastZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'building', 'floor']


@admin.register(BroadcastDevice)
class BroadcastDeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_sn', 'zone', 'status', 'volume']


@admin.register(BroadcastTask)
class BroadcastTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'broadcast_type', 'status', 'scheduled_time']
    list_filter = ['broadcast_type', 'status']


@admin.register(BroadcastSchedule)
class BroadcastScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'cron_expression', 'is_active']


@admin.register(BroadcastLog)
class BroadcastLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'action', 'device', 'timestamp']
