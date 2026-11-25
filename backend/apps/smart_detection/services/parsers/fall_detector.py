import json
import logging
from datetime import datetime
from django.utils import timezone
from .base import BaseDeviceParser

logger = logging.getLogger(__name__)


class FallDetectorParser(BaseDeviceParser):
    """
    跌倒雷达/AI摄像头数据解析器。

    期望JSON格式:
    {
        "event": "fall_detected",
        "confidence": 0.92,
        "x": 50.1,
        "y": 30.2,
        "floor": 2,
        "image_url": "http://...",
        "timestamp": "2026-03-17T10:30:00"
    }
    """

    def parse(self, topic, payload, device):
        try:
            data = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning(f'跌倒检测 {device.device_sn}: 无法解析载荷')
            return []

        results = []
        ts = self._parse_timestamp(data.get('timestamp'))

        # 心跳
        results.append({
            'type': 'heartbeat',
            'data': {},
            'timestamp': ts,
        })

        event = data.get('event', '')
        if event in ('fall_detected', 'fall_alarm', 'fall'):
            confidence = data.get('confidence', 0)
            severity = 'confirmed' if confidence >= 0.8 else 'suspected'
            results.append({
                'type': 'fall_alarm',
                'data': {
                    'confidence': confidence,
                    'severity': severity,
                    'x': data.get('x'),
                    'y': data.get('y'),
                    'floor': data.get('floor'),
                    'image_url': data.get('image_url', ''),
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
