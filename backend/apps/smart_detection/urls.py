from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('vitals', views.VitalSignViewSet)
router.register('fall-alerts', views.FallAlertViewSet)
router.register('health-checks', views.HealthCheckRecordViewSet)
router.register('positions', views.PositionRecordViewSet)
router.register('detection-devices', views.DetectionDeviceViewSet)
router.register('alert-rules', views.AlertRuleViewSet)
router.register('alerts', views.AlertViewSet)
router.register('mqtt-mappings', views.MQTTDeviceMappingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
