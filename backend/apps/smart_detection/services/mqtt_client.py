import json
import logging
import threading
import time

import paho.mqtt.client as mqtt
from django.conf import settings

logger = logging.getLogger(__name__)


class MQTTGatewayClient:
    """MQTT物联网网关客户端 -- 连接EMQX并分发设备消息。"""

    def __init__(self, broker=None, port=None):
        self.broker = broker or settings.MQTT_BROKER_HOST
        self.port = port or settings.MQTT_BROKER_PORT
        self.prefix = settings.MQTT_TOPIC_PREFIX
        self.client_id = settings.MQTT_CLIENT_ID

        self._device_cache = {}  # topic -> (device, parser)
        self._cache_lock = threading.Lock()
        self._last_cache_refresh = 0

        self.client = mqtt.Client(
            client_id=self.client_id,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )
        if settings.MQTT_USERNAME:
            self.client.username_pw_set(
                settings.MQTT_USERNAME, settings.MQTT_PASSWORD
            )

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def start(self):
        """阻塞运行：连接broker并进入消息循环。"""
        self._refresh_device_cache()
        logger.info(f'连接MQTT Broker: {self.broker}:{self.port}')
        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.loop_forever()

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        logger.info(f'MQTT已连接, reason_code={reason_code}')
        # 订阅通配符topic
        data_topic = f'{self.prefix}/+/data'
        alarm_topic = f'{self.prefix}/+/alarm'
        client.subscribe(data_topic)
        client.subscribe(alarm_topic)
        logger.info(f'已订阅: {data_topic}, {alarm_topic}')

    def _on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        logger.warning(f'MQTT断开连接, reason_code={reason_code}, 将自动重连...')

    def _on_message(self, client, userdata, msg):
        """处理收到的MQTT消息。"""
        topic = msg.topic
        payload = msg.payload

        try:
            # 定期刷新缓存
            now = time.time()
            if now - self._last_cache_refresh > 60:
                self._refresh_device_cache()

            # 从topic提取device_sn: {prefix}/{sn}/data 或 {prefix}/{sn}/alarm
            parts = topic.split('/')
            if len(parts) < 3:
                return
            device_sn = parts[-2]

            device, parser = self._get_device_parser(device_sn)
            if not device or not parser:
                logger.debug(f'未找到设备映射: {device_sn}')
                return

            # 解析
            parsed_results = parser.parse(topic, payload, device)
            if not parsed_results:
                return

            # 数据管道处理
            from .data_pipeline import data_pipeline
            data_pipeline.process(parsed_results, device)

        except Exception:
            logger.exception(f'处理MQTT消息失败: topic={topic}')

    def _get_device_parser(self, device_sn):
        """根据设备序列号获取设备和解析器（带缓存）。"""
        with self._cache_lock:
            cached = self._device_cache.get(device_sn)
            if cached:
                return cached

        # 缓存未命中，从数据库查找
        from ..models import MQTTDeviceMapping
        from .parsers import get_parser

        try:
            mapping = MQTTDeviceMapping.objects.select_related(
                'detection_device', 'detection_device__bound_resident'
            ).get(
                detection_device__device_sn=device_sn,
                is_deleted=False
            )
        except MQTTDeviceMapping.DoesNotExist:
            return None, None

        device = mapping.detection_device
        parser = get_parser(mapping.protocol_type)

        if parser:
            with self._cache_lock:
                self._device_cache[device_sn] = (device, parser)

        return device, parser

    def _refresh_device_cache(self):
        """刷新设备映射缓存。"""
        from ..models import MQTTDeviceMapping
        from .parsers import get_parser

        try:
            mappings = MQTTDeviceMapping.objects.select_related(
                'detection_device', 'detection_device__bound_resident'
            ).filter(is_deleted=False)

            new_cache = {}
            for mapping in mappings:
                parser = get_parser(mapping.protocol_type)
                if parser:
                    new_cache[mapping.detection_device.device_sn] = (
                        mapping.detection_device, parser
                    )

            with self._cache_lock:
                self._device_cache = new_cache

            self._last_cache_refresh = time.time()
            logger.info(f'设备缓存已刷新，共 {len(new_cache)} 个设备')
        except Exception:
            logger.exception('刷新设备缓存失败')
