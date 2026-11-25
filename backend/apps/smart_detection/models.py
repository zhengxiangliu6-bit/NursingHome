from django.db import models
from apps.common.models import BaseModel


class DetectionDevice(BaseModel):
    """检测设备。"""
    DEVICE_TYPE_CHOICES = [
        ('wearable', '穿戴设备'),
        ('room_sensor', '房间传感器'),
        ('beacon', '定位信标'),
        ('camera', '智能摄像头'),
    ]

    device_sn = models.CharField('设备序列号', max_length=100, unique=True)
    device_type = models.CharField('设备类型', max_length=30, choices=DEVICE_TYPE_CHOICES)
    bound_resident = models.ForeignKey(
        'residents.Resident', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='绑定老人'
    )
    location = models.ForeignKey(
        'campus.Area', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='位置'
    )
    status = models.CharField('状态', max_length=20, default='online')
    battery_level = models.IntegerField('电量(%)', null=True, blank=True)
    last_heartbeat = models.DateTimeField('最近心跳', null=True, blank=True)

    class Meta:
        verbose_name = '检测设备'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.get_device_type_display()} ({self.device_sn})'


class VitalSign(BaseModel):
    """生命体征时序数据。"""
    resident = models.ForeignKey(
        'residents.Resident', on_delete=models.CASCADE,
        related_name='vital_signs', verbose_name='老人'
    )
    device = models.ForeignKey(
        DetectionDevice, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='设备'
    )
    measured_at = models.DateTimeField('测量时间')
    heart_rate = models.IntegerField('心率(bpm)', null=True, blank=True)
    systolic_bp = models.IntegerField('收缩压(mmHg)', null=True, blank=True)
    diastolic_bp = models.IntegerField('舒张压(mmHg)', null=True, blank=True)
    blood_oxygen = models.FloatField('血氧(%)', null=True, blank=True)
    temperature = models.FloatField('体温(℃)', null=True, blank=True)
    respiratory_rate = models.IntegerField('呼吸率(次/分)', null=True, blank=True)
    is_abnormal = models.BooleanField('是否异常', default=False)
    abnormal_items = models.JSONField('异常项', default=list, blank=True)

    class Meta:
        verbose_name = '生命体征'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['resident', 'measured_at']),
            models.Index(fields=['measured_at']),
        ]


class FallAlert(BaseModel):
    """跌倒预警。"""
    SEVERITY_CHOICES = [
        ('suspected', '疑似跌倒'),
        ('confirmed', '确认跌倒'),
        ('false_alarm', '误报'),
    ]
    STATUS_CHOICES = [
        ('alerting', '告警中'),
        ('responding', '响应中'),
        ('resolved', '已处理'),
        ('dismissed', '已忽略'),
    ]

    resident = models.ForeignKey(
        'residents.Resident', on_delete=models.CASCADE,
        related_name='fall_alerts', verbose_name='老人'
    )
    device = models.ForeignKey(
        DetectionDevice, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='设备'
    )
    alert_time = models.DateTimeField('告警时间')
    location_x = models.FloatField('X坐标', null=True, blank=True)
    location_y = models.FloatField('Y坐标', null=True, blank=True)
    floor = models.IntegerField('楼层', null=True, blank=True)
    location_description = models.CharField('位置描述', max_length=200, blank=True)
    severity = models.CharField('严重程度', max_length=20, choices=SEVERITY_CHOICES, default='suspected')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='alerting')
    handled_by = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='处理人'
    )
    handle_time = models.DateTimeField('处理时间', null=True, blank=True)
    notes = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '跌倒预警'
        verbose_name_plural = verbose_name


class HealthCheckRecord(BaseModel):
    """健康检查记录。"""
    resident = models.ForeignKey(
        'residents.Resident', on_delete=models.CASCADE, verbose_name='老人'
    )
    checked_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, verbose_name='检查人'
    )
    check_time = models.DateTimeField('检查时间')
    check_type = models.CharField('检查类型', max_length=30)  # daily_round/weekly_checkup/special
    vital_sign = models.OneToOneField(
        VitalSign, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='体征数据'
    )
    mental_status = models.CharField('精神状态', max_length=20, blank=True)
    skin_condition = models.CharField('皮肤状况', max_length=50, blank=True)
    appetite = models.CharField('食欲', max_length=20, blank=True)
    sleep_quality = models.CharField('睡眠质量', max_length=20, blank=True)
    notes = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '健康检查'
        verbose_name_plural = verbose_name


class PositionRecord(BaseModel):
    """室内定位记录。"""
    resident = models.ForeignKey(
        'residents.Resident', on_delete=models.CASCADE, verbose_name='老人'
    )
    device = models.ForeignKey(
        DetectionDevice, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='设备'
    )
    timestamp = models.DateTimeField('时间戳')
    x = models.FloatField('X坐标')
    y = models.FloatField('Y坐标')
    floor = models.IntegerField('楼层')
    area = models.ForeignKey(
        'campus.Area', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='区域'
    )
    is_in_restricted_zone = models.BooleanField('是否在限制区域', default=False)

    class Meta:
        verbose_name = '定位记录'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['resident', 'timestamp']),
        ]


# ==================== Phase 2 新增模型 ====================


