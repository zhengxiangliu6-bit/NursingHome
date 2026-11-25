from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


class CallConsumer(AsyncJsonWebsocketConsumer):
    """呼叫实时推送WebSocket消费者，支持角色分组路由。"""

    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or self.user.is_anonymous:
            await self.close()
            return

        self.groups_joined = []
        user_info = await self._get_user_info()
        self.user_role = user_info['role']
        self.user_building_id = user_info['building_id']

        # 个人频道（定向通知）
        personal_group = f"calls_user_{self.user.id}"
        await self.channel_layer.group_add(personal_group, self.channel_name)
        self.groups_joined.append(personal_group)

        # 角色分组
        if self.user_role in ('super_admin', 'admin', 'nurse', 'doctor'):
            await self.channel_layer.group_add('calls_all', self.channel_name)
            self.groups_joined.append('calls_all')
        elif self.user_role == 'care_worker' and self.user_building_id:
            building_group = f"calls_building_{self.user_building_id}"
            await self.channel_layer.group_add(building_group, self.channel_name)
            self.groups_joined.append(building_group)

        await self.accept()

        # 推送当前活跃呼叫
        active_calls = await self._get_active_calls()
        await self.send_json({
            'type': 'init',
            'data': {'active_calls': active_calls, 'role': self.user_role}
        })

    async def disconnect(self, close_code):
        for group in getattr(self, 'groups_joined', []):
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive_json(self, content):
        msg_type = content.get('type')
        if msg_type == 'ping':
            await self.send_json({'type': 'pong'})

    # --- channel layer 消息处理器 ---
    async def call_new(self, event):
        await self.send_json({'type': 'new_call', 'data': event['data']})

    async def call_accepted(self, event):
        await self.send_json({'type': 'call_accepted', 'data': event['data']})

    async def call_resolved(self, event):
        await self.send_json({'type': 'call_resolved', 'data': event['data']})

    async def call_cancelled(self, event):
        await self.send_json({'type': 'call_cancelled', 'data': event['data']})

    async def call_escalated(self, event):
        await self.send_json({'type': 'call_escalated', 'data': event['data']})

    async def call_timeout(self, event):
        await self.send_json({'type': 'call_timeout', 'data': event['data']})

    # --- 数据库查询辅助 ---
    @database_sync_to_async
    def _get_user_info(self):
        role_name = self.user.role.name if self.user.role else ''
        building_id = None
        try:
            profile = self.user.staff_profile
            if profile and profile.assigned_building:
                building_id = str(profile.assigned_building.id)
        except Exception:
            pass
        return {'role': role_name, 'building_id': building_id}

    @database_sync_to_async
    def _get_active_calls(self):
        from .models import CallRecord
        from .serializers import CallRecordListSerializer
        qs = CallRecord.objects.filter(
            status__in=['pending', 'accepted', 'in_progress'],
            is_deleted=False
        ).select_related('caller_resident').order_by('-priority', 'call_time')
        if self.user_role == 'care_worker' and self.user_building_id:
            qs = qs.filter(building_id=self.user_building_id)
        return CallRecordListSerializer(qs, many=True).data


class AlertConsumer(AsyncJsonWebsocketConsumer):
    """告警推送WebSocket消费者（跌倒/体征异常/IoT告警）。"""

    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or self.user.is_anonymous:
            await self.close()
            return

        self.group_name = 'alerts'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            getattr(self, 'group_name', 'alerts'), self.channel_name
        )

    async def alert_update(self, event):
        await self.send_json(event['data'])
