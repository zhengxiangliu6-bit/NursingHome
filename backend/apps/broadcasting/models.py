from django.db import models
from apps.common.models import BaseModel


class BroadcastZone(BaseModel):
    """广播分区。"""
    name = models.CharField('分区名称', max_length=100)
    building = models.ForeignKey(
        'campus.Building', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='所属楼栋'
    )
    floor = models.IntegerField('楼层', null=True, blank=True)
    description = models.TextField('描述', blank=True)

    class Meta:
        verbose_name = '广播分区'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BroadcastDevice(BaseModel):
    """广播设备（扬声器/功放）。"""
    device_sn = models.CharField('设备序列号', max_length=100, unique=True)
    name = models.CharField('设备名称', max_length=100)
    zone = models.ForeignKey(
        BroadcastZone, on_delete=models.CASCADE, related_name='devices', verbose_name='广播分区'
    )
    status = models.CharField('状态', max_length=20, default='online')
    volume = models.IntegerField('音量', default=50)  # 0-100

    class Meta:
        verbose_name = '广播设备'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BroadcastTask(BaseModel):
    """广播任务。"""
    BROADCAST_TYPE_CHOICES = [
        ('realtime', '实时广播'),
        ('scheduled', '定时广播'),
        ('emergency', '紧急广播'),
    ]
    SOURCE_TYPE_CHOICES = [
        ('audio_file', '音频文件'),
        ('tts', '语音转文字'),
        ('live', '实时语音'),
    ]
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('scheduled', '已计划'),
        ('broadcasting', '播放中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    title = models.CharField('标题', max_length=200)
    broadcast_type = models.CharField('广播类型', max_length=20, choices=BROADCAST_TYPE_CHOICES)
    source_type = models.CharField('来源类型', max_length=20, choices=SOURCE_TYPE_CHOICES)
    content_text = models.TextField('文字内容', blank=True)
    audio_file = models.FileField('音频文件', upload_to='broadcasts/', null=True, blank=True)
    zones = models.ManyToManyField(BroadcastZone, related_name='tasks', verbose_name='广播分区')
    priority = models.IntegerField('优先级', default=5)  # 1=最高
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_time = models.DateTimeField('计划时间', null=True, blank=True)
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    ended_at = models.DateTimeField('结束时间', null=True, blank=True)
    created_by_user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, verbose_name='创建人'
    )

    class Meta:
        verbose_name = '广播任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class BroadcastSchedule(BaseModel):
    """定时广播计划。"""
    name = models.CharField('计划名称', max_length=100)
    cron_expression = models.CharField('Cron表达式', max_length=100)  # e.g., "0 7 * * *"
    source_type = models.CharField('来源类型', max_length=20)
    content_text = models.TextField('文字内容', blank=True)
    audio_file = models.FileField('音频文件', upload_to='broadcast_schedules/', null=True, blank=True)
    zones = models.ManyToManyField(BroadcastZone, verbose_name='广播分区')
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        verbose_name = '定时广播计划'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BroadcastLog(BaseModel):
    """广播审计日志。"""
    task = models.ForeignKey(
        BroadcastTask, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='广播任务'
    )
    action = models.CharField('操作', max_length=30)  # started/stopped/error
    device = models.ForeignKey(
        BroadcastDevice, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='设备'
    )
    timestamp = models.DateTimeField('时间', auto_now_add=True)
    details = models.TextField('详情', blank=True)

    class Meta:
        verbose_name = '广播日志'
        verbose_name_plural = verbose_name
