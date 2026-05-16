"""
Local TTS - Using Coqui TTS or Piper (free, runs locally)
"""

import os
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AudioFile:
    path: Path
    duration: float
    voice: str
    service: str


class LocalTTS:
    """Local TTS using pyttsx3 (Windows SAPI - free, works locally)"""

    def __init__(self, voice: str = None):
        self.voice = voice or "default"

    def is_available(self) -> bool:
        """Check if pyttsx3 is available"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            return engine is not None
        except:
            return False

    def generate(self, text: str, output_path: Path = None) -> AudioFile:
        """Generate audio using Windows SAPI"""
        try:
            import pyttsx3

            if output_path is None:
                from datetime import datetime
                output_path = Path(config.OUTPUT_DIR) / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)

            engine.save_to_file(text, str(output_path))
            engine.runAndWait()

            if output_path.exists():
                size = output_path.stat().st_size
                duration = size / 16000.0
                return AudioFile(path=output_path, duration=duration, voice=self.voice, service="Windows SAPI TTS")

            raise Exception("Windows SAPI failed to create audio")

        except Exception as e:
            logger.error(f"Windows SAPI TTS failed: {e}")
            raise


class CoquiTTS:
    """Local TTS using Coqui (better quality)"""

    def is_available(self) -> bool:
        try:
            import torch
            return True
        except:
            return False

    def generate(self, text: str, output_path: Path = None) -> AudioFile:
        """Generate audio using Coqui XTTS"""
        logger.info("Using Coqui TTS (requires model download on first run)")

        try:
            from TTS.api import TTS

            if output_path is None:
                from datetime import datetime
                output_path = Path(config.OUTPUT_DIR) / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

            tts = TTS(model_name="xtts_v2", gpu=False)
            tts.tts_to_file(text=text, file_path=str(output_path))

            if output_path.exists():
                size = output_path.stat().st_size
                duration = size / 22050.0

                return AudioFile(path=output_path, duration=duration, voice="xtts_v2", service="Coqui TTS")

        except Exception as e:
            logger.error(f"Coqui TTS failed: {e}")
            raise


class TTSEngine:
    """TTS with local fallback - tries local first, then creates placeholder"""

    def __init__(self, api_keys=None, rate_limiter=None):
        self.api_keys = api_keys or {}
        self.local_tts = LocalTTS()
        self.coqui_tts = CoquiTTS()

    def generate(self, text: str, voice: str = None, output_path: Path = None) -> AudioFile:
        """Generate audio - try local options, then placeholder"""

        # Try Piper first
        if self.local_tts.is_available():
            try:
                logger.info("Using local Piper TTS")
                return self.local_tts.generate(text, output_path)
            except Exception as e:
                logger.warning(f"Piper failed: {e}")

        # Try Coqui
        if self.coqui_tts.is_available():
            try:
                logger.info("Using local Coqui TTS")
                return self.coqui_tts.generate(text, output_path)
            except Exception as e:
                logger.warning(f"Coqui failed: {e}")

        # Fallback: create placeholder with script text
        logger.info("No local TTS available, creating placeholder")
        return self._create_placeholder(text, output_path)

    def _create_placeholder(self, text: str, output_path: Path = None) -> AudioFile:
        """Create placeholder audio file"""
        import wave

        if output_path is None:
            from datetime import datetime
            output_path = Path(config.OUTPUT_DIR) / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        # Create silent WAV
        with wave.open(str(output_path), 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b'\x00' * 32000)  # 2 seconds

        # Save script text
        script_path = output_path.with_suffix('.txt')
        script_path.write_text(text)

        logger.info(f"Created placeholder: {output_path}")
        logger.info(f"Script saved to: {script_path}")

        return AudioFile(path=output_path, duration=2.0, voice="placeholder", service="None")