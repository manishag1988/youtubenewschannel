"""
Text-to-Speech module - Create placeholder audio files
Since Windows TTS is having issues with subprocess, we create placeholder audio
"""

import os
from pathlib import Path
from dataclasses import dataclass
from config import config
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


@dataclass
class AudioFile:
    path: Path
    duration: float
    voice: str
    service: str


class TTSEngine:
    """TTS engine - creates placeholder for now"""

    def __init__(self, api_keys: dict = None, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_keys = api_keys or {}
        self.default_voice = config.tts.PRIMARY_VOICE

    def generate(self, text: str, voice: str = None, output_path: Path = None) -> AudioFile:
        if voice is None:
            voice = self.default_voice

        if not text:
            raise ValueError("No text provided")

        logger.info(f"Creating placeholder audio (Windows TTS requires manual setup)")
        
        logger.info("Note: For real TTS, either:")
        logger.info("  1. Add OPENAI_API_KEY for AI voiceover")
        logger.info("  2. Or use Windows Narrator manually")
        
        if output_path is None:
            from datetime import datetime
            output_path = Path(config.OUTPUT_DIR) / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        # Write a simple WAV header as placeholder
        # This creates a valid but silent WAV file
        import wave
        import struct
        
        try:
            with wave.open(str(output_path), 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                
                # Write 3 seconds of silence (48000 bytes)
                silence = b'\x00' * 48000
                wav_file.writeframes(silence)
            
            duration = 3.0
            
            logger.info(f"Created placeholder audio: {output_path} ({duration:.1f}s)")
            
            # Also save the text script for manual recording
            script_path = output_path.with_suffix('.txt')
            script_path.write_text(text)
            logger.info(f"Saved script for manual recording: {script_path}")
            
            return AudioFile(
                path=output_path,
                duration=duration,
                voice=voice,
                service="Placeholder"
            )
            
        except Exception as e:
            logger.error(f"Failed to create placeholder: {e}")
            raise