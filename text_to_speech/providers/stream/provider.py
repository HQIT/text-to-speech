"""
Stream TTS Provider - 流式 TTS 服务适配器
"""

import logging
import os
from typing import Iterator, List

import requests
from dotenv import load_dotenv

from ..base import TTSProvider, VoiceInfo

load_dotenv()
DEFAULT_URL = os.getenv("TTS_URL", "http://49.52.4.115:8002/tts_stream")

logger = logging.getLogger(__name__)


class StreamTTSProvider(TTSProvider):
    """
    流式 TTS 服务提供者。
    
    适配 POST 请求返回流式音频数据的 TTS 服务。
    
    Example:
        >>> provider = StreamTTSProvider(url="http://localhost:8002/tts_stream")
        >>> for chunk in provider.synthesize("你好", "xiaoyan"):
        ...     audio_data += chunk
    """
    
    def __init__(self, url: str = None, chunk_size: int = 4096):
        """
        初始化 Stream TTS Provider。
        
        Args:
            url: TTS 服务 URL，默认从 TTS_URL 环境变量获取
            chunk_size: 流式读取的块大小
        """
        self.url = url or DEFAULT_URL
        self.chunk_size = chunk_size
    
    def synthesize(self, text: str, spk_id: str) -> Iterator[bytes]:
        """
        调用流式 TTS 服务。
        
        Args:
            text: 要转换的文本
            spk_id: 说话人ID（hash_id），会自动转换为原始ID
            
        Yields:
            音频数据块
        """
        # 通过 hash_id 查找对应的原始 id
        voice_info = self.find_voice_by_hash_id(spk_id)
        original_id = voice_info.id if voice_info else spk_id
        
        data = {
            "text": text,
            "spk_id": original_id
        }
        
        response = requests.post(self.url, data=data, stream=True)
        response.raise_for_status()
        
        for chunk in response.iter_content(chunk_size=self.chunk_size):
            if chunk:
                yield chunk
    
    def list_voices(self) -> List[VoiceInfo]:
        """
        从 TTS 服务获取音色列表。
        
        Returns:
            音色信息列表
        """
        try:
            # 假设 TTS 服务提供 /voices 接口
            voices_url = self.url.rsplit('/', 1)[0] + '/voices'
            response = requests.get(voices_url, timeout=10)
            response.raise_for_status()
            
            voices = []
            for item in response.json():
                voices.append(VoiceInfo(
                    id=item.get('id', item.get('spk_id', '')),
                    name=item.get('name', item.get('title', '')),
                    provider="stream",
                    language=item.get('language', 'zh'),
                    gender=item.get('gender', ''),
                    sample_url=item.get('sample_url', ''),
                    description=item.get('description', '')
                ))
            return voices
        except Exception as e:
            logger.warning(f"Failed to list voices from {self.url}: {e}")
            return []
    
    @property
    def name(self) -> str:
        return "stream"

