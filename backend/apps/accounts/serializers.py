from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Role, StaffProfile, FamilyRelation, StaffSchedule


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description']


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.get_name_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone', 'email', 'first_name', 'last_name',
            'avatar', 'role', 'role_name', 'department', 'employee_id',
            'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'phone', 'email', 'first_name', 'last_name',
            'role', 'department', 'employee_id'
        ]
        read_only_fields = ['id']

    def validate_employee_id(self, value):
        # 空字符串转 None，避免 unique 约束冲突
        return value if value else None

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value


class StaffProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = StaffProfile
        fields = ['id', 'user', 'user_name', 'title', 'certification', 'assigned_building', 'on_duty']


class StaffScheduleSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    building_name = serializers.CharField(source='building.name', read_only=True)
    shift_display = serializers.CharField(source='get_shift_display', read_only=True)

    class Meta:
        model = StaffSchedule
        fields = [
            'id', 'staff', 'staff_name', 'date', 'shift', 'shift_display',
            'building', 'building_name', 'is_on_leave', 'notes',
        ]

    def get_staff_name(self, obj):
        return obj.staff.get_full_name() or obj.staff.username


class FamilyRelationSerializer(serializers.ModelSerializer):
    family_user_name = serializers.CharField(source='family_user.get_full_name', read_only=True)
    resident_name = serializers.CharField(source='resident.name', read_only=True)

    class Meta:
        model = FamilyRelation
        fields = [
            'id', 'family_user', 'family_user_name', 'resident', 'resident_name',
            'relationship', 'is_primary_contact', 'can_receive_alerts'
        ]
