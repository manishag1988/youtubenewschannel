"""
Text-to-Speech module - Windows SAPI via PowerShell script
"""

import os
import subprocess
import tempfile
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

        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir) / "output.wav"

                text_clean = text.replace('"', "'").replace('\n', ' ').replace('\r', '')[:2000]

                ps_script = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft David Desktop')
$synth.SetOutputToWaveFile('{tmp_path}')
$synth.Speak('{text_clean}')
$synth.Dispose()
"""

                result = subprocess.run(
                    ['powershell', '-Command', ps_script],
                    capture_output=True,
                    timeout=120,
                    cwd=tmp_dir
                )

                if tmp_path.exists():
                    audio_size = tmp_path.stat().st_size
                    logger.info(f"Audio file size: {audio_size} bytes")

                    if audio_size > 1000:
                        if output_path is None:
                            from datetime import datetime
                            output_path = Path(config.OUTPUT_DIR) / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

                        import shutil
                        shutil.copy2(tmp_path, output_path)

                        duration = audio_size / 2000.0

                        logger.info(f"Audio generated: {output_path} ({duration:.1f}s)")

                        return AudioFile(
                            path=output_path,
                            duration=duration,
                            voice=voice,
                            service="Windows SAPI"
                        )

            raise Exception("Windows TTS failed - no audio file")

        except Exception as e:
            logger.error(f"TTS failed: {e}")
            raise Exception(f"Audio generation failed: {e}")