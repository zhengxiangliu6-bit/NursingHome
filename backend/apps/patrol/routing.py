from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/patrol/', consumers.PatrolConsumer.as_asgi()),
]
