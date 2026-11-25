from django.contrib import admin
from .models import Resident, CareLevel, CareAssessment, Room, Bed


@admin.register(CareLevel)
class CareLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'daily_rate']


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'birth_date', 'status', 'care_level', 'bed']
    list_filter = ['status', 'care_level', 'gender']
    search_fields = ['name', 'id_card']


@admin.register(CareAssessment)
class CareAssessmentAdmin(admin.ModelAdmin):
    list_display = ['resident', 'assessor', 'assessment_date', 'overall_score', 'status']
    list_filter = ['status']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'building', 'floor', 'room_type', 'capacity']
    list_filter = ['building', 'room_type']


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['bed_number', 'room', 'status']
    list_filter = ['status']
