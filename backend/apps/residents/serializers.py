from rest_framework import serializers
from .models import Resident, CareLevel, CareAssessment, Room, Bed, AdmissionApplication, ResidentLeave, BedTransfer


class CareLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareLevel
        fields = ['id', 'name', 'level', 'description', 'daily_rate']


class BedSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)

    class Meta:
        model = Bed
        fields = ['id', 'bed_number', 'room', 'room_number', 'status']


class RoomSerializer(serializers.ModelSerializer):
    beds = BedSerializer(many=True, read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    occupancy = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'building', 'building_name', 'floor',
            'room_type', 'capacity', 'status', 'beds', 'occupancy'
        ]

    def get_occupancy(self, obj):
        return obj.beds.filter(status='occupied').count()


class ResidentSerializer(serializers.ModelSerializer):
    care_level_name = serializers.CharField(source='care_level.name', read_only=True)
    bed_info = serializers.SerializerMethodField()
    primary_nurse_name = serializers.CharField(source='primary_nurse.get_full_name', read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Resident
        fields = [
            'id', 'name', 'gender', 'birth_date', 'age', 'id_card', 'photo',
            'phone', 'admission_date', 'discharge_date', 'status', 'bed', 'bed_info',
            'care_level', 'care_level_name', 'primary_nurse', 'primary_nurse_name',
            'medical_history', 'allergy_info',
            'emergency_contact_name', 'emergency_contact_phone', 'notes'
        ]

    def get_bed_info(self, obj):
        if obj.bed:
            return str(obj.bed)
        return obj.last_bed_info or None

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        return today.year - obj.birth_date.year - (
            (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
        )


class ResidentListSerializer(serializers.ModelSerializer):
    """列表用的精简序列化器。"""
    care_level_name = serializers.CharField(source='care_level.name', read_only=True)
    bed_info = serializers.SerializerMethodField()

    class Meta:
        model = Resident
        fields = [
            'id', 'name', 'gender', 'birth_date', 'status',
            'bed', 'care_level_name', 'bed_info', 'admission_date'
        ]

    def get_bed_info(self, obj):
        if obj.bed:
            return str(obj.bed)
        return obj.last_bed_info or None


class AdmissionApplicationSerializer(serializers.ModelSerializer):
    handler_name = serializers.CharField(source='handler.get_full_name', read_only=True)
    resident_name = serializers.CharField(source='resident.name', read_only=True)
    resident_status = serializers.CharField(source='resident.status', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    reserved_bed_info = serializers.SerializerMethodField()

    class Meta:
        model = AdmissionApplication
        fields = [
            'id', 'name', 'gender', 'gender_display', 'birth_date', 'phone',
            'emergency_contact_name', 'emergency_contact_phone',
            'inquiry_source', 'notes', 'stage', 'stage_display',
            'handler', 'handler_name', 'expected_admission_date',
            'contract_signed_at', 'reserved_bed', 'reserved_bed_info',
            'resident', 'resident_name', 'resident_status', 'created_at',
        ]
        read_only_fields = ['id', 'resident', 'created_at']

    def get_reserved_bed_info(self, obj):
        return str(obj.reserved_bed) if obj.reserved_bed else None


class ResidentLeaveSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source='resident.name', read_only=True)
    handler_name = serializers.CharField(source='handler.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ResidentLeave
        fields = [
            'id', 'resident', 'resident_name', 'start_date', 'expected_return_date',
            'actual_return_date', 'reason', 'status', 'status_display',
            'handler', 'handler_name', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class CareAssessmentSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source='resident.name', read_only=True)
    assessor_name = serializers.CharField(source='assessor.get_full_name', read_only=True)
    recommended_level_name = serializers.CharField(
        source='recommended_level.name', read_only=True
    )

    class Meta:
        model = CareAssessment
        fields = [
            'id', 'resident', 'resident_name', 'assessor', 'assessor_name',
            'assessment_date', 'adl_score', 'cognitive_score', 'mobility_score',
            'overall_score', 'recommended_level', 'recommended_level_name',
            'notes', 'status'
        ]


class BedTransferSerializer(serializers.ModelSerializer):
    resident_a_name = serializers.CharField(source='resident_a.name', read_only=True)
    resident_b_name = serializers.CharField(source='resident_b.name', read_only=True, default=None)
    bed_a_info = serializers.CharField(source='bed_a.__str__', read_only=True)
    target_bed_info = serializers.CharField(source='target_bed.__str__', read_only=True)
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transfer_type = serializers.SerializerMethodField()

    class Meta:
        model = BedTransfer
        fields = [
            'id', 'resident_a', 'resident_a_name',
            'bed_a', 'bed_a_info', 'target_bed', 'target_bed_info',
            'resident_b', 'resident_b_name', 'transfer_type',
            'reason', 'status', 'status_display',
            'applicant', 'applicant_name', 'reviewer', 'reviewer_name',
            'reviewed_at', 'reject_reason', 'created_at',
        ]
        read_only_fields = [
            'id', 'bed_a', 'resident_b', 'applicant', 'reviewer',
            'reviewed_at', 'status', 'created_at',
        ]

    def get_transfer_type(self, obj):
        return '互换' if obj.resident_b_id else '调换'
