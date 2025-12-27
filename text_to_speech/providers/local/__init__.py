"""
Local TTS Provider - 使用系统自带的TTS引擎（pyttsx3）
"""

try:
    from .provider import LocalTTSProvider
    __all__ = ["LocalTTSProvider"]
except ImportError:
    __all__ = []

