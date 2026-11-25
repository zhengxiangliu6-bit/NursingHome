from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('residents', views.ResidentViewSet)
router.register('care-levels', views.CareLevelViewSet)
router.register('assessments', views.CareAssessmentViewSet)
router.register('rooms', views.RoomViewSet)
router.register('beds', views.BedViewSet)
router.register('admission-applications', views.AdmissionApplicationViewSet)
router.register('resident-leaves', views.ResidentLeaveViewSet)
router.register('bed-transfers', views.BedTransferViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
