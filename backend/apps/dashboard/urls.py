from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/overview/', views.OverviewView.as_view(), name='dashboard-overview'),
    path('dashboard/call-stats/', views.CallStatsView.as_view(), name='dashboard-call-stats'),
    path('dashboard/health-stats/', views.HealthStatsView.as_view(), name='dashboard-health-stats'),
    path('dashboard/patrol-stats/', views.PatrolStatsView.as_view(), name='dashboard-patrol-stats'),
]
