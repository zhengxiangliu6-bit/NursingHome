from django.db import models
from apps.common.models import BaseModel


class Building(BaseModel):
    """楼栋信息。"""
    name = models.CharField('楼栋名称', max_length=100)
    code = models.CharField('楼栋编号', max_length=20, unique=True)
    address = models.CharField('地址', max_length=200, blank=True)
    floors = models.IntegerField('楼层数')
    description = models.TextField('描述', blank=True)
    floor_plan_image = models.ImageField('平面图', upload_to='floor_plans/', null=True, blank=True)

    class Meta:
        verbose_name = '楼栋'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Area(BaseModel):
    """楼栋内的区域。"""
    AREA_TYPE_CHOICES = [
        ('residential', '住宿区'),
        ('common', '公共区'),
        ('medical', '医疗区'),
        ('dining', '餐饮区'),
        ('outdoor', '户外区'),
        ('restricted', '限制区'),
    ]

    name = models.CharField('区域名称', max_length=100)
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name='areas', verbose_name='所属楼栋'
    )
    floor = models.IntegerField('所在楼层')
    area_type = models.CharField('区域类型', max_length=30, choices=AREA_TYPE_CHOICES)
    map_coordinates = models.JSONField('地图坐标', null=True, blank=True)

    class Meta:
        verbose_name = '区域'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.building.name} - {self.name}'


class Device(BaseModel):
    """全硬件设备注册表。"""
    DEVICE_CATEGORY_CHOICES = [
        ('camera', '摄像头'),
        ('sensor', '传感器'),
        ('speaker', '广播设备'),
        ('call_device', '呼叫设备'),
        ('beacon', '定位信标'),
        ('network', '网络设备'),
        ('display', '显示设备'),
        ('other', '其他'),
    ]
    STATUS_CHOICES = [
        ('online', '在线'),
        ('offline', '离线'),
        ('fault', '故障'),
        ('maintenance', '维护中'),
    ]

    device_sn = models.CharField('设备序列号', max_length=100, unique=True)
    name = models.CharField('设备名称', max_length=100)
    device_category = models.CharField('设备类别', max_length=30, choices=DEVICE_CATEGORY_CHOICES)
    model_name = models.CharField('设备型号', max_length=100, blank=True)
    manufacturer = models.CharField('制造商', max_length=100, blank=True)
    building = models.ForeignKey(
        Building, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='所属楼栋'
    )
    area = models.ForeignKey(
        Area, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='所属区域'
    )
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='online')
    installed_at = models.DateField('安装日期', null=True, blank=True)
    last_maintenance = models.DateField('最近维护日期', null=True, blank=True)
    config = models.JSONField('配置信息', default=dict, blank=True)

    class Meta:
        verbose_name = '设备'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.name} ({self.device_sn})'


class DeviceMaintenanceLog(BaseModel):
    """设备维护日志。"""
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name='maintenance_logs', verbose_name='设备'
    )
    maintained_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, verbose_name='维护人员'
    )
    maintenance_type = models.CharField('维护类型', max_length=30)  # routine/repair/replacement
    description = models.TextField('维护描述')
    result = models.CharField('维护结果', max_length=20)  # success/pending_parts/needs_replacement
    cost = models.DecimalField('费用', max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = '维护日志'
        verbose_name_plural = verbose_name


class Notice(BaseModel):
    """信息发布/通知公告。"""
    NOTICE_TYPE_CHOICES = [
        ('announcement', '通知公告'),
        ('policy', '制度规范'),
        ('activity', '活动通知'),
        ('emergency', '紧急通报'),
    ]

    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    notice_type = models.CharField('类型', max_length=20, choices=NOTICE_TYPE_CHOICES)
    target_roles = models.JSONField('目标角色', default=list, blank=True)
    is_published = models.BooleanField('是否发布', default=False)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    author = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, verbose_name='作者'
    )
    attachments = models.JSONField('附件', default=list, blank=True)

    class Meta:
        verbose_name = '通知公告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
