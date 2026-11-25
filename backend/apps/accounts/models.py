import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.common.models import BaseModel


class Role(models.Model):
    """角色表，用于RBAC权限控制。"""
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    DOCTOR = 'doctor'
    NURSE = 'nurse'
    CARE_WORKER = 'care_worker'
    FAMILY_MEMBER = 'family_member'

    ROLE_CHOICES = [
        (SUPER_ADMIN, '超级管理员'),
        (ADMIN, '管理员'),
        (DOCTOR, '医生'),
        (NURSE, '护士'),
        (CARE_WORKER, '护工'),
        (FAMILY_MEMBER, '家属'),
    ]

    name = models.CharField('角色标识', max_length=30, unique=True, choices=ROLE_CHOICES)
    display_name = models.CharField('角色名称', max_length=50, blank=True)
    description = models.TextField('描述', blank=True)
    permissions = models.JSONField('权限配置', default=dict, blank=True)

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """自定义用户模型。"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField('手机号', max_length=20, unique=True)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name='users',
        verbose_name='角色', null=True
    )
    department = models.CharField('部门', max_length=100, blank=True)
    employee_id = models.CharField('工号', max_length=50, blank=True, unique=True, null=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.role})'


class StaffProfile(BaseModel):
    """员工扩展信息。"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='staff_profile',
        verbose_name='用户'
    )
    title = models.CharField('职称', max_length=50, blank=True)
    certification = models.CharField('资质证书', max_length=100, blank=True)
    assigned_building = models.ForeignKey(
        'campus.Building', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='所属楼栋'
    )
    on_duty = models.BooleanField('是否值班', default=False)

    class Meta:
        verbose_name = '员工信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.title}'


class FamilyRelation(BaseModel):
    """家属与老人的关联关系。"""
    family_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='family_relations',
        verbose_name='家属用户'
    )
    resident = models.ForeignKey(
        'residents.Resident', on_delete=models.CASCADE,
        related_name='family_relations', verbose_name='关联老人'
    )
    relationship = models.CharField('关系', max_length=20)  # 子女/配偶/其他
    is_primary_contact = models.BooleanField('是否主要联系人', default=False)
    can_receive_alerts = models.BooleanField('是否接收告警', default=True)

    class Meta:
        verbose_name = '家属关系'
        verbose_name_plural = verbose_name
        unique_together = ['family_user', 'resident']

    def __str__(self):
        return f'{self.family_user} - {self.resident} ({self.relationship})'


class StaffSchedule(BaseModel):
    """员工排班。"""
    SHIFT_CHOICES = [
        ('morning', '早班 06:00-14:00'),
        ('afternoon', '午班 14:00-22:00'),
        ('night', '夜班 22:00-06:00'),
    ]

    staff = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='schedules', verbose_name='员工'
    )
    date = models.DateField('排班日期')
    shift = models.CharField('班次', max_length=20, choices=SHIFT_CHOICES)
    building = models.ForeignKey(
        'campus.Building', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='所属楼栋'
    )
    is_on_leave = models.BooleanField('请假', default=False)
    notes = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '排班'
        verbose_name_plural = verbose_name
        unique_together = ['staff', 'date', 'shift']
        ordering = ['date', 'shift']

    def __str__(self):
        return f'{self.staff} {self.date} {self.get_shift_display()}'
