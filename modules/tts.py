"""
Text-to-Speech module with multiple service fallbacks
"""

import os
import re
import requests
import base64
import json
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


class TTSProvider:
    """Base class for TTS providers"""

    def generate(self, text: str, voice: str = None) -> bytes:
        """Generate audio - to be implemented by subclasses"""
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


class TTSMP3Provider(TTSProvider):
    """TTSMP3 browser-based TTS service - Completely free!"""

    VOICE_MAP = {
        "adam": "Adam",
        "brian": "Brian",
        "daniel": "Daniel",
        "rachel": "Rachel",
        "amy": "Amy",
        "emma": "Emma",
    }

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()

    def generate(self, text: str, voice: str = "adam") -> bytes:
        """Generate audio using TTSMP3 (free, no signup)"""
        import urllib.parse

        voice_id = self.VOICE_MAP.get(voice.lower(), "Adam")

        try:
            response = requests.post(
                "https://ttsmp3.com/sapi/",
                data=urllib.parse.urlencode({"text": text, "voice": voice_id}),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=60
            )

            if response.status_code == 200 and response.content:
                return response.content
            else:
                raise Exception(f"TTSMP3 returned status {response.status_code}")

        except Exception as e:
            logger.error(f"TTSMP3 generation failed: {e}")
            raise


class GoogleTranslateTTS(TTSProvider):
    """Google Translate TTS - always free"""

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()

    def generate(self, text: str, voice: str = "adam") -> bytes:
        """Generate using Google Translate TTS"""
        import urllib.parse

        text = text[:200]
        encoded_text = urllib.parse.quote(text)

        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=en-US&client=tw-ob"

        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)

            if response.status_code == 200 and response.content:
                return response.content
            else:
                raise Exception(f"Google TTS returned {response.status_code}")

        except Exception as e:
            logger.error(f"Google TTS failed: {e}")
            raise


class WindowsOfflineTTS(TTSProvider):
    """Windows SAPI TTS - works completely offline!"""

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()

    def generate(self, text: str, voice: str = "adam") -> bytes:
        """Generate using Windows SAPI (offline, no internet)"""
        try:
            import subprocess
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp_path = tmp.name

            voices = {
                "adam": "David",
                "brian": "Zira",
                "rachel": "Hazel",
                "daniel": "Mark"
            }
            voice_name = voices.get(voice.lower(), "David")

            cmd = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.SelectVoice("{voice_name}"); $synth.SetOutputToWaveFile("{tmp_path}"); $synth.Speak("{text.replace("\"", "'\"'").replace("\n", " ")}"); $synth.Dispose()'

            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                timeout=60
            )

            if result.returncode == 0 and Path(tmp_path).exists():
                with open(tmp_path, 'rb') as f:
                    audio_data = f.read()

                Path(tmp_path).unlink()
                return audio_data
            else:
                raise Exception("Windows TTS failed")

        except Exception as e:
            logger.error(f"Windows TTS failed: {e}")
            raise


class SoundToolsProvider(TTSProvider):
    """SoundTools browser-based TTS"""

    VOICE_MAP = {
        "adam": "af_sarah",
        "brian": "am_eric",
        "rachel": "af_ivy",
        "daniel": "am_michael",
    }

    def generate(self, text: str, voice: str = "adam") -> bytes:
        """Generate using SoundTools (Kokoro model)"""
        voice_id = self.VOICE_MAP.get(voice.lower(), "af_sarah")

        url = f"https://soundtools.io/tts?voice={voice_id}"

        try:
            response = requests.post(
                url,
                json={"text": text},
                timeout=60
            )

            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"SoundTools returned {response.status_code}")

        except Exception as e:
            logger.error(f"SoundTools generation failed: {e}")
            raise


class AnyVoiceLabProvider(TTSProvider):
    """AnyVoice Lab TTS service"""

    def __init__(self, api_key: str = None, rate_limiter: RateLimiter = None):
        self.api_key = api_key
        self.rate_limiter = rate_limiter or RateLimiter()

    def generate(self, text: str, voice: str = "adam") -> bytes:
        """Generate using AnyVoice Lab"""
        if not self.api_key:
            raise Exception("No API key")

        try:
            response = requests.post(
                "https://api.anyvoicelab.com/v1/tts",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "text": text,
                    "voice_id": voice,
                    "format": "mp3"
                },
                timeout=60
            )

            self.rate_limiter.use("anyvoicelab", 100)
            return response.content

        except Exception as e:
            logger.error(f"AnyVoice Lab failed: {e}")
            raise


class BrowserTTSProvider(TTSProvider):
    """Browser-based TTS using Web Speech API simulation"""

    def generate(self, text: str, voice: str = "adam") -> bytes:
        """Generate placeholder audio file with text"""
        logger.warning("Browser TTS - creating placeholder audio")

        text_placeholder = f"Audio placeholder for: {text[:100]}..."
        return text_placeholder.encode('utf-8')


