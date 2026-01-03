"""
TTS Providers - 不同 TTS 服务的适配器
"""

from .base import TTSProvider, VoiceInfo
from .stream import StreamTTSProvider
from .edge import EdgeTTSProvider

__all__ = ["TTSProvider", "StreamTTSProvider", "EdgeTTSProvider", "VoiceInfo"]
