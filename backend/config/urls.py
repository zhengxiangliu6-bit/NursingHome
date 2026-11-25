from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.residents.urls')),
    path('api/v1/', include('apps.call_response.urls')),
    path('api/v1/', include('apps.smart_detection.urls')),
    path('api/v1/', include('apps.patrol.urls')),
    path('api/v1/', include('apps.broadcasting.urls')),
    path('api/v1/', include('apps.campus.urls')),
    path('api/v1/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
