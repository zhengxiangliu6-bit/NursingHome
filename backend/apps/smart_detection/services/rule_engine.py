import logging
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

# 体征类指标列表（对应 VitalSign 模型字段名）
VITAL_METRICS = [
    'heart_rate', 'systolic_bp', 'diastolic_bp',
    'blood_oxygen', 'temperature', 'respiratory_rate'
]

OPERATORS = {
    'gt': lambda v, t: v > t,
    'gte': lambda v, t: v >= t,
    'lt': lambda v, t: v < t,
    'lte': lambda v, t: v <= t,
    'eq': lambda v, t: v == t,
    'neq': lambda v, t: v != t,
}


class RuleEngine:
    """规则引擎 -- 评估体征数据是否触发告警规则。"""

    def evaluate_vitals(self, vital_sign):
        """评估一条体征数据是否触发告警。"""
        from ..models import AlertRule

        rules = AlertRule.objects.filter(
            enabled=True, is_deleted=False,
            metric__in=VITAL_METRICS
        )

        for rule in rules:
            value = getattr(vital_sign, rule.metric, None)
            if value is None:
                continue

            if not self._check_condition(value, rule.operator, rule.threshold):
                continue

            if rule.duration > 0:
                # 持续性规则：调度 Celery 延迟检查
                from ..tasks import check_sustained_alert
                check_sustained_alert.apply_async(
                    args=[str(vital_sign.resident_id), str(rule.id)],
                    countdown=rule.duration
                )
            else:
                # 即时规则：检查冷却后直接创建告警
                self._maybe_create_alert(vital_sign, rule)

    def _check_condition(self, value, operator, threshold):
        """比较值是否满足条件。"""
        op_func = OPERATORS.get(operator)
        if not op_func:
            return False
        return op_func(float(value), float(threshold))

    def _maybe_create_alert(self, vital_sign, rule):
        """检查冷却期后创建告警。"""
        if self._in_cooldown(vital_sign.resident_id, rule):
            return

        from .alert_service import AlertService

        metric_display = rule.get_metric_display()
        value = getattr(vital_sign, rule.metric)
        op_display = rule.get_operator_display()

        AlertService.create_alert(
            alert_type='vital_abnormal',
            severity=rule.severity,
            title=f'{vital_sign.resident.name} {metric_display}异常',
            content=f'{metric_display}: {value} (规则: {op_display} {rule.threshold})',
            resident=vital_sign.resident,
            device=vital_sign.device,
            rule=rule,
            source_vital=vital_sign,
            alert_time=vital_sign.measured_at,
        )

    def _in_cooldown(self, resident_id, rule):
        """检查是否在冷却期内（同一老人同一规则）。"""
        from ..models import Alert

        cooldown_since = timezone.now() - timedelta(seconds=rule.cooldown)
        return Alert.objects.filter(
            resident_id=resident_id,
            rule=rule,
            alert_time__gte=cooldown_since,
            is_deleted=False
        ).exists()


# 单例
rule_engine = RuleEngine()
