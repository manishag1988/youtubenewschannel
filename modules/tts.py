"""
Text-to-Speech module - Simple Windows SAPI via PowerShell
"""

import os
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
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
    """TTS engine using Windows SAPI"""

    def __init__(self, api_keys: dict = None, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_keys = api_keys or {}
        self.default_voice = config.tts.PRIMARY_VOICE

    def generate(self, text: str, voice: str = None, output_path: Path = None) -> AudioFile:
        if voice is None:
            voice = self.default_voice

        if not text:
            raise ValueError("No text provided")

        logger.info(f"Generating TTS with voice: {voice}")

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp_path = tmp.name

            text_clean = text.replace('"', "'").replace('\n', ' ').replace('\r', '')[:2000]

            cmd = f'''powershell -Command "Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.SelectVoice('Microsoft David Desktop'); $synth.SetOutputToWaveFile('{tmp_path.replace(chr(92), chr(92)+chr(92))}'); $synth.Speak('{text_clean}'); $synth.Dispose()"'''

            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=120)

            if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 1000:
                with open(tmp_path, 'rb') as f:
                    audio_data = f.read()

                if output_path is None:
                    from datetime import datetime
                    output_path = Path(config.OUTPUT_DIR) / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

                with open(output_path, 'wb') as f:
                    f.write(audio_data)

                os.unlink(tmp_path)

                duration = len(audio_data) / 2000.0

                logger.info(f"Audio generated: {output_path} ({duration:.1f}s)")

                return AudioFile(
                    path=output_path,
                    duration=duration,
                    voice=voice,
                    service="Windows SAPI"
                )
            else:
                raise Exception("Windows TTS failed - no audio file")

        except Exception as e:
            logger.error(f"TTS failed: {e}")
            raise Exception(f"Audio generation failed: {e}")