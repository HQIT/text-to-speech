"""
TTS Providers - 不同 TTS 服务的适配器
"""

from .base import TTSProvider, VoiceInfo
from .stream import StreamTTSProvider

try:
    from .local import LocalTTSProvider
    __all__ = ["TTSProvider", "StreamTTSProvider", "LocalTTSProvider", "VoiceInfo"]
except ImportError:
    __all__ = ["TTSProvider", "StreamTTSProvider", "VoiceInfo"]

