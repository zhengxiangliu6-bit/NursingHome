from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.common.permissions import IsAdmin, IsStaff
from apps.residents.models import Resident, Room, Bed
from apps.call_response.models import CallRecord
from apps.smart_detection.models import FallAlert, VitalSign
from apps.patrol.models import PatrolTask
from apps.campus.models import Device


class OverviewView(APIView):
    """综合看板概览。"""
    permission_classes = [IsStaff]

    def get(self, request):
        today = timezone.now().date()
        return Response({
            'residents': {
                'total': Resident.objects.filter(status='active', is_deleted=False).count(),
                'new_today': Resident.objects.filter(
                    admission_date=today, is_deleted=False
                ).count(),
            },
            'calls': {
                'active': CallRecord.objects.filter(
                    status__in=['pending', 'accepted', 'in_progress'], is_deleted=False
                ).count(),
                'today_total': CallRecord.objects.filter(
                    call_time__date=today, is_deleted=False
                ).count(),
            },
            'alerts': {
                'active': FallAlert.objects.filter(
                    status__in=['alerting', 'responding'], is_deleted=False
                ).count(),
                'today_total': FallAlert.objects.filter(
                    alert_time__date=today, is_deleted=False
                ).count(),
            },
            'devices': {
                'online': Device.objects.filter(status='online', is_deleted=False).count(),
                'offline': Device.objects.filter(status='offline', is_deleted=False).count(),
                'fault': Device.objects.filter(status='fault', is_deleted=False).count(),
            },
            'occupancy': {
                'total_beds': Bed.objects.filter(is_deleted=False).count(),
                'occupied_beds': Bed.objects.filter(status='occupied', is_deleted=False).count(),
            },
        })


class CallStatsView(APIView):
    """呼叫统计图表数据。"""
    permission_classes = [IsAdmin]

    def get(self, request):
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        daily_stats = []
        for i in range(days):
            day = (since + timedelta(days=i + 1)).date()
            qs = CallRecord.objects.filter(call_time__date=day, is_deleted=False)
            daily_stats.append({
                'date': str(day),
                'total': qs.count(),
                'emergency': qs.filter(priority='emergency').count(),
                'avg_response': qs.aggregate(
                    avg=Avg('response_duration')
                )['avg'] or 0,
            })
        return Response(daily_stats)


class HealthStatsView(APIView):
    """健康统计。"""
    permission_classes = [IsStaff]

    def get(self, request):
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        abnormal_count = VitalSign.objects.filter(
            is_abnormal=True, measured_at__date__gte=week_ago, is_deleted=False
        ).count()
        fall_count = FallAlert.objects.filter(
            alert_time__date__gte=week_ago, is_deleted=False
        ).count()
        return Response({
            'abnormal_vitals_week': abnormal_count,
            'fall_alerts_week': fall_count,
        })


class PatrolStatsView(APIView):
    """巡更统计。"""
    permission_classes = [IsAdmin]

    def get(self, request):
        today = timezone.now().date()
        today_tasks = PatrolTask.objects.filter(
            scheduled_start__date=today, is_deleted=False
        )
        total = today_tasks.count()
        completed = today_tasks.filter(status='completed').count()
        return Response({
            'today_total': total,
            'today_completed': completed,
            'completion_rate': round(completed / total * 100, 1) if total > 0 else 0,
        })
