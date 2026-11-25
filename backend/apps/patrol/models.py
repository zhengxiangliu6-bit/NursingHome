import uuid
from django.db import models
from apps.common.models import BaseModel


class PatrolCheckpoint(BaseModel):
    """巡更点。"""
    name = models.CharField('巡更点名称', max_length=100)
    code = models.CharField('标识编码', max_length=50, unique=True)  # NFC/QR
    building = models.ForeignKey(
        'campus.Building', on_delete=models.CASCADE, verbose_name='所属楼栋'
    )
    floor = models.IntegerField('楼层')
    area = models.ForeignKey(
        'campus.Area', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='区域'
    )
    location_x = models.FloatField('X坐标', null=True, blank=True)
    location_y = models.FloatField('Y坐标', null=True, blank=True)
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        verbose_name = '巡更点'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PatrolRoute(BaseModel):
    """巡更路线。"""
    name = models.CharField('路线名称', max_length=100)
    description = models.TextField('描述', blank=True)
    checkpoints = models.ManyToManyField(
        PatrolCheckpoint, through='PatrolRouteCheckpoint', verbose_name='巡更点'
    )
    estimated_duration = models.IntegerField('预估时长(分钟)')
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        verbose_name = '巡更路线'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PatrolRouteCheckpoint(models.Model):
    """路线-巡更点关联（有序）。"""
    route = models.ForeignKey(PatrolRoute, on_delete=models.CASCADE)
    checkpoint = models.ForeignKey(PatrolCheckpoint, on_delete=models.CASCADE)
    sequence = models.IntegerField('顺序')
    expected_duration = models.IntegerField('预计到达时间(分钟)', null=True, blank=True)

    class Meta:
        ordering = ['sequence']
        unique_together = ['route', 'sequence']


class PatrolTask(BaseModel):
    """巡更任务。"""
    STATUS_CHOICES = [
        ('scheduled', '已排班'),
        ('in_progress', '巡更中'),
        ('completed', '已完成'),
        ('missed', '未执行'),
        ('abnormal', '异常'),
    ]

    task_number = models.CharField('任务编号', max_length=30, unique=True)
    route = models.ForeignKey(PatrolRoute, on_delete=models.CASCADE, verbose_name='巡更路线')
    assigned_to = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='patrol_tasks', verbose_name='执行人'
    )
    scheduled_start = models.DateTimeField('计划开始时间')
    scheduled_end = models.DateTimeField('计划结束时间')
    actual_start = models.DateTimeField('实际开始时间', null=True, blank=True)
    actual_end = models.DateTimeField('实际结束时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='scheduled')

    class Meta:
        verbose_name = '巡更任务'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.task_number:
            self.task_number = f'PT-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.task_number} - {self.assigned_to}'


class PatrolRecord(BaseModel):
    """巡更打卡记录。"""
    task = models.ForeignKey(
        PatrolTask, on_delete=models.CASCADE, related_name='records', verbose_name='巡更任务'
    )
    checkpoint = models.ForeignKey(PatrolCheckpoint, on_delete=models.CASCADE, verbose_name='巡更点')
    scanned_at = models.DateTimeField('扫描时间')
    is_on_time = models.BooleanField('是否准时', default=True)
    photo = models.ImageField('现场照片', upload_to='patrol/', null=True, blank=True)
    notes = models.TextField('备注', blank=True)
    location_x = models.FloatField('X坐标', null=True, blank=True)
    location_y = models.FloatField('Y坐标', null=True, blank=True)

    class Meta:
        verbose_name = '巡更记录'
        verbose_name_plural = verbose_name


class PatrolException(BaseModel):
    """巡更异常。"""
    SEVERITY_CHOICES = [('low', '低'), ('medium', '中'), ('high', '高')]

    task = models.ForeignKey(
        PatrolTask, on_delete=models.CASCADE, related_name='exceptions', verbose_name='巡更任务'
    )
    checkpoint = models.ForeignKey(
        PatrolCheckpoint, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='巡更点'
    )
    exception_type = models.CharField('异常类型', max_length=30)  # equipment_fault/safety_hazard/resident_issue
    description = models.TextField('异常描述')
    photo = models.ImageField('照片', upload_to='patrol_exceptions/', null=True, blank=True)
    severity = models.CharField('严重程度', max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField('状态', max_length=20, default='reported')
    handled_by = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='处理人'
    )

    class Meta:
        verbose_name = '巡更异常'
        verbose_name_plural = verbose_name
