import json
import logging
from datetime import datetime
from django.utils import timezone
from .base import BaseDeviceParser

logger = logging.getLogger(__name__)


class WristbandParser(BaseDeviceParser):
    """
    手环/定位卡数据解析器。

    期望JSON格式:
    {
        "x": 120.5,
        "y": 45.2,
        "floor": 3,
        "sos": false,
        "heart_rate": 75,
        "blood_oxygen": 98.5,
        "battery": 60,
        "timestamp": "2026-03-17T10:30:00"
    }
    """

    def parse(self, topic, payload, device):
        try:
            data = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning(f'手环 {device.device_sn}: 无法解析载荷')
            return []

        results = []
        ts = self._parse_timestamp(data.get('timestamp'))

        # 心跳/电量
        results.append({
            'type': 'heartbeat',
            'data': {'battery': data.get('battery')},
            'timestamp': ts,
        })

        # 定位数据
        x = data.get('x')
        y = data.get('y')
        if x is not None and y is not None:
            results.append({
                'type': 'position',
                'data': {
                    'x': float(x),
                    'y': float(y),
                    'floor': data.get('floor', 1),
                },
                'timestamp': ts,
            })

        # 体征（手环可能含心率/血氧）
        hr = data.get('heart_rate')
        spo2 = data.get('blood_oxygen')
        if hr is not None or spo2 is not None:
            results.append({
                'type': 'vital_sign',
                'data': {
                    'heart_rate': hr,
                    'blood_oxygen': spo2,
                },
                'timestamp': ts,
            })

        # SOS按钮
        if data.get('sos'):
            results.append({
                'type': 'sos',
                'data': {
                    'x': x, 'y': y,
                    'floor': data.get('floor', 1),
                },
                'timestamp': ts,
            })

        return results

    def _parse_timestamp(self, ts_str):
        if not ts_str:
            return timezone.now()
        try:
            dt = datetime.fromisoformat(ts_str)
            if dt.tzinfo is None:
                dt = timezone.make_aware(dt)
            return dt
        except (ValueError, TypeError):
            return timezone.now()
