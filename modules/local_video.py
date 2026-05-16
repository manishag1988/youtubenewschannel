"""
Local Video/Image Generation - Using Stable Diffusion via local API
"""

import os
import time
import requests
from pathlib import Path
from dataclasses import dataclass
from config import config
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


@dataclass
class VideoClip:
    path: Path
    prompt: str
    duration: float
    service: str
    resolution: str


class LocalSD:
    """Use Stable Diffusion via local API (automatic1111 or ComfyUI)"""

    def __init__(self, base_url: str = "http://127.0.0.1:7860"):
        self.base_url = base_url

    def is_available(self) -> bool:
        """Check if local Stable Diffusion is running"""
        try:
            response = requests.get(f"{self.base_url}/sdapi/v1/sd-models", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate_image(self, prompt: str, width: int = 1280, height: int = 720) -> bytes:
        """Generate image using local Stable Diffusion"""
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": 20,
            "cfg_scale": 7,
            "sampler_name": "Euler"
        }

        response = requests.post(f"{self.base_url}/sdapi/v1/txt2img", json=payload, timeout=120)

        if response.status_code == 200:
            import base64
            image_data = response.json()["images"][0]
            return base64.b64decode(image_data)

        raise Exception(f"Stable Diffusion returned {response.status_code}")

    def generate_video_frames(self, prompt: str, frames: int = 30) -> list:
        """Generate a sequence of frames for video"""
        images = []
        for i in range(frames):
            frame_prompt = f"{prompt}, frame {i}/{frames}"
            try:
                img_data = self.generate_image(frame_prompt)
                images.append(img_data)
            except Exception as e:
                logger.warning(f"Frame {i} failed: {e}")

        return images


class ComfyUI:
    """Use ComfyUI for local generation"""

    def __init__(self, base_url: str = "http://127.0.0.1:8188"):
        self.base_url = base_url

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate_image(self, prompt: str) -> bytes:
        """Generate using ComfyUI workflow"""
        # Simplified - you'd need proper workflow JSON
        payload = {
            "prompt": prompt,
            "seed": int(time.time())
        }

        try:
            response = requests.post(f"{self.base_url}/prompt", json=payload, timeout=180)
            if response.status_code == 200:
                # Would need to poll for completion
                pass
        except Exception as e:
            logger.error(f"ComfyUI failed: {e}")
            raise


class LocalVideoGenerator:
    """Local video generation using PIL + local SD"""

    def __init__(self, api_keys=None, rate_limiter=None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.local_sd = LocalSD()
        self.comfy = ComfyUI()

    def generate_clips(self, prompts: list, count: int = 3) -> list:
        """Generate video clips - try local SD, then fallback to PIL"""
        clips = []

        # Try local Stable Diffusion
        if self.local_sd.is_available():
            try:
                logger.info("Using local Stable Diffusion for video generation")
                return self._generate_with_sd(prompts, count)
            except Exception as e:
                logger.warning(f"Local SD failed: {e}")

        # Fallback to PIL animation
        logger.info("Using PIL fallback for video generation")
        return self._generate_with_pil(prompts, count)

    def _generate_with_sd(self, prompts: list, count: int) -> list:
        """Generate using Stable Diffusion"""
        clips = []

        for i, prompt in enumerate(prompts[:count]):
            try:
                images = self.local_sd.generate_video_frames(prompt, frames=15)

                if images:
                    # Save as animated image
                    from PIL import Image
                    import io

                    first_img = Image.open(io.BytesIO(images[0]))
                    frames = [Image.open(io.BytesIO(img)) for img in images]

                    output_path = Path(config.OUTPUT_DIR) / f"clip_{i}_{int(time.time())}.gif"
                    frames[0].save(output_path, save_all=True, append_images=frames[1:],
                                  duration=100, loop=0)

                    clips.append(VideoClip(
                        path=output_path,
                        prompt=prompt,
                        duration=1.5,
                        service="Local Stable Diffusion",
                        resolution="1280x720"
                    ))

                    logger.info(f"Generated SD clip: {output_path.name}")

            except Exception as e:
                logger.error(f"SD clip {i} failed: {e}")

        return clips

    def _generate_with_pil(self, prompts: list, count: int) -> list:
        """Generate using PIL - fallback"""
        from PIL import Image, ImageDraw

        clips = []
        width, height = 1280, 720

        selected = prompts[:count] if len(prompts) >= count else prompts + ["tech"] * (count - len(prompts))

        for i, prompt in enumerate(selected):
            frames = []

            for f in range(20):
                color = (20 + f * 5, 40 + f * 3, 80 + f * 2)
                img = Image.new('RGB', (width, height), color=color)
                draw = ImageDraw.Draw(img)

                x = (f * 60) % width
                draw.ellipse([x-40, height//2-40, x+40, height//2+40], fill=(100, 150, 255))
                draw.text((50, 50), prompt[:30], fill=(255, 255, 255))

                frames.append(img)

            output_path = Path(config.OUTPUT_DIR) / f"clip_{i}_{int(time.time())}.gif"
            frames[0].save(output_path, save_all=True, append_images=frames[1:],
                          duration=100, loop=0)

            clips.append(VideoClip(
                path=output_path,
                prompt=prompt,
                duration=2.0,
                service="Local PIL",
                resolution="1280x720"
            ))

            logger.info(f"Generated PIL clip: {output_path.name}")

        return clips


class VideoGenerator:
    """Video generation with local options"""

    def __init__(self, api_keys=None, rate_limiter=None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_keys = api_keys or {}
        self.generator = LocalVideoGenerator(api_keys, rate_limiter)

    def generate_clips(self, prompts: list, count: int = 3) -> list:
        return self.generator.generate_clips(prompts, count)

    def generate_from_script(self, script_text: str, clip_count: int = 3) -> list:
        import re
        brolls = re.findall(r'\[B-ROLL:([^\]]+)\]', script_text, re.IGNORECASE)
        return self.generate_clips(brolls or ["tech news"], clip_count)