"""
Command-line interface for text-to-speech.
"""

import argparse
import sys
import logging
from pathlib import Path

from .client import TTSClient, TTSResult, TTSError
from .registry import registry
from .providers import StreamTTSProvider

try:
    from .providers import LocalTTSProvider
except ImportError:
    LocalTTSProvider = None


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def init_default_provider(tts_url: str = None):
    """初始化默认 Provider"""
    logger = logging.getLogger(__name__)
    if not registry.list_providers():
        provider = StreamTTSProvider(url=tts_url)
        registry.register("default", provider)
    
    # 注册 local provider（如果可用，使用默认语言）
    if LocalTTSProvider and not registry.get("local"):
        try:
            local_provider = LocalTTSProvider(default_language="zh")
            registry.register("local", local_provider)
            logger.info("Registered TTS provider: local")
        except Exception as e:
            logger.warning(f"Local provider not available: {e}")


def list_providers_cmd():
    """列出所有可用的 Providers"""
    providers = registry.list_providers()
    
    if not providers:
        print("No providers available")
        return
    
    print("Available TTS Providers:")
    print("-" * 30)
    for name in providers:
        provider = registry.get(name)
        provider_type = provider.__class__.__name__ if provider else "Unknown"
        print(f"  {name:<15} ({provider_type})")
    print(f"\nTotal: {len(providers)} providers")


def list_voices_cmd(provider_name: str = None):
    """列出所有可用音色"""
    from . import list_voices
    
    voices = list_voices(provider_name)
    
    if not voices:
        print("No voices available")
        if provider_name:
            print(f"Provider '{provider_name}' may not be available or has no voices.")
        return
    
    print(f"{'ID':<18} {'Name':<20} {'Provider':<15} {'Language':<10} {'Gender':<10}")
    print("-" * 75)
    for voice in voices:
        print(f"{voice.hash_id:<18} {voice.name:<20} {voice.provider:<15} {voice.language:<10} {voice.gender:<10}")
    print(f"\nTotal: {len(voices)} voices")
    print(f"\nUsage: Use the ID value with --spk-id option")
    if voices:
        print(f"Example: text-to-speech \"text\" -o output.wav --spk-id {voices[0].hash_id}")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="text-to-speech",
        description="Convert text to speech audio"
    )
    
    # List options
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List all available TTS providers"
    )
    
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List all available voices (use the ID column as --spk-id value)"
    )
    
    # Provider option
    parser.add_argument(
        "--provider",
        help="TTS provider name (default: default)"
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "text",
        nargs="?",
        help="Text content to convert to speech"
    )
    input_group.add_argument(
        "-i", "--input",
        dest="input_file",
        help="Input text file path"
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output",
        help="Output audio file path"
    )
    
    # TTS options
    parser.add_argument(
        "--spk-id",
        default="xiaoyan",
        help="Speaker ID (hash) for voice selection (default: xiaoyan). Use --list-voices to see available IDs"
    )
    
    parser.add_argument(
        "--language",
        help="Language code (e.g., zh, en). Used by local provider for voice selection"
    )
    
    parser.add_argument(
        "--tts-url",
        help="TTS service URL (default: from TTS_URL env var)"
    )
    
    # Logging
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # 初始化默认 Provider
    init_default_provider(args.tts_url)
    
    # 处理 --list-providers
    if args.list_providers:
        list_providers_cmd()
        return
    
    # 处理 --list-voices
    if args.list_voices:
        list_voices_cmd(args.provider)
        return
    
    # 验证必需参数
    if not args.text and not args.input_file:
        parser.error("text or --input is required")
    if not args.output:
        parser.error("--output is required")
    
    # Get text content
    if args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            sys.exit(1)
        
        from .utils import read_text_file
        text = read_text_file(input_path)
        logger.info(f"Read text from: {input_path}")
    else:
        text = args.text
    
    if not text or not text.strip():
        logger.error("Text content is empty")
        sys.exit(1)
    
    try:
        # Create progress callback
        def on_progress(result: TTSResult):
            if result.type == 0:
                logger.debug("Processing...")
            elif result.type == 1:
                logger.info("TTS completed")
            else:
                logger.error(f"Error: {result.message}")
        
        # 使用指定的 provider 或默认
        provider_name = args.provider or "default"
        provider = registry.get(provider_name)
        
        # 如果指定了 language 且 provider 支持 language 参数，创建新的 provider 实例
        if args.language and provider and LocalTTSProvider:
            # 检查是否是 LocalTTSProvider 类型
            if isinstance(provider, LocalTTSProvider):
                try:
                    provider = LocalTTSProvider(default_language=args.language)
                    logger.debug(f"Created provider with language: {args.language}")
                except Exception as e:
                    logger.warning(f"Failed to create provider with language {args.language}: {e}")
                    # 使用已注册的 provider
        
        if not provider:
            logger.error(f"Provider not found: {provider_name}")
            sys.exit(1)
        
        # Create client and convert
        # 优先使用 provider，如果没有则使用 tts_url 创建 StreamTTSProvider
        client = TTSClient(
            content=text,
            spk_id=args.spk_id,
            provider=provider,
            tts_url=args.tts_url,  # 仅当 provider 为 None 时使用
            callback=on_progress if args.verbose else None
        )
        
        logger.info(f"Converting text to speech (spk_id={args.spk_id}, provider={provider_name})...")
        audio = client.convert(output_path=args.output)
        
        print(f"Audio saved to: {args.output}")
        print(f"Audio size: {len(audio)} bytes")
        
    except TTSError as e:
        logger.error(f"TTS failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

