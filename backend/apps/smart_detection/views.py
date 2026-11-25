from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import IsStaff, IsAdmin, IsNurseOrAbove
from .models import (
    DetectionDevice, VitalSign, FallAlert, HealthCheckRecord, PositionRecord,
    MQTTDeviceMapping, AlertRule, Alert,
)
from .serializers import (
    DetectionDeviceSerializer, VitalSignSerializer,
    FallAlertSerializer, HealthCheckRecordSerializer, PositionRecordSerializer,
    MQTTDeviceMappingSerializer, AlertRuleSerializer,
    AlertSerializer, AlertListSerializer,
)


class DetectionDeviceViewSet(viewsets.ModelViewSet):
    queryset = DetectionDevice.objects.select_related('bound_resident').filter(is_deleted=False)
    serializer_class = DetectionDeviceSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['device_type', 'status']


class VitalSignViewSet(viewsets.ModelViewSet):
    queryset = VitalSign.objects.select_related('resident').filter(is_deleted=False)
    serializer_class = VitalSignSerializer
    permission_classes = [IsStaff]
    filterset_fields = ['resident', 'is_abnormal']
    ordering_fields = ['measured_at']

    @action(detail=False, methods=['get'], url_path='latest/(?P<resident_id>[^/.]+)')
    def latest(self, request, resident_id=None):
        """获取指定老人最新的生命体征数据。"""
        vital = self.queryset.filter(resident_id=resident_id).order_by('-measured_at').first()
        if vital:
            return Response(VitalSignSerializer(vital).data)
        return Response({'detail': '暂无数据'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='trends/(?P<resident_id>[^/.]+)')
    def trends(self, request, resident_id=None):
        """获取指定老人的生命体征趋势。"""
        days = int(request.query_params.get('days', 7))
        from datetime import timedelta
        since = timezone.now() - timedelta(days=days)
        vitals = self.queryset.filter(
            resident_id=resident_id, measured_at__gte=since
        ).order_by('measured_at')
        serializer = VitalSignSerializer(vitals, many=True)
        return Response(serializer.data)


class FallAlertViewSet(viewsets.ModelViewSet):
    queryset = FallAlert.objects.select_related('resident', 'handled_by').filter(is_deleted=False)
    serializer_class = FallAlertSerializer
    permission_classes = [IsStaff]
    filterset_fields = ['severity', 'status', 'resident']

    @action(detail=False, methods=['get'])
    def active(self, request):
        active_alerts = self.queryset.filter(
            status__in=['alerting', 'responding']
        ).order_by('-alert_time')
        return Response(FallAlertSerializer(active_alerts, many=True).data)

    @action(detail=True, methods=['patch'])
    def respond(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'responding'
        alert.handled_by = request.user
        alert.save()
        return Response(FallAlertSerializer(alert).data)

    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status = request.data.get('status', 'resolved')
        alert.handle_time = timezone.now()
        alert.notes = request.data.get('notes', alert.notes)
        alert.save()
        return Response(FallAlertSerializer(alert).data)


class HealthCheckRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthCheckRecord.objects.select_related('resident', 'checked_by').filter(is_deleted=False)
    serializer_class = HealthCheckRecordSerializer
    permission_classes = [IsNurseOrAbove]
    filterset_fields = ['resident', 'check_type']


class PositionRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PositionRecord.objects.select_related('resident').filter(is_deleted=False)
    serializer_class = PositionRecordSerializer
    permission_classes = [IsStaff]
    filterset_fields = ['resident', 'floor']

    @action(detail=False, methods=['get'], url_path='current/(?P<resident_id>[^/.]+)')
    def current(self, request, resident_id=None):
        """获取指定老人的当前位置。"""
        position = self.queryset.filter(resident_id=resident_id).order_by('-timestamp').first()
        if position:
            return Response(PositionRecordSerializer(position).data)
        return Response({'detail': '暂无定位数据'}, status=status.HTTP_404_NOT_FOUND)


# ==================== Phase 2 新增视图 ====================


class MQTTDeviceMappingViewSet(viewsets.ModelViewSet):
    queryset = MQTTDeviceMapping.objects.select_related('detection_device').filter(is_deleted=False)
    serializer_class = MQTTDeviceMappingSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['protocol_type']


class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.filter(is_deleted=False)
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['metric', 'severity', 'enabled']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """启用/禁用规则。"""
        rule = self.get_object()
        rule.enabled = not rule.enabled
        rule.save(update_fields=['enabled', 'updated_at'])
        return Response(AlertRuleSerializer(rule).data)


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related(
        'resident', 'device', 'rule', 'assigned_to', 'processed_by'
    ).prefetch_related('handle_logs').filter(is_deleted=False)
    permission_classes = [IsStaff]
    filterset_fields = ['alert_type', 'severity', 'status', 'resident']
    search_fields = ['title', 'content']
    ordering_fields = ['alert_time', 'severity']

    def get_serializer_class(self):
        if self.action == 'list':
            return AlertListSerializer
        return AlertSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取所有活跃告警（待处理/已指派/处理中）。"""
        active = self.queryset.filter(
            status__in=['pending', 'assigned', 'processing']
        ).order_by('-severity', '-alert_time')
        serializer = AlertListSerializer(active, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """告警统计。"""
        from django.db.models import Count, Q
        qs = self.queryset
        stats = qs.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            critical=Count('id', filter=Q(severity='critical', status__in=['pending', 'assigned', 'processing'])),
            resolved=Count('id', filter=Q(status='resolved')),
        )
        by_type = list(qs.values('alert_type').annotate(count=Count('id')).order_by('-count'))
        stats['by_type'] = by_type
        return Response(stats)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """指派告警。"""
        alert = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        if not assigned_to_id:
            return Response({'detail': '请指定被指派人'}, status=status.HTTP_400_BAD_REQUEST)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            assigned_to = User.objects.get(id=assigned_to_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        from .services.alert_service import AlertService
        AlertService.assign_alert(alert, request.user, assigned_to,
                                  remark=request.data.get('remark', ''))
        return Response(AlertSerializer(alert).data)

    @action(detail=True, methods=['post'])
    def start_process(self, request, pk=None):
        """开始处理告警。"""
        alert = self.get_object()
        from .services.alert_service import AlertService
        AlertService.start_process(alert, request.user,
                                   remark=request.data.get('remark', ''))
        return Response(AlertSerializer(alert).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """解决告警。"""
        alert = self.get_object()
        from .services.alert_service import AlertService
        AlertService.resolve_alert(
            alert, request.user,
            resolution=request.data.get('resolution', ''),
            remark=request.data.get('remark', '')
        )
        return Response(AlertSerializer(alert).data)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """忽略告警。"""
        alert = self.get_object()
        from .services.alert_service import AlertService
        AlertService.dismiss_alert(alert, request.user,
                                   remark=request.data.get('remark', ''))
        return Response(AlertSerializer(alert).data)
