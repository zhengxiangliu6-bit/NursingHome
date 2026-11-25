from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('broadcast/tasks', views.BroadcastTaskViewSet)
router.register('broadcast/zones', views.BroadcastZoneViewSet)
router.register('broadcast/devices', views.BroadcastDeviceViewSet)
router.register('broadcast/schedules', views.BroadcastScheduleViewSet)
router.register('broadcast/logs', views.BroadcastLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
