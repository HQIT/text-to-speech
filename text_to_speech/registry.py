"""
TTS Provider Registry - 管理多个 TTS Provider
"""

import logging
from typing import Dict, List, Optional

from .providers.base import TTSProvider, VoiceInfo

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """TTS Provider 注册表，管理多个 Provider"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers: Dict[str, TTSProvider] = {}
        return cls._instance
    
    def register(self, name: str, provider: TTSProvider):
        """注册 Provider"""
        self._providers[name] = provider
        logger.info(f"Registered TTS provider: {name}")
    
    def unregister(self, name: str):
        """注销 Provider"""
        if name in self._providers:
            del self._providers[name]
            logger.info(f"Unregistered TTS provider: {name}")
    
    def get(self, name: str) -> Optional[TTSProvider]:
        """获取指定 Provider"""
        return self._providers.get(name)
    
    def list_providers(self) -> List[str]:
        """获取所有 Provider 名称"""
        return list(self._providers.keys())
    
    def list_all_voices(self) -> List[VoiceInfo]:
        """获取所有 Provider 的音色列表"""
        voices = []
        for name, provider in self._providers.items():
            try:
                for voice in provider.list_voices():
                    voice.provider = name
                    voices.append(voice)
            except Exception as e:
                logger.warning(f"Failed to get voices from {name}: {e}")
        return voices
    
    def synthesize(self, text: str, spk_id: str, provider_name: str = None) -> bytes:
        """
        合成语音，可指定 Provider。
        
        Args:
            text: 要转换的文本
            spk_id: 说话人 ID
            provider_name: Provider 名称，为空则使用第一个
            
        Returns:
            音频数据 (bytes)
        """
        if provider_name:
            provider = self.get(provider_name)
            if not provider:
                raise ValueError(f"Provider not found: {provider_name}")
        else:
            # 使用第一个 Provider
            provider = next(iter(self._providers.values()), None)
            if not provider:
                raise ValueError("No provider registered")
        
        audio = b''
        for chunk in provider.synthesize(text, spk_id):
            audio += chunk
        return audio


# 全局单例
registry = ProviderRegistry()

