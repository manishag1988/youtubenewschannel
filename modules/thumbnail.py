"""
Thumbnail generation module with multiple service fallbacks
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
class Thumbnail:
    """Represents a generated thumbnail"""
    path: Path
    prompt: str
    service: str
    size: tuple


class ThumbnailProvider:
    """Base class for thumbnail providers"""

    def generate(self, prompt: str, title: str = None) -> bytes:
        """Generate thumbnail from prompt"""
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


class ThumbFreeProvider(ThumbnailProvider):
    """Thumb-Free thumbnail generation"""

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.base_url = "https://thumb-free.com/api"

    def generate(self, prompt: str, title: str = None) -> bytes:
        """Generate thumbnail using Thumb-Free"""
        logger.info(f"Thumb-Free: generating thumbnail for: {title or prompt[:30]}...")

        try:
            payload = {
                "title": title or prompt,
                "prompt": prompt,
                "style": "vibrant"
            }

            response = requests.post(
                f"{self.base_url}/generate",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                image_url = data.get("image_url")

                if image_url:
                    return requests.get(image_url).content

            raise Exception(f"Thumb-Free returned {response.status_code}")

        except Exception as e:
            logger.error(f"Thumb-Free generation failed: {e}")
            raise


class CanvaProvider(ThumbnailProvider):
    """Canva thumbnail generation"""

    def __init__(self, api_key: str = None, rate_limiter: RateLimiter = None):
        self.api_key = api_key
        self.rate_limiter = rate_limiter or RateLimiter()

    def generate(self, prompt: str, title: str = None) -> bytes:
        """Generate thumbnail using Canva"""
        if not self.rate_limiter.can_use("canva"):
            raise Exception("Canva daily limit reached")

        logger.info(f"Canva: generating thumbnail for: {title or prompt[:30]}...")

        try:
            response = requests.post(
                "https://api.canva.com/rest/v1/thumbnails",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "prompt": prompt,
                    "title": title,
                    "dimensions": {"width": 1280, "height": 720}
                },
                timeout=60
            )

            if response.status_code == 200:
                self.rate_limiter.use("canva")
                data = response.json()
                image_url = data.get("url")

                if image_url:
                    return requests.get(image_url).content

            raise Exception(f"Canva returned {response.status_code}")

        except Exception as e:
            logger.error(f"Canva generation failed: {e}")
            raise


class LeonardoProvider(ThumbnailProvider):
    """Leonardo AI image generation"""

    def __init__(self, api_key: str = None, rate_limiter: RateLimiter = None):
        self.api_key = api_key
        self.rate_limiter = rate_limiter or RateLimiter()

    def generate(self, prompt: str, title: str = None) -> bytes:
        """Generate thumbnail using Leonardo"""
        if not self.api_key:
            raise Exception("Leonardo API key required")

        if not self.rate_limiter.can_use("leonardo"):
            raise Exception("Leonardo daily limit reached")

        logger.info(f"Leonardo: generating thumbnail for: {title or prompt[:30]}...")

        try:
            response = requests.post(
                "https://api.leonardo.ai/v1/generations",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "prompt": f"YouTube thumbnail: {prompt}, high contrast, vibrant colors, cinematic",
                    "width": 1280,
                    "height": 720,
                    "style": "photorealistic"
                },
                timeout=60
            )

            if response.status_code == 200:
                self.rate_limiter.use("leonardo")
                task_id = response.json().get("sd_generate_job_id")

                return self._wait_for_result(task_id)

            raise Exception(f"Leonardo returned {response.status_code}")

        except Exception as e:
            logger.error(f"Leonardo generation failed: {e}")
            raise

    def _wait_for_result(self, task_id: str) -> bytes:
        """Wait for Leonardo generation"""
        max_attempts = 30

        for _ in range(max_attempts):
            time.sleep(5)

            try:
                response = requests.get(
                    f"https://api.leonardo.ai/v1/generations/{task_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")

                    if status == "COMPLETE":
                        images = data.get("generations", [])
                        if images:
                            image_url = images[0].get("url")
                            return requests.get(image_url).content

            except:
                continue

        raise Exception("Leonardo generation timeout")


class EditThisPicProvider(ThumbnailProvider):
    """EditThisPic image enhancement"""

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.base_url = "https://editthispic.com/api"

    def generate(self, prompt: str, title: str = None) -> bytes:
        """Generate thumbnail using EditThisPic"""
        logger.info(f"EditThisPic: generating thumbnail for: {title or prompt[:30]}...")

        try:
            prompt_enhanced = f"make this a bold YouTube thumbnail with high contrast, vivid saturated colors, sharp subject"

            response = requests.post(
                f"{self.base_url}/enhance",
                json={"prompt": prompt_enhanced},
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                image_url = data.get("url")

                if image_url:
                    return requests.get(image_url).content

            raise Exception(f"EditThisPic returned {response.status_code}")

        except Exception as e:
            logger.error(f"EditThisPic generation failed: {e}")
            raise


class PlaceholderThumbnailProvider(ThumbnailProvider):
    """Placeholder thumbnail for when no API is available"""

    def generate(self, prompt: str, title: str = None) -> bytes:
        """Create placeholder thumbnail"""
        logger.warning(f"Creating placeholder thumbnail for: {title or prompt[:30]}...")

        try:
            from PIL import Image, ImageDraw, ImageFont

            width, height = config.thumbnail.WIDTH, config.thumbnail.HEIGHT
            img = Image.new('RGB', (width, height), color=(40, 40, 50))
            draw = ImageDraw.Draw(img)

            text = title or prompt[:30]
            if len(text) > 30:
                text = text[:30] + "..."

            try:
                draw.text((width // 2, height // 2), text, fill=(255, 255, 255), anchor="mm")
            except:
                draw.text((width // 2 - 50, height // 2), text, fill=(255, 255, 255))

            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()

        except ImportError:
            placeholder = f"THUMBNAIL_PLACEHOLDER:{title or prompt}"
            return placeholder.encode('utf-8')


class ThumbnailGenerator:
    """
    Thumbnail generation with multiple service fallbacks
    """

    def __init__(self, api_keys: dict = None, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_keys = api_keys or {}

        self.width = config.thumbnail.WIDTH
        self.height = config.thumbnail.HEIGHT

        self.providers = self._init_providers()

    def _init_providers(self) -> List[ThumbnailProvider]:
        """Initialize thumbnail providers in priority order"""
        providers = []

        providers.append(ThumbFreeProvider(self.rate_limiter))

        if self.api_keys.get("leonardo"):
            providers.append(LeonardoProvider(
                self.api_keys["leonardo"],
                self.rate_limiter
            ))

        if self.api_keys.get("canva"):
            providers.append(CanvaProvider(
                self.api_keys["canva"],
                self.rate_limiter
            ))

        providers.append(EditThisPicProvider(self.rate_limiter))

        providers.append(PlaceholderThumbnailProvider())

        return providers

    def generate(self, title: str, prompt: str = None, count: int = 1) -> List[Thumbnail]:
        """
        Generate thumbnail(s) for a video

        Args:
            title: Video title
            prompt: Custom prompt (optional)
            count: Number of thumbnails to generate

        Returns:
            List of Thumbnail objects
        """
        if prompt is None:
            prompt = self._generate_prompt_from_title(title)

        thumbnails = []

        for i in range(count):
            thumbnail = self._generate_single(prompt, title, i)
            if thumbnail:
                thumbnails.append(thumbnail)

        logger.info(f"Generated {len(thumbnails)} thumbnails")
        return thumbnails

    def _generate_single(self, prompt: str, title: str, index: int) -> Optional[Thumbnail]:
        """Generate a single thumbnail with fallback"""
        last_error = None

        for provider in self.providers:
            try:
                logger.info(f"Generating thumbnail {index + 1} with {provider.name}")

                image_data = provider.generate(prompt, title)

                if image_data:
                    filename = f"thumbnail_{index}_{int(time.time())}.png"
                    output_path = Path(config.OUTPUT_DIR) / filename

                    output_path.write_bytes(image_data)

                    return Thumbnail(
                        path=output_path,
                        prompt=prompt,
                        service=provider.name,
                        size=(self.width, self.height)
                    )

            except Exception as e:
                logger.warning(f"{provider.name} failed for thumbnail {index + 1}: {e}")
                last_error = e
                continue

        logger.error(f"All providers failed for thumbnail {index + 1}")
        return None

    def _generate_prompt_from_title(self, title: str) -> str:
        """Generate a thumbnail prompt from video title"""
        words = title.split()

        tech_keywords = ["AI", "tech", "news", "google", "microsoft", "apple", "startup"]
        has_tech = any(kw.lower() in title.lower() for kw in tech_keywords)

        if has_tech:
            prompt = f"YouTube thumbnail, {title}, modern tech aesthetic, bold typography, vibrant colors, cinematic lighting, high contrast"
        else:
            prompt = f"YouTube thumbnail, {title}, eye-catching design, bold colors, professional finish, trending style"

        return prompt

    def generate_from_video_title(self, title: str) -> Optional[Thumbnail]:
        """Generate a single thumbnail from video title"""
        thumbnails = self.generate(title, count=1)
        return thumbnails[0] if thumbnails else None