class GoogleCloudTTSProvider(TTSProvider):
    """Google Cloud TTS"""

    def __init__(self, api_key: str = None, rate_limiter: RateLimiter = None):
        self.api_key = api_key
        self.rate_limiter = rate_limiter or RateLimiter()

    def generate(self, text: str, voice: str = "adam") -> bytes:
        """Generate using Google Cloud TTS"""
        if not self.api_key:
            raise Exception("No API key")

        try:
            url = "https://texttospeech.googleapis.com/v1/text:synthesize"

            voice_name = "en-US-Neural2-J" if voice.lower() in ["adam", "brian"] else "en-US-Neural2-F"

            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "input": {"text": text},
                    "voice": {"languageCode": "en-US", "name": voice_name},
                    "audioConfig": {"audioEncoding": "MP3"}
                },
                timeout=60
            )

            data = response.json()
            if "audioContent" in data:
                return base64.b64decode(data["audioContent"])
            else:
                raise Exception("No audio content returned")

        except Exception as e:
            logger.error(f"Google Cloud TTS failed: {e}")
            raise


class TTSEngine:
    """
    Text-to-Speech engine with multiple service fallbacks
    """

    def __init__(self, api_keys: dict = None, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_keys = api_keys or {}

        self.default_voice = config.tts.PRIMARY_VOICE
        self.fallback_voices = config.tts.FALLBACK_VOICES

        self.providers = self._init_providers()

    def _init_providers(self) -> List[TTSProvider]:
        """Initialize TTS providers in priority order"""
        providers = []

        providers.append(TTSMP3Provider(self.rate_limiter))

        providers.append(GoogleTranslateTTS(self.rate_limiter))

        if self.api_keys.get("google_cloud"):
            providers.append(GoogleCloudTTSProvider(
                self.api_keys["google_cloud"],
                self.rate_limiter
            ))

        if self.api_keys.get("anyvoicelab"):
            providers.append(AnyVoiceLabProvider(
                self.api_keys["anyvoicelab"],
                self.rate_limiter
            ))

        providers.append(BrowserTTSProvider())

        return providers

    def generate(self, text: str, voice: str = None, output_path: Path = None) -> AudioFile:
        """
        Generate audio from text

        Args:
            text: Text to convert to speech
            voice: Voice to use
            output_path: Path to save audio file

        Returns:
            AudioFile object
        """
        if voice is None:
            voice = self.default_voice

        if not text:
            raise ValueError("No text provided")

        chunks = self._split_text(text)
        logger.info(f"Generating audio from {len(chunks)} text chunks")

        audio_chunks = []

        for i, chunk in enumerate(chunks):
            audio = self._generate_chunk(chunk, voice, i)
            audio_chunks.append(audio)

        if output_path is None:
            from datetime import datetime
            output_path = Path(config.OUTPUT_DIR) / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

        final_audio = self._merge_audio(audio_chunks, output_path)

        logger.info(f"Audio generated: {output_path}")
        return final_audio

    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks respecting sentence boundaries"""
        max_length = config.tts.MAX_CHUNK_SIZE

        if len(text) <= max_length:
            return [text]

        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _generate_chunk(self, text: str, voice: str, index: int) -> bytes:
        """Generate audio for a single chunk with fallback"""
        last_error = None

        for provider in self.providers:
            try:
                logger.debug(f"Trying {provider.name} for chunk {index}")
                audio = provider.generate(text, voice)
                return audio

            except Exception as e:
                logger.warning(f"{provider.name} failed for chunk {index}: {e}")
                last_error = e
                continue

        raise Exception(f"All TTS providers failed: {last_error}")

    def _merge_audio(self, chunks: List[bytes], output_path: Path) -> AudioFile:
        """Merge audio chunks into single file"""
        try:
            from moviepy.editor import AudioFileClip
            import tempfile

            temp_files = []
            for i, chunk in enumerate(chunks):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                    f.write(chunk)
                    temp_files.append(Path(f.name))

            if temp_files:
                first_clip = AudioFileClip(str(temp_files[0]))
                final_clip = first_clip

                for temp_file in temp_files[1:]:
                    clip = AudioFileClip(str(temp_file))
                    final_clip = final_clip.append(clip)

                final_clip.write_audiofile(str(output_path), codec='libmp3lame')

                for tf in temp_files:
                    tf.unlink()

                duration = final_clip.duration
                final_clip.close()

            else:
                output_path.write_bytes(b'\x00' * 1000)
                duration = 1.0

        except ImportError:
            logger.warning("moviepy not available, saving raw audio")
            with open(output_path, 'wb') as f:
                for chunk in chunks:
                    f.write(chunk)
            duration = len(chunks) * 2.0

        except Exception as e:
            logger.error(f"Audio merge failed: {e}")
            with open(output_path, 'wb') as f:
                for chunk in chunks:
                    f.write(chunk)
            duration = len(chunks) * 2.0

        return AudioFile(
            path=output_path,
            duration=duration,
            voice=self.default_voice,
            service="ttsmp3"
        )

    def get_available_voices(self) -> List[str]:
        """Get list of available voices"""
        return self.fallback_voices