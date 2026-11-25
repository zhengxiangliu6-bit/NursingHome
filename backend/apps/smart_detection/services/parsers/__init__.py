from .smart_mattress import SmartMattressParser
from .wristband import WristbandParser
from .fall_detector import FallDetectorParser

PARSER_REGISTRY = {
    'smart_mattress': SmartMattressParser,
    'wristband': WristbandParser,
    'fall_radar': FallDetectorParser,
    'fall_camera': FallDetectorParser,
}


def get_parser(protocol_type):
    """根据协议类型获取解析器实例。"""
    parser_cls = PARSER_REGISTRY.get(protocol_type)
    if parser_cls:
        return parser_cls()
    return None
