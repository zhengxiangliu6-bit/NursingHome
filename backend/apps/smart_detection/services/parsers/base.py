from abc import ABC, abstractmethod


class BaseDeviceParser(ABC):
    """设备数据解析器基类。"""

    @abstractmethod
    def parse(self, topic, payload, device):
        """
        解析MQTT消息载荷。

        Args:
            topic: MQTT topic字符串
            payload: 原始字节数据
            device: DetectionDevice实例

        Returns:
            list of dict, 每个dict格式:
            {
                'type': 'vital_sign' | 'position' | 'fall_alarm' | 'sos' |
                        'bed_exit' | 'heartbeat',
                'data': { ... 解析后的字段 ... },
                'timestamp': datetime or None
            }
        """
        pass
