from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('campus/buildings', views.BuildingViewSet)
router.register('campus/areas', views.AreaViewSet)
router.register('campus/devices', views.DeviceViewSet)
router.register('campus/notices', views.NoticeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
