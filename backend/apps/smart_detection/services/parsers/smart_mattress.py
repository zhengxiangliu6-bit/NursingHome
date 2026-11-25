import json
import logging
from datetime import datetime
from django.utils import timezone
from .base import BaseDeviceParser

logger = logging.getLogger(__name__)


class SmartMattressParser(BaseDeviceParser):
    """
    智能床垫数据解析器。

    期望JSON格式:
    {
        "heart_rate": 72,
        "respiratory_rate": 18,
        "bed_status": "in_bed" | "out_of_bed",
        "body_movement": 0-100,
        "battery": 85,
        "timestamp": "2026-03-17T10:30:00"
    }
    """

    def parse(self, topic, payload, device):
        try:
            data = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning(f'智能床垫 {device.device_sn}: 无法解析载荷')
            return []

        results = []
        ts = self._parse_timestamp(data.get('timestamp'))

        # 心跳/电量更新
        results.append({
            'type': 'heartbeat',
            'data': {'battery': data.get('battery')},
            'timestamp': ts,
        })

        # 体征数据
        hr = data.get('heart_rate')
        rr = data.get('respiratory_rate')
        if hr is not None or rr is not None:
            results.append({
                'type': 'vital_sign',
                'data': {
                    'heart_rate': hr,
                    'respiratory_rate': rr,
                },
                'timestamp': ts,
            })

        # 离床检测
        bed_status = data.get('bed_status')
        if bed_status == 'out_of_bed':
            results.append({
                'type': 'bed_exit',
                'data': {'body_movement': data.get('body_movement')},
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
