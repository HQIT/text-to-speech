"""
Utility functions for text-to-speech.
"""

import os
from pathlib import Path
from typing import Union, Optional


def load_config() -> dict:
    """
    Load configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        "tts_url": os.getenv("TTS_URL", "http://49.52.4.115:8002/tts_stream"),
        "default_spk_id": os.getenv("TTS_SPK_ID", "xiaoyan"),
    }


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, create if not.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_text_file(file_path: Union[str, Path]) -> str:
    """
    Read text content from a file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Text content
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def save_audio_file(audio_data: bytes, output_path: Union[str, Path]) -> str:
    """
    Save audio data to a file.
    
    Args:
        audio_data: Audio data as bytes
        output_path: Path to save the audio file
        
    Returns:
        Path to the saved file
    """
    output_path = Path(output_path)
    ensure_directory(output_path.parent)
    
    with open(output_path, 'wb') as f:
        f.write(audio_data)
    
    return str(output_path)

