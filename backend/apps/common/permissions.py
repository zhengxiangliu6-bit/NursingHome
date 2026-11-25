from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """允许管理员及超级管理员访问。"""
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and request.user.role
            and request.user.role.name in ('super_admin', 'admin')
        )


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and request.user.role
            and request.user.role.name in ('super_admin', 'admin', 'doctor')
        )


class IsNurseOrAbove(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and request.user.role
            and request.user.role.name in ('super_admin', 'admin', 'doctor', 'nurse')
        )


class IsStaff(BasePermission):
    """允许所有工作人员（非家属）访问。"""
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and request.user.role
            and request.user.role.name in (
                'super_admin', 'admin', 'doctor', 'nurse', 'care_worker'
            )
        )


class IsFamilyMember(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and request.user.role
            and request.user.role.name == 'family_member'
        )
