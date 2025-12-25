"""
text-to-speech: Text to speech conversion tool.
"""

from .client import TTSClient, TTSResult, TTSError, text_to_speech
from .providers import TTSProvider, StreamTTSProvider

__version__ = "0.1.0"
__all__ = [
    "TTSClient", 
    "TTSResult", 
    "TTSError",
    "text_to_speech",
    "TTSProvider", 
    "StreamTTSProvider"
]
