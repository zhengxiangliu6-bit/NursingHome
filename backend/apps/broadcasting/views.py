from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import IsAdmin, IsNurseOrAbove
from .models import BroadcastZone, BroadcastDevice, BroadcastTask, BroadcastSchedule, BroadcastLog
from .serializers import (
    BroadcastZoneSerializer, BroadcastDeviceSerializer,
    BroadcastTaskSerializer, BroadcastScheduleSerializer, BroadcastLogSerializer,
)


class BroadcastZoneViewSet(viewsets.ModelViewSet):
    queryset = BroadcastZone.objects.select_related('building').filter(is_deleted=False)
    serializer_class = BroadcastZoneSerializer
    permission_classes = [IsAdmin]


class BroadcastDeviceViewSet(viewsets.ModelViewSet):
    queryset = BroadcastDevice.objects.select_related('zone').filter(is_deleted=False)
    serializer_class = BroadcastDeviceSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['zone', 'status']


class BroadcastTaskViewSet(viewsets.ModelViewSet):
    queryset = BroadcastTask.objects.select_related('created_by_user').filter(is_deleted=False)
    serializer_class = BroadcastTaskSerializer
    permission_classes = [IsNurseOrAbove]
    filterset_fields = ['broadcast_type', 'status']

    def perform_create(self, serializer):
        serializer.save(created_by_user=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        task = self.get_object()
        task.status = 'broadcasting'
        task.started_at = timezone.now()
        task.save()
        BroadcastLog.objects.create(task=task, action='started')
        return Response(BroadcastTaskSerializer(task).data)

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        task = self.get_object()
        task.status = 'completed'
        task.ended_at = timezone.now()
        task.save()
        BroadcastLog.objects.create(task=task, action='stopped')
        return Response(BroadcastTaskSerializer(task).data)


class BroadcastScheduleViewSet(viewsets.ModelViewSet):
    queryset = BroadcastSchedule.objects.filter(is_deleted=False)
    serializer_class = BroadcastScheduleSerializer
    permission_classes = [IsAdmin]


class BroadcastLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BroadcastLog.objects.select_related('task', 'device').filter(is_deleted=False)
    serializer_class = BroadcastLogSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['task', 'action']
