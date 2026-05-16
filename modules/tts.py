"""
Text-to-Speech module - Windows SAPI only (fully local, no internet needed)
"""

import os
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from config import config
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


@dataclass
class AudioFile:
    """Represents generated audio"""
    path: Path
    duration: float
    voice: str
    service: str


class WindowsTTS:
    """Windows SAPI TTS - works completely offline"""

    VOICES = {
        "adam": "David",
        "brian": "Zira", 
        "rachel": "Hazel",
        "daniel": "Mark"
    }

    def generate(self, text: str, voice: str = "adam") -> bytes:
        """Generate audio using Windows SAPI"""
        voice_name = self.VOICES.get(voice.lower(), "David")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp_path = tmp.name

        try:
            cmd = f'''Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.SelectVoice("{voice_name}"); $synth.SetOutputToWaveFile("{tmp_path}"); $synth.Speak("{text.replace('"', "'\"'").replace("\n", " ")}"); $synth.Dispose()'''

            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                timeout=60
            )

            if result.returncode == 0 and os.path.exists(tmp_path):
                with open(tmp_path, 'rb') as f:
                    audio_data = f.read()

                os.unlink(tmp_path)

                if len(audio_data) > 1000:
                    return audio_data

            raise Exception("Windows TTS failed")

        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            raise


class TTSEngine:
    """TTS engine using Windows SAPI only"""

    def __init__(self, api_keys: dict = None, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_keys = api_keys or {}
        self.default_voice = config.tts.PRIMARY_VOICE

    def generate(self, text: str, voice: str = None, output_path: Path = None) -> AudioFile:
        """Generate audio from text using Windows SAPI"""
        if voice is None:
            voice = self.default_voice

        if not text:
            raise ValueError("No text provided")

        logger.info(f"Generating TTS with voice: {voice}")

        try:
            tts = WindowsTTS()
            audio_data = tts.generate(text, voice)

            if output_path is None:
                from datetime import datetime
                output_path = Path(config.OUTPUT_DIR) / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

            output_path.write_bytes(audio_data)

            duration = len(audio_data) / 2000.0

            logger.info(f"Audio generated: {output_path} ({duration:.1f}s)")

            return AudioFile(
                path=output_path,
                duration=duration,
                voice=voice,
                service="Windows SAPI"
            )

        except Exception as e:
            logger.error(f"TTS failed: {e}")
            raise Exception(f"Audio generation failed: {e}")