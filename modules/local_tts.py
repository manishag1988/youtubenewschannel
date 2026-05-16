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
    """Local TTS using Piper (lightweight, fast)"""

    def __init__(self, voice: str = "en_US-lessac-medium"):
        self.voice = voice

    def is_available(self) -> bool:
        """Check if Piper is installed"""
        try:
            result = subprocess.run(["piper", "--help"], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def generate(self, text: str, output_path: Path = None) -> AudioFile:
        """Generate audio using Piper"""
        try:
            if output_path is None:
                from datetime import datetime
                output_path = Path(config.OUTPUT_DIR) / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp:
                tmp.write(text.encode('utf-8'))
                tmp_path = tmp.name

            result = subprocess.run(
                ["piper", "--model", self.voice, "--input_file", tmp_path, "--output_file", str(output_path)],
                capture_output=True,
                timeout=60
            )

            os.unlink(tmp_path)

            if output_path.exists():
                size = output_path.stat().st_size
                duration = size / 16000.0

                return AudioFile(path=output_path, duration=duration, voice=self.voice, service="Piper TTS")

            raise Exception("Piper failed to create audio")

        except Exception as e:
            logger.error(f"Piper TTS failed: {e}")
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