from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import IsStaff, IsAdmin, IsNurseOrAbove
from .models import CallDevice, CallRecord, CallAssignment, EscalationRule
from .serializers import (
    CallDeviceSerializer, CallRecordSerializer,
    CallRecordListSerializer, CallAssignmentSerializer,
    EscalationRuleSerializer,
)


class CallDeviceViewSet(viewsets.ModelViewSet):
    queryset = CallDevice.objects.select_related('bound_resident').filter(is_deleted=False)
    serializer_class = CallDeviceSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['device_type', 'status']


class CallRecordViewSet(viewsets.ModelViewSet):
    queryset = CallRecord.objects.select_related(
        'caller_resident', 'call_device', 'building'
    ).prefetch_related('assignments', 'escalations').filter(is_deleted=False)
    permission_classes = [IsStaff]
    filterset_fields = ['priority', 'status']
    search_fields = ['call_number', 'caller_resident__name']
    ordering_fields = ['call_time', 'priority']

    def get_serializer_class(self):
        if self.action == 'list':
            return CallRecordListSerializer
        return CallRecordSerializer

    def perform_create(self, serializer):
        call = serializer.save()
        # 从老人床位推导楼栋
        resident = call.caller_resident
        if resident.bed and resident.bed.room:
            call.building = resident.bed.room.building
            if not call.location_description:
                call.location_description = (
                    f'{resident.bed.room.building.name} '
                    f'{resident.bed.room.room_number}房 '
                    f'{resident.bed.bed_number}床'
                )
            call.save(update_fields=['building', 'location_description'])
        # 调度升级定时器
        from .tasks import schedule_initial_escalation
        schedule_initial_escalation(call)
        # WebSocket广播
        from .broadcast import broadcast_call_event
        data = CallRecordSerializer(call).data
        broadcast_call_event(
            'call_new', data,
            building_id=str(call.building_id) if call.building_id else None
        )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取当前所有未解决的呼叫。"""
        active_calls = self.queryset.filter(
            status__in=['pending', 'accepted', 'in_progress']
        ).order_by('-priority', 'call_time')
        serializer = CallRecordSerializer(active_calls, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def accept(self, request, pk=None):
        """接受呼叫。"""
        call = self.get_object()
        if call.status != 'pending':
            return Response({'detail': '该呼叫已被处理'}, status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        call.status = 'accepted'
        call.accept_time = now
        call.response_duration = int((now - call.call_time).total_seconds())
        call.save()
        CallAssignment.objects.create(
            call_record=call,
            assigned_to=request.user,
            status='accepted',
            role_at_assignment=request.user.role.name if request.user.role else ''
        )
        # 取消升级定时器
        from .tasks import cancel_escalation_timer
        cancel_escalation_timer(call)
        # WebSocket广播
        from .broadcast import broadcast_call_event
        broadcast_call_event(
            'call_accepted',
            {
                'call_id': str(call.id),
                'call_number': call.call_number,
                'accepted_by': request.user.get_full_name() or request.user.username,
                'accepted_by_role': request.user.role.name if request.user.role else '',
                'accept_time': now.isoformat(),
            },
            building_id=str(call.building_id) if call.building_id else None
        )
        return Response(CallRecordSerializer(call).data)

    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        """解决呼叫。"""
        call = self.get_object()
        call.status = 'resolved'
        call.resolve_time = timezone.now()
        call.notes = request.data.get('notes', call.notes)
        call.save()
        # 取消升级定时器
        from .tasks import cancel_escalation_timer
        cancel_escalation_timer(call)
        # WebSocket广播
        from .broadcast import broadcast_call_event
        broadcast_call_event(
            'call_resolved',
            {
                'call_id': str(call.id),
                'call_number': call.call_number,
                'resolved_by': request.user.get_full_name() or request.user.username,
                'resolve_time': call.resolve_time.isoformat(),
            },
            building_id=str(call.building_id) if call.building_id else None
        )
        return Response(CallRecordSerializer(call).data)

    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """取消呼叫。"""
        call = self.get_object()
        call.status = 'cancelled'
        call.save()
        # 取消升级定时器
        from .tasks import cancel_escalation_timer
        cancel_escalation_timer(call)
        # WebSocket广播
        from .broadcast import broadcast_call_event
        broadcast_call_event(
            'call_cancelled',
            {'call_id': str(call.id), 'call_number': call.call_number},
            building_id=str(call.building_id) if call.building_id else None
        )
        return Response(CallRecordSerializer(call).data)

    @action(detail=True, methods=['patch'], permission_classes=[IsNurseOrAbove])
    def escalate(self, request, pk=None):
        """手动升级呼叫。"""
        call = self.get_object()
        if call.status != 'pending':
            return Response({'detail': '只能升级待响应的呼叫'}, status=status.HTTP_400_BAD_REQUEST)
        # 取消当前定时器并立即触发升级
        from .tasks import cancel_escalation_timer, check_call_escalation
        cancel_escalation_timer(call)
        check_call_escalation(str(call.id))
        call.refresh_from_db()
        return Response(CallRecordSerializer(call).data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """呼叫统计。"""
        from django.db.models import Avg, Count, Q
        qs = self.queryset
        stats = qs.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            resolved=Count('id', filter=Q(status='resolved')),
            timeout=Count('id', filter=Q(status='timeout')),
            avg_response=Avg('response_duration', filter=Q(response_duration__isnull=False)),
        )
        return Response(stats)


class EscalationRuleViewSet(viewsets.ModelViewSet):
    queryset = EscalationRule.objects.filter(is_deleted=False)
    serializer_class = EscalationRuleSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['priority']
    ordering_fields = ['priority', 'escalation_order']