class MQTTDeviceMapping(BaseModel):
    """MQTT设备映射 -- 将MQTT topic映射到DetectionDevice。"""
    PROTOCOL_TYPE_CHOICES = [
        ('smart_mattress', '智能床垫'),
        ('wristband', '手环/定位卡'),
        ('fall_radar', '跌倒雷达'),
        ('fall_camera', 'AI摄像头'),
    ]

    detection_device = models.OneToOneField(
        DetectionDevice, on_delete=models.CASCADE,
        related_name='mqtt_mapping', verbose_name='检测设备'
    )
    mqtt_client_id = models.CharField('MQTT Client ID', max_length=200, blank=True)
    mqtt_topic = models.CharField('订阅Topic', max_length=200,
        help_text='例如: devices/{device_sn}/data')
    protocol_type = models.CharField('协议类型', max_length=30, choices=PROTOCOL_TYPE_CHOICES)
    parser_config = models.JSONField('解析配置', default=dict, blank=True,
        help_text='厂商特定的字段映射配置')

    class Meta:
        verbose_name = 'MQTT设备映射'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.detection_device.device_sn} -> {self.mqtt_topic}'


class AlertRule(BaseModel):
    """可配置告警规则。"""
    METRIC_CHOICES = [
        ('heart_rate', '心率'),
        ('systolic_bp', '收缩压'),
        ('diastolic_bp', '舒张压'),
        ('blood_oxygen', '血氧'),
        ('temperature', '体温'),
        ('respiratory_rate', '呼吸率'),
        ('bed_exit', '离床'),
        ('restricted_zone', '越界'),
        ('device_offline', '设备离线'),
    ]
    OPERATOR_CHOICES = [
        ('gt', '>'),
        ('gte', '>='),
        ('lt', '<'),
        ('lte', '<='),
        ('eq', '=='),
        ('neq', '!='),
    ]
    SEVERITY_CHOICES = [
        ('critical', '严重'),
        ('warning', '警告'),
        ('info', '提示'),
    ]

    name = models.CharField('规则名称', max_length=100)
    description = models.TextField('规则描述', blank=True)
    metric = models.CharField('监控指标', max_length=30, choices=METRIC_CHOICES)
    operator = models.CharField('操作符', max_length=10, choices=OPERATOR_CHOICES)
    threshold = models.FloatField('阈值')
    duration = models.IntegerField('持续时间(秒)', default=0,
        help_text='指标持续超出阈值多少秒后触发告警，0表示立即触发')
    severity = models.CharField('告警级别', max_length=20, choices=SEVERITY_CHOICES, default='warning')
    enabled = models.BooleanField('是否启用', default=True)
    cooldown = models.IntegerField('冷却时间(秒)', default=300,
        help_text='同一老人同一规则在冷却时间内不重复触发')
    created_by = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='创建人'
    )

    class Meta:
        verbose_name = '告警规则'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.name} ({self.get_metric_display()} {self.get_operator_display()} {self.threshold})'


class Alert(BaseModel):
    """统一告警模型 -- 覆盖所有告警类型，实现报警-处置-归档闭环。"""
    ALERT_TYPE_CHOICES = [
        ('vital_abnormal', '体征异常'),
        ('fall', '跌倒'),
        ('sos', 'SOS求助'),
        ('bed_exit', '离床'),
        ('restricted_zone', '越界'),
        ('device_offline', '设备离线'),
        ('battery_low', '电量低'),
    ]
    SEVERITY_CHOICES = [
        ('critical', '严重'),
        ('warning', '警告'),
        ('info', '提示'),
    ]
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('assigned', '已指派'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('dismissed', '已忽略'),
        ('auto_resolved', '自动恢复'),
    ]

    alert_type = models.CharField('告警类型', max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField('严重程度', max_length=20, choices=SEVERITY_CHOICES, default='warning')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    title = models.CharField('告警标题', max_length=200)
    content = models.TextField('告警内容')

    resident = models.ForeignKey(
        'residents.Resident', null=True, blank=True, on_delete=models.CASCADE,
        related_name='alerts', verbose_name='关联老人'
    )
    device = models.ForeignKey(
        DetectionDevice, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='alerts', verbose_name='关联设备'
    )
    rule = models.ForeignKey(
        AlertRule, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='alerts', verbose_name='触发规则'
    )

    # 关联到原始数据记录
    source_vital = models.ForeignKey(
        VitalSign, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='关联体征'
    )
    source_fall = models.ForeignKey(
        FallAlert, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='关联跌倒'
    )
    source_position = models.ForeignKey(
        PositionRecord, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='关联定位'
    )

    location_description = models.CharField('位置描述', max_length=200, blank=True)
    alert_time = models.DateTimeField('告警时间')

    # 处理闭环字段
    assigned_to = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='assigned_alerts', verbose_name='指派给'
    )
    assigned_at = models.DateTimeField('指派时间', null=True, blank=True)
    processed_by = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='processed_alerts', verbose_name='处理人'
    )
    processed_at = models.DateTimeField('处理时间', null=True, blank=True)
    resolution = models.TextField('处理结果', blank=True)

    extra_data = models.JSONField('附加数据', default=dict, blank=True)

    class Meta:
        verbose_name = '告警'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['alert_type', 'status']),
            models.Index(fields=['resident', 'alert_time']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['alert_time']),
        ]

    def __str__(self):
        return f'[{self.get_severity_display()}] {self.title}'


class AlertHandleLog(BaseModel):
    """告警处理日志 -- 每次状态变更都记录，形成处理审计链。"""
    alert = models.ForeignKey(
        Alert, on_delete=models.CASCADE, related_name='handle_logs', verbose_name='告警'
    )
    action = models.CharField('操作', max_length=30)  # create/assign/start_process/resolve/dismiss/escalate
    from_status = models.CharField('原状态', max_length=20, blank=True)
    to_status = models.CharField('新状态', max_length=20)
    operator = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作人'
    )
    remark = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '告警处理日志'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        return f'{self.alert} {self.action}: {self.from_status}->{self.to_status}'
