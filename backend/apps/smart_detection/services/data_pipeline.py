import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class DataPipeline:
    """数据处理管道：解析结果 -> 存储 -> 规则评估 -> 告警。"""

    def process(self, parsed_results, device):
        """
        处理解析器返回的结果列表。

        Args:
            parsed_results: list of {'type': str, 'data': dict, 'timestamp': datetime}
            device: DetectionDevice实例
        """
        for result in parsed_results:
            msg_type = result.get('type')
            data = result.get('data', {})
            timestamp = result.get('timestamp') or timezone.now()

            try:
                handler = getattr(self, f'_handle_{msg_type}', None)
                if handler:
                    handler(data, device, timestamp)
                else:
                    logger.warning(f'未知消息类型: {msg_type}')
            except Exception:
                logger.exception(f'处理 {msg_type} 消息失败: device={device.device_sn}')

    def _handle_heartbeat(self, data, device, timestamp):
        """更新设备心跳和电量。"""
        update_fields = ['last_heartbeat', 'updated_at']
        device.last_heartbeat = timestamp
        if device.status != 'online':
            device.status = 'online'
            update_fields.append('status')
        battery = data.get('battery')
        if battery is not None:
            device.battery_level = battery
            update_fields.append('battery_level')
        device.save(update_fields=update_fields)

        # 低电量告警
        if battery is not None and battery <= 10:
            self._create_battery_alert(device, battery)

    def _handle_vital_sign(self, data, device, timestamp):
        """创建VitalSign记录并评估规则。"""
        from ..models import VitalSign

        resident = device.bound_resident
        if not resident:
            logger.warning(f'设备 {device.device_sn} 未绑定老人，跳过体征记录')
            return

        vital = VitalSign.objects.create(
            resident=resident,
            device=device,
            measured_at=timestamp,
            heart_rate=data.get('heart_rate'),
            systolic_bp=data.get('systolic_bp'),
            diastolic_bp=data.get('diastolic_bp'),
            blood_oxygen=data.get('blood_oxygen'),
            temperature=data.get('temperature'),
            respiratory_rate=data.get('respiratory_rate'),
        )

        # 规则引擎评估
        from .rule_engine import rule_engine
        rule_engine.evaluate_vitals(vital)

    def _handle_position(self, data, device, timestamp):
        """创建PositionRecord，检查越界。"""
        from ..models import PositionRecord

        resident = device.bound_resident
        if not resident:
            return

        x = data.get('x', 0)
        y = data.get('y', 0)
        floor = data.get('floor', 1)

        # 检查是否在限制区域
        in_restricted = self._check_restricted_zone(x, y, floor)

        position = PositionRecord.objects.create(
            resident=resident,
            device=device,
            timestamp=timestamp,
            x=x, y=y, floor=floor,
            is_in_restricted_zone=in_restricted,
        )

        if in_restricted:
            self._create_restricted_zone_alert(resident, device, position)

    def _handle_fall_alarm(self, data, device, timestamp):
        """创建FallAlert和统一Alert。"""
        from ..models import FallAlert

        resident = device.bound_resident
        severity = data.get('severity', 'suspected')

        fall_alert = FallAlert.objects.create(
            resident=resident,
            device=device,
            alert_time=timestamp,
            location_x=data.get('x'),
            location_y=data.get('y'),
            floor=data.get('floor'),
            severity=severity,
            status='alerting',
        )

        # 同时创建统一告警
        from .alert_service import AlertService
        name = resident.name if resident else '未知'
        AlertService.create_alert(
            alert_type='fall',
            severity='critical',
            title=f'{name} 跌倒告警',
            content=f'检测到{dict(FallAlert.SEVERITY_CHOICES).get(severity, severity)}，'
                    f'置信度: {data.get("confidence", "N/A")}',
            resident=resident,
            device=device,
            source_fall=fall_alert,
            alert_time=timestamp,
            location_description=f'{data.get("floor", "")}楼',
        )

    def _handle_sos(self, data, device, timestamp):
        """SOS按钮告警。"""
        from .alert_service import AlertService

        resident = device.bound_resident
        name = resident.name if resident else '未知'
        AlertService.create_alert(
            alert_type='sos',
            severity='critical',
            title=f'{name} SOS求助',
            content=f'通过{device.get_device_type_display()}发出SOS求助信号',
            resident=resident,
            device=device,
            alert_time=timestamp,
            location_description=f'{data.get("floor", "")}楼' if data.get('floor') else '',
        )

    def _handle_bed_exit(self, data, device, timestamp):
        """离床告警。"""
        from .alert_service import AlertService

        resident = device.bound_resident
        if not resident:
            return

        AlertService.create_alert(
            alert_type='bed_exit',
            severity='warning',
            title=f'{resident.name} 离床',
            content=f'智能床垫检测到离床信号',
            resident=resident,
            device=device,
            alert_time=timestamp,
        )

    def _check_restricted_zone(self, x, y, floor):
        """检查坐标是否在限制区域内（简化实现：查询restricted类型Area）。"""
        from apps.campus.models import Area
        # 简化：检查是否有restricted区域包含该坐标点
        restricted = Area.objects.filter(
            area_type='restricted', is_deleted=False
        ).exists()
        # 实际实现需要坐标范围比较，这里先返回False
        # TODO: 实现真正的坐标范围检查
        return False

    def _create_restricted_zone_alert(self, resident, device, position):
        """创建越界告警。"""
        from .alert_service import AlertService
        AlertService.create_alert(
            alert_type='restricted_zone',
            severity='critical',
            title=f'{resident.name} 进入限制区域',
            content=f'位置: ({position.x}, {position.y}) {position.floor}楼',
            resident=resident,
            device=device,
            source_position=position,
            alert_time=position.timestamp,
        )

    def _create_battery_alert(self, device, battery):
        """创建低电量告警。"""
        from .alert_service import AlertService
        from ..models import Alert

        # 冷却：同设备1小时内不重复
        from datetime import timedelta
        recent = Alert.objects.filter(
            device=device, alert_type='battery_low',
            alert_time__gte=timezone.now() - timedelta(hours=1),
            is_deleted=False
        ).exists()
        if recent:
            return

        AlertService.create_alert(
            alert_type='battery_low',
            severity='info',
            title=f'设备电量低: {device.device_sn}',
            content=f'{device.get_device_type_display()} 电量仅剩 {battery}%',
            resident=device.bound_resident,
            device=device,
        )


# 单例
data_pipeline = DataPipeline()
