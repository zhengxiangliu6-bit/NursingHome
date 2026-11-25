from django.contrib import admin
from .models import PatrolCheckpoint, PatrolRoute, PatrolTask, PatrolRecord, PatrolException


@admin.register(PatrolCheckpoint)
class PatrolCheckpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'building', 'floor', 'is_active']
    list_filter = ['building', 'is_active']


@admin.register(PatrolRoute)
class PatrolRouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'estimated_duration', 'is_active']


@admin.register(PatrolTask)
class PatrolTaskAdmin(admin.ModelAdmin):
    list_display = ['task_number', 'route', 'assigned_to', 'status', 'scheduled_start']
    list_filter = ['status']


@admin.register(PatrolRecord)
class PatrolRecordAdmin(admin.ModelAdmin):
    list_display = ['task', 'checkpoint', 'scanned_at', 'is_on_time']


@admin.register(PatrolException)
class PatrolExceptionAdmin(admin.ModelAdmin):
    list_display = ['task', 'exception_type', 'severity', 'status']
    list_filter = ['severity', 'status']
