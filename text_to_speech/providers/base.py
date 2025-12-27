"""
TTS Provider 基类
"""

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator, List, Optional


def _generate_hash_id(provider: str, original_id: str, language: str) -> str:
    """生成基于 provider、原始 ID 和语言的 hash ID"""
    content = f"{provider}:{original_id}:{language}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]


@dataclass
class VoiceInfo:
    """音色信息"""
    id: str                    # 音色 ID (spk_id)，原始 ID
    name: str                  # 显示名称
    provider: str = ""         # Provider 名称
    language: str = "zh"       # 语言
    gender: str = ""           # 性别 (male/female)
    sample_url: str = ""       # 试听 URL
    description: str = ""      # 描述
    hash_id: str = field(default="", init=False)  # Hash ID，用于避免特殊字符
    
    def __post_init__(self):
        """初始化后生成 hash_id（基于 provider + voice_id + language）"""
        if not self.hash_id:
            self.hash_id = _generate_hash_id(self.provider, self.id, self.language)


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
            spk_id: 说话人 ID (hash_id)
            
        Yields:
            音频数据块 (bytes)
        """
        pass
    
    def list_voices(self) -> List[VoiceInfo]:
        """
        获取可用音色列表。
        
        Returns:
            音色信息列表
        """
        return []
    
    def find_voice_by_hash_id(self, hash_id: str) -> Optional[VoiceInfo]:
        """通过 hash_id 查找对应的 VoiceInfo"""
        for voice_info in self.list_voices():
            if voice_info.hash_id.lower() == hash_id.lower():
                return voice_info
        return None
    
    @property
    def name(self) -> str:
        """Provider 名称"""
        return self.__class__.__name__

