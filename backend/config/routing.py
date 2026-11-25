from apps.call_response.routing import websocket_urlpatterns as call_ws
from apps.patrol.routing import websocket_urlpatterns as patrol_ws

websocket_urlpatterns = call_ws + patrol_ws
