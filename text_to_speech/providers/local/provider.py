"""
Local TTS Provider - 使用系统自带的TTS引擎（pyttsx3）
最简单的本地TTS实现，无需网络连接
"""

import logging
import os
import tempfile
from typing import Iterator, List

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

from ..base import TTSProvider, VoiceInfo

logger = logging.getLogger(__name__)


class LocalTTSProvider(TTSProvider):
    """
    本地TTS提供者，使用pyttsx3（系统自带TTS引擎）。
    
    支持平台：
    - Windows: SAPI5
    - macOS: NSSpeechSynthesizer
    - Linux: espeak
    
    Example:
        >>> provider = LocalTTSProvider()
        >>> for chunk in provider.synthesize("你好", "default"):
        ...     audio_data += chunk
    """
    
    def __init__(self, default_language: str = "zh"):
        """
        初始化本地TTS Provider
        
        Args:
            default_language: 默认语言代码，如 "zh", "en" 等
        """
        if pyttsx3 is None:
            raise ImportError(
                "pyttsx3 is required for LocalTTSProvider. "
                "Install it with: pip install pyttsx3"
            )
        self.engine = pyttsx3.init()
        self.default_language = default_language
    
    def synthesize(self, text: str, spk_id: str) -> Iterator[bytes]:
        """
        使用系统TTS引擎合成语音。
        
        Args:
            text: 要转换的文本
            spk_id: 说话人ID（hash_id），用于匹配特定的发音人（音色）
            
        Yields:
            音频数据块（WAV格式）
        """
        try:
            voices = self.engine.getProperty('voices')
            if not voices:
                # 如果没有可用声音，使用默认
                pass
            else:
                # 通过 hash_id 查找 voice_info
                voice_info = self.find_voice_by_hash_id(spk_id) if spk_id and spk_id != "default" else None
                
                # 匹配系统声音
                selected_voice = None
                if voice_info:
                    # 通过原始 id 匹配
                    for voice in voices:
                        if voice_info.id.lower() in getattr(voice, 'id', '').lower():
                            selected_voice = voice
                            break
                else:
                    # 未指定 spk_id，根据默认语言从 list_voices 中选择
                    voice_infos = self.list_voices()
                    for vi in voice_infos:
                        if vi.language.lower() == self.default_language.lower():
                            for voice in voices:
                                if vi.id.lower() in getattr(voice, 'id', '').lower():
                                    selected_voice = voice
                                    break
                            if selected_voice:
                                break
                
                # 设置声音
                voice_id = selected_voice.id if selected_voice else (voices[0].id if voices else None)
                if voice_id:
                    self.engine.setProperty('voice', voice_id)
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # 保存为WAV文件
            self.engine.save_to_file(text, tmp_path)
            self.engine.runAndWait()
            
            # 读取文件并返回
            with open(tmp_path, 'rb') as f:
                audio_data = f.read()
            
            # 清理临时文件
            os.unlink(tmp_path)
            
            # 返回整个音频数据（作为单个chunk）
            yield audio_data
            
        except Exception as e:
            logger.error(f"Local TTS synthesis failed: {e}")
            raise
    
    def list_voices(self) -> List[VoiceInfo]:
        """
        获取系统可用的音色列表。
        
        Returns:
            音色信息列表
        """
        voices = []
        try:
            engine_voices = self.engine.getProperty('voices')
            if engine_voices:
                for i, voice in enumerate(engine_voices):
                    voice_id = voice.id if hasattr(voice, 'id') else f"voice_{i}"
                    # 从 voice id 提取语言代码（espeak 格式：lang_code 或 lang_code/variant）
                    lang_code = voice_id.split('/')[0].split('-')[0].lower()
                    # 语言代码映射
                    language_map = {'zh': 'zh', 'zho': 'zh', 'cn': 'zh', 'en': 'en', 'eng': 'en'}
                    language = language_map.get(lang_code, 'en')
                    
                    voices.append(VoiceInfo(
                        id=voice_id,
                        name=voice.name if hasattr(voice, 'name') else f"Voice {i+1}",
                        provider="local",
                        language=language,
                        gender="female" if "female" in str(voice).lower() else "male"
                    ))
        except Exception as e:
            logger.warning(f"Failed to list voices: {e}")
        
        return voices
    
    @property
    def name(self) -> str:
        return "local"

