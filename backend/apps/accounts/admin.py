from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, StaffProfile, FamilyRelation


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'description']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'phone', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('phone', 'avatar', 'role', 'department', 'employee_id')}),
    )


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'on_duty']


@admin.register(FamilyRelation)
class FamilyRelationAdmin(admin.ModelAdmin):
    list_display = ['family_user', 'resident', 'relationship', 'is_primary_contact']
