from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import IsStaff, IsAdmin
from .models import (
    PatrolCheckpoint, PatrolRoute, PatrolTask, PatrolRecord, PatrolException,
)
from .serializers import (
    PatrolCheckpointSerializer, PatrolRouteSerializer,
    PatrolTaskSerializer, PatrolTaskListSerializer,
    PatrolRecordSerializer, PatrolExceptionSerializer,
)


class PatrolCheckpointViewSet(viewsets.ModelViewSet):
    queryset = PatrolCheckpoint.objects.select_related('building').filter(is_deleted=False)
    serializer_class = PatrolCheckpointSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['building', 'is_active']


class PatrolRouteViewSet(viewsets.ModelViewSet):
    queryset = PatrolRoute.objects.prefetch_related('checkpoints').filter(is_deleted=False)
    serializer_class = PatrolRouteSerializer
    permission_classes = [IsAdmin]


class PatrolTaskViewSet(viewsets.ModelViewSet):
    queryset = PatrolTask.objects.select_related(
        'route', 'assigned_to'
    ).prefetch_related('records', 'exceptions').filter(is_deleted=False)
    permission_classes = [IsStaff]
    filterset_fields = ['status', 'assigned_to']
    ordering_fields = ['scheduled_start']

    def get_serializer_class(self):
        if self.action == 'list':
            return PatrolTaskListSerializer
        return PatrolTaskSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        """获取今日巡更任务。"""
        today = timezone.now().date()
        tasks = self.queryset.filter(scheduled_start__date=today)
        serializer = PatrolTaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def start(self, request, pk=None):
        task = self.get_object()
        task.status = 'in_progress'
        task.actual_start = timezone.now()
        task.save()
        return Response(PatrolTaskSerializer(task).data)

    @action(detail=True, methods=['patch'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = 'completed'
        task.actual_end = timezone.now()
        task.save()
        return Response(PatrolTaskSerializer(task).data)

    @action(detail=True, methods=['post'])
    def scan(self, request, pk=None):
        """巡更点扫描打卡。"""
        task = self.get_object()
        serializer = PatrolRecordSerializer(data={
            'task': task.id,
            'checkpoint': request.data.get('checkpoint'),
            'scanned_at': timezone.now().isoformat(),
            'notes': request.data.get('notes', ''),
            'location_x': request.data.get('location_x'),
            'location_y': request.data.get('location_y'),
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='exception')
    def report_exception(self, request, pk=None):
        """上报巡更异常。"""
        task = self.get_object()
        serializer = PatrolExceptionSerializer(data={
            'task': task.id,
            **request.data,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        from django.db.models import Count, Q
        stats = self.queryset.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            missed=Count('id', filter=Q(status='missed')),
            in_progress=Count('id', filter=Q(status='in_progress')),
        )
        if stats['total'] > 0:
            stats['completion_rate'] = round(stats['completed'] / stats['total'] * 100, 1)
        else:
            stats['completion_rate'] = 0
        return Response(stats)
