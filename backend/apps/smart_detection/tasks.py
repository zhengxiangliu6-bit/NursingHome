from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def check_sustained_alert(resident_id, rule_id):
    """
    延迟任务：检查指标是否在duration窗口内持续超阈值。
    由RuleEngine在duration>0时调度。
    """
    from .models import AlertRule, VitalSign, Alert
    from .services.rule_engine import OPERATORS
    from .services.alert_service import AlertService

    try:
        rule = AlertRule.objects.get(id=rule_id, enabled=True, is_deleted=False)
    except AlertRule.DoesNotExist:
        return

    # 检查冷却期
    cooldown_since = timezone.now() - timedelta(seconds=rule.cooldown)
    if Alert.objects.filter(
        resident_id=resident_id, rule=rule,
        alert_time__gte=cooldown_since, is_deleted=False
    ).exists():
        return

    # 查询duration窗口内的所有体征数据
    window_start = timezone.now() - timedelta(seconds=rule.duration)
    vitals = VitalSign.objects.filter(
        resident_id=resident_id,
        measured_at__gte=window_start,
        is_deleted=False
    ).order_by('-measured_at')

    if not vitals.exists():
        return

    # 检查窗口内是否所有值都超阈值
    op_func = OPERATORS.get(rule.operator)
    if not op_func:
        return

    all_exceeded = all(
        op_func(float(getattr(v, rule.metric, 0) or 0), float(rule.threshold))
        for v in vitals
        if getattr(v, rule.metric, None) is not None
    )

    if not all_exceeded:
        return

    # 持续超标，创建告警
    latest_vital = vitals.first()
    metric_display = rule.get_metric_display()
    value = getattr(latest_vital, rule.metric)

    AlertService.create_alert(
        alert_type='vital_abnormal',
        severity=rule.severity,
        title=f'{latest_vital.resident.name} {metric_display}持续异常',
        content=f'{metric_display}: {value} (持续{rule.duration}秒超阈值 {rule.get_operator_display()} {rule.threshold})',
        resident=latest_vital.resident,
        device=latest_vital.device,
        rule=rule,
        source_vital=latest_vital,
        alert_time=timezone.now(),
    )


@shared_task
def check_device_offline():
    """定时任务：检查设备离线（Celery Beat每60秒执行）。"""
    from .models import DetectionDevice, Alert
    from .services.alert_service import AlertService

    threshold = timezone.now() - timedelta(minutes=5)
    offline_devices = DetectionDevice.objects.filter(
        is_deleted=False,
        status='online',
        last_heartbeat__isnull=False,
        last_heartbeat__lt=threshold
    )

    for device in offline_devices:
        device.status = 'offline'
        device.save(update_fields=['status', 'updated_at'])

        # 检查冷却：同设备30分钟内不重复告警
        recent = Alert.objects.filter(
            device=device, alert_type='device_offline',
            alert_time__gte=timezone.now() - timedelta(minutes=30),
            is_deleted=False
        ).exists()
        if recent:
            continue

        resident = device.bound_resident
        AlertService.create_alert(
            alert_type='device_offline',
            severity='warning',
            title=f'设备离线: {device.device_sn}',
            content=f'{device.get_device_type_display()} ({device.device_sn}) 已超过5分钟未上报心跳',
            resident=resident,
            device=device,
            location_description=str(device.location) if device.location else '',
        )
