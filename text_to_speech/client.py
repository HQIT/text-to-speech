"""
Core TTS client for text-to-speech conversion.
"""

import logging
from typing import Optional, Callable, Union
from dataclasses import dataclass

from .providers import TTSProvider, StreamTTSProvider

logger = logging.getLogger(__name__)


@dataclass
class TTSResult:
    """
    TTS processing result.
    
    Attributes:
        type: Result type (0=processing, 1=completed, -1=error)
        message: Error message (if type=-1)
        audio: Audio data bytes
        process: Processing progress (0-100)
    """
    type: int
    message: Optional[str] = None
    audio: bytes = b''
    process: int = 0


class TTSError(Exception):
    """Exception raised when TTS processing fails."""
    pass


class TTSClient:
    """
    Text-to-Speech client.
    
    Example:
        >>> client = TTSClient(content="你好世界", spk_id="xiaoyan")
        >>> client.start()
        >>> audio = client.audio
        
        # 使用自定义 provider
        >>> from text_to_speech.providers import StreamTTSProvider
        >>> provider = StreamTTSProvider(url="http://custom-tts-server/api")
        >>> client = TTSClient(content="你好", provider=provider)
    """
    
    def __init__(
        self,
        content: str,
        spk_id: str = "xiaoyan",
        callback: Optional[Callable[[TTSResult], None]] = None,
        provider: Optional[TTSProvider] = None,
        tts_url: Optional[str] = None  # 向后兼容
    ):
        """
        Initialize TTS client.
        
        Args:
            content: Text content to convert to speech
            spk_id: Speaker ID for voice selection
            callback: Optional callback function for progress updates
            provider: TTS provider instance (优先使用)
            tts_url: TTS service URL (向后兼容，会创建 StreamTTSProvider)
        """
        self.content = content
        self.spk_id = spk_id
        self.callback = callback
        self.audio = b''
        
        # Provider 优先，否则使用 tts_url 创建默认 provider
        if provider:
            self.provider = provider
        else:
            self.provider = StreamTTSProvider(url=tts_url)
    
    def start(self) -> bytes:
        """
        Start TTS processing.
        
        Returns:
            Audio data as bytes
            
        Raises:
            TTSError: If TTS processing fails
        """
        try:
            for chunk in self.provider.synthesize(self.content, self.spk_id):
                self.audio += chunk
                if self.callback:
                    self.callback(TTSResult(0, audio=chunk, process=0))
            
            if self.callback:
                self.callback(TTSResult(1, audio=self.audio))
            
            return self.audio
            
        except Exception as e:
            error_msg = str(e)
            if self.callback:
                self.callback(TTSResult(-1, message=error_msg))
            logger.error(f"TTS processing failed: {error_msg}")
            raise TTSError(error_msg) from e
    
    def convert(self, output_path: Optional[str] = None) -> bytes:
        """
        Convert text to speech and optionally save to file.
        
        Args:
            output_path: Optional path to save audio file
            
        Returns:
            Audio data as bytes
        """
        audio = self.start()
        
        if output_path:
            from .utils import save_audio_file
            save_audio_file(audio, output_path)
            logger.info(f"Audio saved to: {output_path}")
        
        return audio


def text_to_speech(
    text: str,
    output_path: Optional[str] = None,
    spk_id: str = "xiaoyan",
    provider: Optional[TTSProvider] = None,
    tts_url: Optional[str] = None,
    callback: Optional[Callable[[TTSResult], None]] = None
) -> bytes:
    """
    Convenience function to convert text to speech.
    
    Args:
        text: Text content to convert
        output_path: Optional path to save audio file
        spk_id: Speaker ID for voice selection
        provider: TTS provider instance
        tts_url: TTS service URL (向后兼容)
        callback: Optional callback for progress updates
        
    Returns:
        Audio data as bytes
    """
    client = TTSClient(
        content=text,
        spk_id=spk_id,
        callback=callback,
        provider=provider,
        tts_url=tts_url
    )
    return client.convert(output_path)
