"""
Stream TTS Provider - 流式 TTS 服务适配器
"""

import os
from typing import Iterator

import requests
from dotenv import load_dotenv

from .base import TTSProvider

load_dotenv()
DEFAULT_URL = os.getenv("TTS_URL", "http://49.52.4.115:8002/tts_stream")


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
            spk_id: 说话人 ID
            
        Yields:
            音频数据块
        """
        data = {
            "text": text,
            "spk_id": spk_id
        }
        
        response = requests.post(self.url, data=data, stream=True)
        response.raise_for_status()
        
        for chunk in response.iter_content(chunk_size=self.chunk_size):
            if chunk:
                yield chunk
    
    @property
    def name(self) -> str:
        return "stream"

