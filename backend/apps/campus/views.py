from django.utils import timezone
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import IsAdmin, IsStaff
from .models import Building, Area, Device, DeviceMaintenanceLog, Notice
from .serializers import (
    BuildingSerializer, AreaSerializer, DeviceSerializer,
    DeviceMaintenanceLogSerializer, NoticeSerializer,
)


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.filter(is_deleted=False)
    serializer_class = BuildingSerializer
    permission_classes = [IsAdmin]


class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.select_related('building').filter(is_deleted=False)
    serializer_class = AreaSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['building', 'floor', 'area_type']


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related('building', 'area').filter(is_deleted=False)
    serializer_class = DeviceSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['device_category', 'status', 'building']
    search_fields = ['name', 'device_sn']

    @action(detail=True, methods=['post'])
    def maintenance(self, request, pk=None):
        """记录设备维护。"""
        device = self.get_object()
        serializer = DeviceMaintenanceLogSerializer(data={
            'device': device.id,
            'maintained_by': request.user.id,
            **request.data,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        device.last_maintenance = timezone.now().date()
        device.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='status-summary')
    def status_summary(self, request):
        """设备状态统计。"""
        summary = self.queryset.values('status').annotate(count=Count('id'))
        category_summary = self.queryset.values('device_category').annotate(count=Count('id'))
        return Response({
            'by_status': list(summary),
            'by_category': list(category_summary),
        })


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.select_related('author').filter(is_deleted=False)
    serializer_class = NoticeSerializer
    permission_classes = [IsStaff]
    filterset_fields = ['notice_type', 'is_published']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'publish']:
            return [IsAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['patch'])
    def publish(self, request, pk=None):
        notice = self.get_object()
        notice.is_published = True
        notice.published_at = timezone.now()
        notice.save()
        return Response(NoticeSerializer(notice).data)
