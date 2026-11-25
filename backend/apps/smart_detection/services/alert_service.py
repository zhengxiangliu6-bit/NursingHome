from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class AlertService:
    """统一告警服务 -- 创建告警、状态变更、WebSocket推送。"""

    @staticmethod
    def create_alert(alert_type, severity, title, content,
                     resident=None, device=None, rule=None, **kwargs):
        """创建告警并推送WebSocket通知。"""
        from ..models import Alert, AlertHandleLog

        alert = Alert.objects.create(
            alert_type=alert_type,
            severity=severity,
            title=title,
            content=content,
            resident=resident,
            device=device,
            rule=rule,
            alert_time=kwargs.pop('alert_time', timezone.now()),
            status='pending',
            **kwargs
        )
        # 创建初始处理日志
        AlertHandleLog.objects.create(
            alert=alert,
            action='create',
            from_status='',
            to_status='pending',
            remark='系统自动创建'
        )
        # WebSocket推送
        AlertService._push_websocket(alert)
        return alert

    @staticmethod
    def assign_alert(alert, user, assigned_to_user, remark=''):
        """指派告警给指定员工。"""
        from ..models import AlertHandleLog

        old_status = alert.status
        alert.status = 'assigned'
        alert.assigned_to = assigned_to_user
        alert.assigned_at = timezone.now()
        alert.save(update_fields=['status', 'assigned_to', 'assigned_at', 'updated_at'])

        AlertHandleLog.objects.create(
            alert=alert, action='assign',
            from_status=old_status, to_status='assigned',
            operator=user, remark=remark
        )
        AlertService._push_websocket(alert, action='assigned')

    @staticmethod
    def start_process(alert, user, remark=''):
        """开始处理告警。"""
        from ..models import AlertHandleLog

        old_status = alert.status
        alert.status = 'processing'
        alert.processed_by = user
        alert.save(update_fields=['status', 'processed_by', 'updated_at'])

        AlertHandleLog.objects.create(
            alert=alert, action='start_process',
            from_status=old_status, to_status='processing',
            operator=user, remark=remark
        )
        AlertService._push_websocket(alert, action='processing')

    @staticmethod
    def resolve_alert(alert, user, resolution='', remark=''):
        """解决告警。"""
        from ..models import AlertHandleLog

        old_status = alert.status
        alert.status = 'resolved'
        alert.processed_by = user
        alert.processed_at = timezone.now()
        alert.resolution = resolution
        alert.save(update_fields=[
            'status', 'processed_by', 'processed_at', 'resolution', 'updated_at'
        ])

        AlertHandleLog.objects.create(
            alert=alert, action='resolve',
            from_status=old_status, to_status='resolved',
            operator=user, remark=remark
        )
        AlertService._push_websocket(alert, action='resolved')

    @staticmethod
    def dismiss_alert(alert, user, remark=''):
        """忽略告警。"""
        from ..models import AlertHandleLog

        old_status = alert.status
        alert.status = 'dismissed'
        alert.processed_by = user
        alert.processed_at = timezone.now()
        alert.save(update_fields=['status', 'processed_by', 'processed_at', 'updated_at'])

        AlertHandleLog.objects.create(
            alert=alert, action='dismiss',
            from_status=old_status, to_status='dismissed',
            operator=user, remark=remark
        )
        AlertService._push_websocket(alert, action='dismissed')

    @staticmethod
    def _push_websocket(alert, action='new_alert'):
        """通过WebSocket推送告警到前端。"""
        try:
            channel_layer = get_channel_layer()
            data = {
                'action': action,
                'id': str(alert.id),
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'content': alert.content,
                'resident_name': alert.resident.name if alert.resident else None,
                'resident_id': str(alert.resident.id) if alert.resident else None,
                'status': alert.status,
                'alert_time': alert.alert_time.isoformat(),
                'location_description': alert.location_description,
            }
            async_to_sync(channel_layer.group_send)(
                'alerts',
                {'type': 'alert_update', 'data': data}
            )
        except Exception:
            pass  # WebSocket推送失败不应阻断主流程
