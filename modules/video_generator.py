"""
AI Video generation - Local PIL-based (no external APIs needed)
"""

import os
import time
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


class LocalVideoGenerator:
    """Generate animated GIFs using PIL - works locally, no API needed"""

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()

    def generate(self, prompt: str, duration: int = 5) -> bytes:
        """Generate animated video using PIL"""
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            raise Exception("PIL not available")

        width, height = 1280, 720
        frames = []

        for i in range(duration * 10):
            color = self._get_bg_color(prompt, i)
            img = Image.new('RGB', (width, height), color=color)
            draw = ImageDraw.Draw(img)

            for j in range(5):
                x = ((i * 30) + j * 400) % (width + 200) - 100
                y = height // 2 + int(50 * ((i + j) % 3))
                size = 30 + j * 10
                draw.ellipse([x-size, y-size, x+size, y+size],
                           fill=(50 + j*30, 100 + j*20, 200), outline=(255, 255, 255), width=1)

            draw.text((50, 50), "Tech News Background", fill=(255, 255, 255))
            draw.text((50, height - 50), f"Segment {i+1}", fill=(150, 150, 150))

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

    def _get_bg_color(self, prompt: str, frame: int) -> tuple:
        """Get background color based on prompt"""
        prompt_lower = prompt.lower()

        if 'ai' in prompt_lower or 'tech' in prompt_lower:
            colors = [(20, 40, 80), (40, 20, 80), (80, 40, 20)]
        elif 'news' in prompt_lower or 'update' in prompt_lower:
            colors = [(30, 30, 50), (50, 30, 30), (30, 50, 30)]
        else:
            colors = [(20, 20, 40), (40, 20, 40), (20, 40, 40)]

        return colors[frame % len(colors)]


class VideoGenerator:
    """Video generation using local PIL only"""

    def __init__(self, api_keys: dict = None, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_keys = api_keys or {}
        self.max_duration = config.video.MAX_CLIP_DURATION
        self.generator = LocalVideoGenerator(rate_limiter)

    def generate_clips(self, prompts: List[str], count: int = 3) -> List[VideoClip]:
        """Generate video clips from prompts"""
        if not prompts:
            prompts = ["technology background", "news background", "digital animation"]

        selected_prompts = prompts[:count]
        if len(selected_prompts) < count:
            selected_prompts.extend(prompts[:count - len(selected_prompts)])

        clips = []

        for i, prompt in enumerate(selected_prompts):
            try:
                duration = 5
                video_data = self.generator.generate(prompt, duration)

                filename = f"clip_{i}_{int(time.time())}.gif"
                output_path = Path(config.OUTPUT_DIR) / filename
                output_path.write_bytes(video_data)

                clips.append(VideoClip(
                    path=output_path,
                    prompt=prompt,
                    duration=float(duration),
                    service="Local PIL",
                    resolution="1280x720"
                ))

                logger.info(f"Generated clip {i+1}: {filename}")

            except Exception as e:
                logger.error(f"Failed to generate clip {i+1}: {e}")

        return clips

    def generate_from_script(self, script_text: str, clip_count: int = 3) -> List[VideoClip]:
        """Generate video clips based on script"""
        import re
        broll_pattern = r'\[B-ROLL:([^\]]+)\]'
        brolls = re.findall(broll_pattern, script_text, re.IGNORECASE)

        if brolls:
            return self.generate_clips(brolls, clip_count)

        default_prompts = ["technology news", "digital world", "future tech"]
        return self.generate_clips(default_prompts, clip_count)


import io