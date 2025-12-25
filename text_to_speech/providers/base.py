"""
TTS Provider 基类
"""

from abc import ABC, abstractmethod
from typing import Iterator, Optional


class TTSProvider(ABC):
    """
    TTS 服务提供者基类。
    
    所有 TTS 服务适配器都应继承此类并实现 synthesize 方法。
    """
    
    @abstractmethod
    def synthesize(self, text: str, spk_id: str) -> Iterator[bytes]:
        """
        将文本转换为语音，返回音频数据流。
        
        Args:
            text: 要转换的文本
            spk_id: 说话人 ID
            
        Yields:
            音频数据块 (bytes)
        """
        pass
    
    @property
    def name(self) -> str:
        """Provider 名称"""
        return self.__class__.__name__

