"""
Text-to-Speech module - Windows SAPI
"""

import os
import subprocess
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

        if output_path is None:
            from datetime import datetime
            output_path = Path(config.OUTPUT_DIR) / f"temp_tts_{int(time.time())}.wav"

        try:
            text_clean = text.replace('"', "'").replace('\n', ' ').replace('\r', '')[:2000]

            ps_script = f"""
$synth = New-Object -ComObject SAPI.SpVoice
$file = New-Object -ComObject SAPI.SpFileStream
$file.Open('{output_path}', 3, 0)
$synth.Rate = 0
$voice = $synth.GetVoices().Item(0)
$synth.Voice = $voice
$synth.FileStream = $file
$synth.Speak('{text_clean}')
$file.Close()
"""
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                timeout=120
            )

            logger.info(f"Return code: {result.returncode}")

            if output_path.exists():
                audio_size = output_path.stat().st_size
                logger.info(f"Audio file size: {audio_size} bytes")

                if audio_size > 1000:
                    final_path = Path(config.OUTPUT_DIR) / f"audio_{int(time.time())}.wav"
                    output_path.rename(final_path)

                    duration = audio_size / 2000.0

                    logger.info(f"Audio generated: {final_path} ({duration:.1f}s)")

                    return AudioFile(
                        path=final_path,
                        duration=duration,
                        voice=voice,
                        service="Windows SAPI"
                    )

            raise Exception("Windows TTS failed - no audio file")

        except Exception as e:
            logger.error(f"TTS failed: {e}")
            raise Exception(f"Audio generation failed: {e}")


import time