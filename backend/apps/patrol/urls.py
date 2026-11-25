from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('patrol/checkpoints', views.PatrolCheckpointViewSet)
router.register('patrol/routes', views.PatrolRouteViewSet)
router.register('patrol/tasks', views.PatrolTaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
