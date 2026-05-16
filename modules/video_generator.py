"""
AI Video generation module with fallback support
Note: Most free AI video services require browser interaction or API access
This module provides the framework with placeholder fallbacks
"""

import os
import time
import random
import requests
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from config import config
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


@dataclass
class VideoClip:
    """Represents a generated video clip"""
    path: Path
    prompt: str
    duration: float
    service: str
    resolution: str


class VideoProvider:
    """Base class for video generation providers"""

    def generate(self, prompt: str, duration: int = 5) -> bytes:
        """Generate video from prompt"""
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


class KlingProvider(VideoProvider):
    """Kling AI video generation"""

    def __init__(self, api_key: str = None, rate_limiter: RateLimiter = None):
        self.api_key = api_key
        self.rate_limiter = rate_limiter or RateLimiter()
        self.base_url = "https://api.klingai.com/v1"

    def generate(self, prompt: str, duration: int = 5) -> bytes:
        """Generate video using Kling AI"""
        if not self.api_key:
            raise Exception("Kling API key required")

        if not self.rate_limiter.can_use("kling"):
            raise Exception("Kling daily limit reached")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "prompt": prompt,
                "duration": min(duration, 10),
                "mode": "standard"
            }

            response = requests.post(
                f"{self.base_url}/images/generations",
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                self.rate_limiter.use("kling")
                task_id = response.json().get("task_id")

                return self._poll_for_result(task_id, headers)
            else:
                raise Exception(f"Kling returned {response.status_code}")

        except Exception as e:
            logger.error(f"Kling generation failed: {e}")
            raise

    def _poll_for_result(self, task_id: str, headers: dict) -> bytes:
        """Poll for video generation result"""
        max_attempts = 30

        for _ in range(max_attempts):
            time.sleep(5)

            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                status = data.get("status")

                if status == "completed":
                    video_url = data.get("output", {}).get("video_url")
                    if video_url:
                        return requests.get(video_url).content

                elif status == "failed":
                    raise Exception("Kling generation failed")

        raise Exception("Kling generation timeout")


class LoreMotionProvider(VideoProvider):
    """LoreMotion video generation (ad-supported free)"""

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.base_url = "https://loremotion.com"

    def generate(self, prompt: str, duration: int = 5) -> bytes:
        """Generate video using LoreMotion"""
        logger.info(f"LoreMotion: generating {duration}s video for prompt: {prompt[:50]}...")

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "prompt": prompt,
                    "duration": min(duration, 5),
                    "aspect_ratio": "16:9"
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if "video_url" in result:
                    return requests.get(result["video_url"]).content
                elif "task_id" in result:
                    return self._wait_for_completion(result["task_id"])

            logger.warning(f"LoreMotion returned: {response.status_code} - using placeholder")
            raise Exception(f"LoreMotion service unavailable")

        except Exception as e:
            logger.warning(f"LoreMotion generation failed: {e}")
            raise Exception("LoreMotion unavailable")

    def _wait_for_completion(self, task_id: str) -> bytes:
        """Wait for video generation to complete"""
        max_attempts = 20
        for _ in range(max_attempts):
            time.sleep(3)
            try:
                resp = requests.get(f"{self.base_url}/api/status/{task_id}", timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "ready":
                        return requests.get(data.get("video_url")).content
            except:
                continue
        raise Exception("LoreMotion timeout")


class FreeAIPProvider(VideoProvider):
    """Free.ai video generation (CogVideoX)"""

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.base_url = "https://free.ai/api/video"

    def generate(self, prompt: str, duration: int = 5) -> bytes:
        """Generate video using Free.ai"""
        if not self.rate_limiter.can_use("freeai"):
            raise Exception("Free.ai token limit reached")

        logger.info(f"Free.ai: generating video for: {prompt[:50]}...")

        try:
            response = requests.post(
                self.base_url,
                json={
                    "prompt": prompt,
                    "duration": min(duration, 6),
                    "aspect_ratio": "16:9"
                },
                timeout=180
            )

            if response.status_code == 200:
                task_id = response.json().get("task_id")
                result = self._wait_for_result(task_id)
                self.rate_limiter.use("freeai", 10000)
                return result
            else:
                raise Exception(f"Free.ai returned {response.status_code}")

        except Exception as e:
            logger.error(f"Free.ai generation failed: {e}")
            raise

    def _wait_for_result(self, task_id: str) -> bytes:
        """Wait for video generation"""
        max_attempts = 30

        for _ in range(max_attempts):
            time.sleep(10)

            try:
                response = requests.get(f"{self.base_url}/{task_id}")

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "completed":
                        video_url = data.get("url")
                        return requests.get(video_url).content

            except:
                continue

        raise Exception("Free.ai generation timeout")


class LocalVideoProvider(VideoProvider):
    """Local video generation using PIL/moviepy"""

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()

    def generate(self, prompt: str, duration: int = 5) -> bytes:
        """Generate simple animated video locally"""
        logger.info(f"Creating local video for: {prompt[:50]}...")

        try:
            from PIL import Image, ImageDraw, ImageFont
            import io

            width, height = 1280, 720
            frames = []

            for i in range(duration * 10):
                img = Image.new('RGB', (width, height), color=self._get_color(prompt, i))
                draw = ImageDraw.Draw(img)

                x = (i * 20) % width
                y = height // 2 + int(100 * (i % 2))

                draw.ellipse([x-50, y-50, x+50, y+50], fill=(255, 255, 255), outline=(0, 0, 0))

                text = prompt[:40] if len(prompt) > 40 else prompt
                draw.text((width//2 - 100, height - 50), text, fill=(255, 255, 255))

                frames.append(img)

            output = io.BytesIO()
            frames[0].save(
                output,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                duration=100,
                loop=0
            )
            return output.getvalue()

        except ImportError:
            logger.warning("PIL not available, using placeholder")
            raise Exception("PIL not available")
        except Exception as e:
            logger.error(f"Local video generation failed: {e}")
            raise


class PlaceholderProvider(VideoProvider):
    """Placeholder video for when no API is available"""

    def generate(self, prompt: str, duration: int = 5) -> bytes:
        """Create placeholder video data"""
        logger.warning(f"Creating placeholder video for: {prompt[:50]}...")

        placeholder_content = f"PLACEHOLDER_VIDEO:{prompt}:{duration}s"
        return placeholder_content.encode('utf-8')


class LocalProvider(VideoProvider):
    """Local video generation (ComfyUI/WAN)"""

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()

    def generate(self, prompt: str, duration: int = 5) -> bytes:
        """Generate video locally using WAN/ComfyUI"""
        logger.info(f"Local generation (requires ComfyUI setup): {prompt[:50]}...")

        raise Exception("Local video generation requires ComfyUI setup - not yet implemented")


class VideoGenerator:
    """
    AI Video generation with multiple service fallbacks
    Note: Most services require API keys or browser interaction
    """

    def __init__(self, api_keys: dict = None, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_keys = api_keys or {}

        self.providers = self._init_providers()
        self.max_duration = config.video.MAX_CLIP_DURATION

    def _init_providers(self) -> List[VideoProvider]:
        """Initialize video providers in priority order"""
        providers = []

        if self.api_keys.get("kling"):
            providers.append(KlingProvider(
                self.api_keys["kling"],
                self.rate_limiter
            ))

        providers.append(LoreMotionProvider(self.rate_limiter))

        providers.append(FreeAIPProvider(self.rate_limiter))

        providers.append(PlaceholderProvider())

        return providers

    def generate_clips(self, prompts: List[str], count: int = 3) -> List[VideoClip]:
        """
        Generate video clips from prompts

        Args:
            prompts: List of text prompts for video generation
            count: Number of clips to generate

        Returns:
            List of VideoClip objects
        """
        if not prompts:
            logger.warning("No prompts provided, using default prompts")
            prompts = ["tech news animation", "futuristic technology", "digital world"]

        selected_prompts = prompts[:count]
        if len(selected_prompts) < count:
            selected_prompts.extend(prompts[:count - len(selected_prompts)])

        clips = []

        for i, prompt in enumerate(selected_prompts):
            clip = self._generate_single_clip(prompt, i)
            if clip:
                clips.append(clip)

        logger.info(f"Generated {len(clips)} video clips")
        return clips

    def _generate_single_clip(self, prompt: str, index: int) -> Optional[VideoClip]:
        """Generate a single video clip with fallback"""
        last_error = None

        for provider in self.providers:
            try:
                logger.info(f"Generating clip {index + 1} with {provider.name}")

                duration = random.randint(3, self.max_duration)
                video_data = provider.generate(prompt, duration)

                if video_data:
                    filename = f"clip_{index}_{int(time.time())}.mp4"
                    output_path = Path(config.OUTPUT_DIR) / filename

                    output_path.write_bytes(video_data)

                    return VideoClip(
                        path=output_path,
                        prompt=prompt,
                        duration=float(duration),
                        service=provider.name,
                        resolution="720p"
                    )

            except Exception as e:
                logger.warning(f"{provider.name} failed for clip {index + 1}: {e}")
                last_error = e
                continue

        logger.error(f"All providers failed for clip {index + 1}")
        return None

    def generate_from_script(self, script_text: str, clip_count: int = 3) -> List[VideoClip]:
        """Generate video clips based on script content"""
        prompts = self._extract_prompts_from_script(script_text)
        return self.generate_clips(prompts, clip_count)

    def _extract_prompts_from_script(self, script_text: str) -> List[str]:
        """Extract video prompts from script"""
        import re

        broll_pattern = r'\[B-ROLL:([^\]]+)\]'
        brolls = re.findall(broll_pattern, script_text, re.IGNORECASE)

        if brolls:
            return brolls

        keywords = ["technology", "AI", "computer", "digital", "future"]
        return [f"Abstract {kw} background" for kw in keywords[:3]]

    def get_available_services(self) -> List[str]:
        """Get list of available video services"""
        return [p.name for p in self.providers]


def _get_color(prompt: str, frame: int) -> tuple:
    """Get background color based on prompt"""
    prompt_lower = prompt.lower()

    if 'ai' in prompt_lower or 'tech' in prompt_lower:
        colors = [(20, 40, 80), (40, 20, 80), (80, 40, 20)]
    elif 'news' in prompt_lower or 'update' in prompt_lower:
        colors = [(30, 30, 50), (50, 30, 30), (30, 50, 30)]
    else:
        colors = [(20, 20, 40), (40, 20, 40), (20, 40, 40)]

    return colors[frame % len(colors)]