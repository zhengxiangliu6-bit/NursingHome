from channels.generic.websocket import AsyncJsonWebsocketConsumer


class PatrolConsumer(AsyncJsonWebsocketConsumer):
    """巡更实时追踪WebSocket消费者。"""

    async def connect(self):
        self.group_name = 'patrol'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def patrol_update(self, event):
        await self.send_json(event['data'])
