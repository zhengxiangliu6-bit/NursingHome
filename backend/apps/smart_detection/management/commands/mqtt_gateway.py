import signal
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = '启动MQTT物联网设备网关服务'

    def add_arguments(self, parser):
        parser.add_argument(
            '--broker', default=settings.MQTT_BROKER_HOST,
            help=f'MQTT Broker地址 (默认: {settings.MQTT_BROKER_HOST})'
        )
        parser.add_argument(
            '--port', type=int, default=settings.MQTT_BROKER_PORT,
            help=f'MQTT Broker端口 (默认: {settings.MQTT_BROKER_PORT})'
        )

    def handle(self, *args, **options):
        from apps.smart_detection.services.mqtt_client import MQTTGatewayClient

        broker = options['broker']
        port = options['port']

        self.stdout.write(self.style.SUCCESS(
            f'正在启动MQTT网关... Broker: {broker}:{port}'
        ))

        client = MQTTGatewayClient(broker=broker, port=port)

        # 优雅退出
        def shutdown(signum, frame):
            self.stdout.write(self.style.WARNING('收到退出信号，正在关闭...'))
            client.client.disconnect()

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        try:
            client.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('MQTT网关已停止'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'MQTT网关异常: {e}'))
            raise
