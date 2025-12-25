"""
Command-line interface for text-to-speech.
"""

import argparse
import sys
import logging
from pathlib import Path

from .client import TTSClient, TTSResult, TTSError


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="text-to-speech",
        description="Convert text to speech audio"
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
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
        required=True,
        help="Output audio file path"
    )
    
    # TTS options
    parser.add_argument(
        "--spk-id",
        default="xiaoyan",
        help="Speaker ID for voice selection (default: xiaoyan)"
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
        
        # Create client and convert
        client = TTSClient(
            content=text,
            spk_id=args.spk_id,
            tts_url=args.tts_url,
            callback=on_progress if args.verbose else None
        )
        
        logger.info(f"Converting text to speech (spk_id={args.spk_id})...")
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

