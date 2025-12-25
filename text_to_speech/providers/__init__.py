"""
TTS Providers - 不同 TTS 服务的适配器
"""

from .base import TTSProvider
from .stream import StreamTTSProvider

__all__ = ["TTSProvider", "StreamTTSProvider"]

