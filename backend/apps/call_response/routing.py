from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/calls/', consumers.CallConsumer.as_asgi()),
    path('ws/alerts/', consumers.AlertConsumer.as_asgi()),
]
