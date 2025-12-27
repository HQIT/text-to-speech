"""
text-to-speech: Text to speech conversion tool.
"""

from typing import List

from .client import TTSClient, TTSResult, TTSError, text_to_speech
from .providers import TTSProvider, StreamTTSProvider, VoiceInfo
from .registry import ProviderRegistry, registry

__version__ = "0.1.0"
__all__ = [
    "TTSClient", 
    "TTSResult", 
    "TTSError",
    "text_to_speech",
    "TTSProvider", 
    "StreamTTSProvider",
    "VoiceInfo",
    "ProviderRegistry",
    "registry",
    "list_voices",
    "register_provider",
]


def list_voices(provider_name: str = None) -> List[VoiceInfo]:
    """
    便捷函数：获取音色列表。
    
    Args:
        provider_name: 指定 Provider 名称，为空则获取所有
        
    Returns:
        音色信息列表
    """
    if provider_name:
        provider = registry.get(provider_name)
        return provider.list_voices() if provider else []
    return registry.list_all_voices()


def register_provider(name: str, provider: TTSProvider):
    """
    便捷函数：注册 Provider。
    
    Args:
        name: Provider 名称
        provider: Provider 实例
    """
    registry.register(name, provider)
