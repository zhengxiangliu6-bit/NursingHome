from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('calls', views.CallRecordViewSet)
router.register('call-devices', views.CallDeviceViewSet)
router.register('escalation-rules', views.EscalationRuleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
