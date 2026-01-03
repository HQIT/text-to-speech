"""
Edge TTS Provider - 使用微软 Edge TTS（免费，无需注册）
"""

import asyncio
import logging
import tempfile
import os
from typing import Iterator, List

try:
    import edge_tts
except ImportError:
    edge_tts = None

from ..base import TTSProvider, VoiceInfo

logger = logging.getLogger(__name__)

# 常用中文音色
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"

# 预定义音色列表（避免每次都查询）
PRESET_VOICES = [
    {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓", "language": "zh", "gender": "female"},
    {"id": "zh-CN-YunxiNeural", "name": "云希", "language": "zh", "gender": "male"},
    {"id": "zh-CN-YunjianNeural", "name": "云健", "language": "zh", "gender": "male"},
    {"id": "zh-CN-XiaoyiNeural", "name": "晓伊", "language": "zh", "gender": "female"},
    {"id": "zh-CN-YunyangNeural", "name": "云扬", "language": "zh", "gender": "male"},
    {"id": "zh-CN-XiaochenNeural", "name": "晓辰", "language": "zh", "gender": "female"},
    {"id": "zh-CN-XiaohanNeural", "name": "晓涵", "language": "zh", "gender": "female"},
    {"id": "zh-CN-XiaomengNeural", "name": "晓梦", "language": "zh", "gender": "female"},
    {"id": "zh-CN-XiaomoNeural", "name": "晓墨", "language": "zh", "gender": "female"},
    {"id": "zh-CN-XiaoqiuNeural", "name": "晓秋", "language": "zh", "gender": "female"},
    {"id": "zh-CN-XiaoruiNeural", "name": "晓睿", "language": "zh", "gender": "female"},
    {"id": "zh-CN-XiaoshuangNeural", "name": "晓双", "language": "zh", "gender": "female"},
    {"id": "zh-CN-XiaoxuanNeural", "name": "晓萱", "language": "zh", "gender": "female"},
    {"id": "zh-CN-XiaoyanNeural", "name": "晓颜", "language": "zh", "gender": "female"},
    {"id": "zh-CN-XiaoyouNeural", "name": "晓悠", "language": "zh", "gender": "female"},
    {"id": "zh-CN-YunfengNeural", "name": "云枫", "language": "zh", "gender": "male"},
    {"id": "zh-CN-YunhaoNeural", "name": "云皓", "language": "zh", "gender": "male"},
    {"id": "zh-CN-YunxiaNeural", "name": "云夏", "language": "zh", "gender": "male"},
    {"id": "zh-CN-YunyeNeural", "name": "云野", "language": "zh", "gender": "male"},
    {"id": "zh-CN-YunzeNeural", "name": "云泽", "language": "zh", "gender": "male"},
    {"id": "en-US-JennyNeural", "name": "Jenny", "language": "en", "gender": "female"},
    {"id": "en-US-GuyNeural", "name": "Guy", "language": "en", "gender": "male"},
]


class EdgeTTSProvider(TTSProvider):
    """
    Edge TTS Provider - 使用微软免费 TTS 服务。
    
    特点：
    - 免费，无需注册
    - 中文语音质量好
    - 需要网络连接
    
    Example:
        >>> provider = EdgeTTSProvider()
        >>> for chunk in provider.synthesize("你好世界", "zh-CN-XiaoxiaoNeural"):
        ...     audio_data += chunk
    """
    
    def __init__(self, default_voice: str = DEFAULT_VOICE):
        """
        初始化 Edge TTS Provider
        
        Args:
            default_voice: 默认音色 ID
        """
        if edge_tts is None:
            raise ImportError(
                "edge-tts is required for EdgeTTSProvider. "
                "Install it with: pip install edge-tts"
            )
        self.default_voice = default_voice
    
    def synthesize(self, text: str, spk_id: str) -> Iterator[bytes]:
        """
        使用 Edge TTS 合成语音。
        
        Args:
            text: 要转换的文本
            spk_id: 音色 ID（如 zh-CN-XiaoxiaoNeural）或 hash_id
            
        Yields:
            音频数据块（MP3格式）
        """
        # 查找音色
        voice = self._resolve_voice(spk_id)
        
        logger.info(f"Edge TTS: voice={voice}, text={text[:20]}...")
        
        # 同步包装异步调用
        audio_data = asyncio.get_event_loop().run_until_complete(
            self._synthesize_async(text, voice)
        )
        
        yield audio_data
    
    async def _synthesize_async(self, text: str, voice: str) -> bytes:
        """异步合成语音"""
        communicate = edge_tts.Communicate(text, voice)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            await communicate.save(tmp_path)
            
            with open(tmp_path, 'rb') as f:
                return f.read()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _resolve_voice(self, spk_id: str) -> str:
        """解析音色 ID"""
        if not spk_id or spk_id == "default":
            return self.default_voice
        
        # 如果是完整的 voice ID（如 zh-CN-XiaoxiaoNeural）
        if "-" in spk_id and "Neural" in spk_id:
            return spk_id
        
        # 尝试通过 hash_id 查找
        voice_info = self.find_voice_by_hash_id(spk_id)
        if voice_info:
            return voice_info.id
        
        # 尝试通过名称匹配
        for v in PRESET_VOICES:
            if spk_id.lower() in v["name"].lower() or spk_id.lower() in v["id"].lower():
                return v["id"]
        
        return self.default_voice
    
    def list_voices(self) -> List[VoiceInfo]:
        """
        获取可用的音色列表。
        
        Returns:
            音色信息列表
        """
        voices = []
        for v in PRESET_VOICES:
            voices.append(VoiceInfo(
                id=v["id"],
                name=v["name"],
                provider="edge",
                language=v["language"],
                gender=v["gender"]
            ))
        return voices
    
    @property
    def name(self) -> str:
        return "edge"

