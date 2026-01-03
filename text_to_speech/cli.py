"""
Command-line interface for text-to-speech.
"""

import argparse
import sys
import logging
from pathlib import Path

from .client import TTSClient, TTSResult, TTSError
from .registry import registry
from .providers import StreamTTSProvider, EdgeTTSProvider


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def init_default_provider():
    """初始化默认 Provider"""
    logger = logging.getLogger(__name__)
    
    # 优先使用 Edge TTS（免费且中文质量好）
    if not registry.get("default"):
        try:
            edge_provider = EdgeTTSProvider()
            registry.register("default", edge_provider)
            registry.register("edge", edge_provider)
            logger.info("Registered TTS provider: default (edge)")
        except Exception as e:
            logger.warning(f"Edge provider not available: {e}")
    
    # 回退到 Stream
    if not registry.get("default"):
        provider = StreamTTSProvider()
        registry.register("default", provider)
        logger.info("Registered TTS provider: default (stream)")
    
    # 同时注册 stream provider 供选择
    if not registry.get("stream"):
        stream_provider = StreamTTSProvider()
        registry.register("stream", stream_provider)


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
        default="default",
        help="Speaker ID for voice selection (default: default). Use --list-voices to see available IDs"
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
    init_default_provider()
    
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
        
        if not provider:
            logger.error(f"Provider not found: {provider_name}")
            sys.exit(1)
        
        # Create client and convert
        client = TTSClient(
            content=text,
            spk_id=args.spk_id,
            provider=provider,
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
