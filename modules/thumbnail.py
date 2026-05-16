"""
Thumbnail generation - Local PIL-based (no external APIs needed)
"""

import time
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


class LocalThumbnailGenerator:
    """Generate thumbnails using PIL - works locally"""

    def generate(self, title: str, prompt: str = None) -> bytes:
        """Generate thumbnail using PIL"""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise Exception("PIL not available")

        width, height = 1280, 720
        img = Image.new('RGB', (width, height), color=(20, 20, 35))
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, width, height], outline=(100, 150, 255), width=5)

        title_short = title[:50] if len(title) > 50 else title
        try:
            draw.text((width//2 - 300, height//2 - 50), title_short.upper(), fill=(255, 255, 255))
        except:
            draw.text((width//2 - 300, height//2 - 50), "TECH NEWS", fill=(255, 255, 255))

        draw.text((width//2 - 150, height//2 + 20), "Automated Video", fill=(200, 200, 200))

        draw.text((width - 200, height - 50), "YouTube", fill=(150, 150, 150))

        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()

    def _get_bg_color(self, prompt: str) -> tuple:
        colors = [(20, 40, 80), (40, 20, 80), (80, 40, 20)]
        return colors[hash(prompt) % len(colors)]


class ThumbnailGenerator:
    """Thumbnail generation using local PIL only"""

    def __init__(self, api_keys: dict = None, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_keys = api_keys or {}
        self.width = config.thumbnail.WIDTH
        self.height = config.thumbnail.HEIGHT
        self.generator = LocalThumbnailGenerator()
        self.output_dir = None

    def generate(self, title: str, prompt: str = None, count: int = 1, output_dir: Path = None) -> List[Thumbnail]:
        """Generate thumbnail(s)"""
        self.output_dir = output_dir or Path(config.OUTPUT_DIR)

        if prompt is None:
            prompt = f"YouTube thumbnail for: {title}"

        thumbnails = []

        for i in range(count):
            try:
                image_data = self.generator.generate(title, prompt)

                filename = f"thumbnail_{i}_{int(time.time())}.png"
                output_path = self.output_dir / filename
                output_path.write_bytes(image_data)

                thumbnails.append(Thumbnail(
                    path=output_path,
                    prompt=prompt,
                    service="Local PIL",
                    size=(self.width, self.height)
                ))

                logger.info(f"Generated thumbnail: {filename}")

            except Exception as e:
                logger.error(f"Failed to generate thumbnail {i+1}: {e}")

        return thumbnails

    def generate_from_video_title(self, title: str) -> Optional[Thumbnail]:
        """Generate a single thumbnail from video title"""
        thumbnails = self.generate(title, count=1)
        return thumbnails[0] if thumbnails else None


import io