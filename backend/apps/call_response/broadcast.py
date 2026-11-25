from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_call_event(signal_type, data, building_id=None):
    """
    向相关WebSocket组广播呼叫事件。

    signal_type: call_new / call_accepted / call_resolved /
                 call_cancelled / call_escalated / call_timeout
    data: 序列化后的呼叫数据字典
    building_id: 如有值，同时广播到楼栋专属组
    """
    channel_layer = get_channel_layer()
    send = async_to_sync(channel_layer.group_send)

    payload = {'type': signal_type, 'data': data}

    # 广播到全局组（admin/nurse/doctor 订阅）
    send('calls_all', payload)

    # 广播到楼栋专属组（care_worker 订阅）
    if building_id:
        send(f'calls_building_{building_id}', payload)
