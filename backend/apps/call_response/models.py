import uuid
from django.db import models
from apps.common.models import BaseModel


class CallDevice(BaseModel):
    """呼叫设备。"""
    DEVICE_TYPE_CHOICES = [
        ('bedside', '床头呼叫器'),
        ('pendant', '随身挂件'),
        ('wall', '墙壁按钮'),
    ]

    device_sn = models.CharField('设备序列号', max_length=100, unique=True)
    device_type = models.CharField('设备类型', max_length=30, choices=DEVICE_TYPE_CHOICES)
    location = models.ForeignKey(
        'campus.Area', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='位置'
    )
    bound_resident = models.ForeignKey(
        'residents.Resident', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='绑定老人'
    )
    status = models.CharField('状态', max_length=20, default='online')  # online/offline/fault

    class Meta:
        verbose_name = '呼叫设备'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.get_device_type_display()} ({self.device_sn})'


class CallRecord(BaseModel):
    """呼叫记录。"""
    PRIORITY_CHOICES = [
        ('emergency', '紧急呼叫'),
        ('normal', '普通呼叫'),
        ('consultation', '咨询呼叫'),
    ]
    STATUS_CHOICES = [
        ('pending', '待响应'),
        ('accepted', '已接受'),
        ('in_progress', '处理中'),
        ('resolved', '已解决'),
        ('cancelled', '已取消'),
        ('timeout', '超时未响应'),
    ]

    call_number = models.CharField('呼叫编号', max_length=30, unique=True)
    caller_resident = models.ForeignKey(
        'residents.Resident', on_delete=models.CASCADE, verbose_name='呼叫老人'
    )
    call_device = models.ForeignKey(
        CallDevice, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='呼叫设备'
    )
    priority = models.CharField('优先级', max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    call_time = models.DateTimeField('呼叫时间', auto_now_add=True)
    accept_time = models.DateTimeField('接受时间', null=True, blank=True)
    resolve_time = models.DateTimeField('解决时间', null=True, blank=True)
    response_duration = models.IntegerField('响应时长(秒)', null=True, blank=True)
    location_description = models.CharField('位置描述', max_length=200, blank=True)
    notes = models.TextField('备注', blank=True)
    # Phase 2: 升级相关字段
    current_escalation_level = models.PositiveIntegerField('当前升级级别', default=0)
    escalation_task_id = models.CharField('升级任务ID', max_length=255, blank=True,
        help_text='Celery task ID，用于取消待执行的升级任务')
    building = models.ForeignKey(
        'campus.Building', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='所属楼栋', help_text='反范式存储，加速WebSocket路由'
    )

    class Meta:
        verbose_name = '呼叫记录'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.call_number:
            self.call_number = f'CALL-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.call_number} - {self.caller_resident}'


class CallAssignment(BaseModel):
    """呼叫分配记录。"""
    call_record = models.ForeignKey(
        CallRecord, on_delete=models.CASCADE, related_name='assignments', verbose_name='呼叫记录'
    )
    assigned_to = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, verbose_name='分配给'
    )
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)
    responded_at = models.DateTimeField('响应时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20, default='assigned')  # assigned/accepted/rejected/completed
    role_at_assignment = models.CharField('分配时角色', max_length=30, blank=True)
    notes = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '呼叫分配'
        verbose_name_plural = verbose_name


class EscalationRule(BaseModel):
    """升级规则 -- 定义每种优先级下、每一级角色超时后如何升级。"""
    ROLE_LEVEL_CHOICES = [
        ('care_worker', '护工'),
        ('nurse', '护士'),
        ('admin', '管理员'),
        ('super_admin', '超级管理员'),
    ]

    priority = models.CharField('呼叫优先级', max_length=20, choices=CallRecord.PRIORITY_CHOICES)
    escalation_order = models.PositiveIntegerField('升级顺序', default=0,
        help_text='0=第一级, 1=第二级, 2=第三级...')
    target_role = models.CharField('目标角色', max_length=30, choices=ROLE_LEVEL_CHOICES)
    timeout_seconds = models.PositiveIntegerField('超时秒数', default=180,
        help_text='该级别超时后自动升级到下一级')

    class Meta:
        verbose_name = '升级规则'
        verbose_name_plural = verbose_name
        unique_together = ['priority', 'escalation_order']
        ordering = ['priority', 'escalation_order']

    def __str__(self):
        return f'{self.get_priority_display()} L{self.escalation_order} -> {self.get_target_role_display()} ({self.timeout_seconds}s)'


class CallEscalation(BaseModel):
    """呼叫升级记录 -- 每次超时升级的审计日志。"""
    call_record = models.ForeignKey(
        CallRecord, on_delete=models.CASCADE, related_name='escalations', verbose_name='呼叫记录'
    )
    from_level = models.PositiveIntegerField('原级别')
    to_level = models.PositiveIntegerField('升级至级别')
    target_role = models.CharField('目标角色', max_length=30)
    escalated_at = models.DateTimeField('升级时间', auto_now_add=True)
    reason = models.CharField('原因', max_length=100, default='timeout')  # timeout / manual

    class Meta:
        verbose_name = '呼叫升级记录'
        verbose_name_plural = verbose_name
        ordering = ['escalated_at']

    def __str__(self):
        return f'{self.call_record.call_number} L{self.from_level}->L{self.to_level}'
