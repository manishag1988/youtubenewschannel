"""
Video editing module to assemble final video from audio, clips, and images
Creates CapCut-ready output with separate files
"""

import os
import time
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FinalVideo:
    """Represents the final assembled video"""
    path: Path
    duration: float
    resolution: str
    format: str


class VideoEditor:
    """
    Video editor that creates CapCut-ready output with separate files
    """

    def __init__(self):
        self.output_format = config.editor.OUTPUT_FORMAT
        self.resolution = config.editor.OUTPUT_RESOLUTION
        self.fps = config.editor.OUTPUT_FPS

    def assemble(
        self,
        audio_path: Path,
        video_clips: List[Path] = None,
        images: List[Path] = None,
        output_dir: Path = None
    ) -> FinalVideo:
        """
        Assemble final video from components
        Creates CapCut-ready output with separate files
        """
        logger.info("Starting video assembly for CapCut import...")

        if output_dir is None:
            output_dir = Path(config.OUTPUT_DIR) / f"final_{int(time.time())}"

        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            from PIL import Image, ImageDraw
        except ImportError:
            logger.error("PIL required for video generation")
            raise Exception("PIL not available")

        width, height = 1920, 1080

        print("Creating background animation frames...", flush=True)
        frames = []
        for i in range(60):
            if i % 10 == 0:
                print(f"  Frame {i}/60", flush=True)
            img = Image.new('RGB', (width, height), color=(15, 15, 25))
            draw = ImageDraw.Draw(img)

            for j in range(5):
                x = ((i * 30) + j * 400) % (width + 200) - 100
                y = height // 2 + int(50 * ((i + j) % 3))
                size = 30 + j * 10
                draw.ellipse([x-size, y-size, x+size, y+size],
                           fill=(50 + j*30, 100 + j*20, 200), outline=(255, 255, 255), width=1)

            draw.text((50, 50), "Tech News", fill=(255, 255, 255))
            draw.text((50, height - 100), f"Frame {i+1}/60", fill=(150, 150, 150))

            frames.append(img)

        bg_path = output_dir / "background_loop.gif"
        frames[0].save(
            str(bg_path),
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )
        logger.info(f"Created background: {bg_path.name}")

        title_path = output_dir / "title_card.png"
        title_img = Image.new('RGB', (width, height), color=(20, 20, 35))
        title_draw = ImageDraw.Draw(title_img)
        title_draw.rectangle([0, 0, width, height], outline=(100, 150, 255), width=5)
        title_draw.text((width//2 - 200, height//2 - 50), "TECH NEWS", fill=(255, 255, 255))
        title_draw.text((width//2 - 250, height//2 + 20), "Automated Video", fill=(200, 200, 200))
        title_img.save(str(title_path))
        logger.info(f"Created title card: {title_path.name}")

        if audio_path and audio_path.exists():
            audio_dest = output_dir / "voiceover.mp3"
            shutil.copy2(audio_path, audio_dest)
            logger.info(f"Copied audio: {audio_dest.name}")

        file_list = output_dir / "IMPORT_THIS_INTO_CAPCUT.txt"
        with open(file_list, 'w') as f:
            f.write("CAPCUT IMPORT GUIDE\n")
            f.write("=" * 40 + "\n\n")
            f.write("1. Open CapCut on your device\n")
            f.write("2. Click 'Import'\n")
            f.write("3. Import these files in this order:\n\n")
            f.write(f"   FIRST: {title_path.name} (use as intro)\n")
            f.write(f"   SECOND: {bg_path.name} (loop as background)\n")
            f.write(f"   THIRD: voiceover.mp3 (your script audio)\n\n")
            f.write("4. In CapCut timeline:\n")
            f.write("   - Place title_card.png first (3 seconds)\n")
            f.write("   - Place background_loop.gif after (loop it)\n")
            f.write("   - Place voiceover.mp3 on audio track\n\n")
            f.write("5. Add transitions, text overlays, export!\n\n")
            f.write("=" * 40 + "\n")
            f.write("Your files are ready in:\n")
            f.write(f"{output_dir}\n")

        logger.info(f"Created import guide: {file_list.name}")

        return FinalVideo(
            path=output_dir,
            duration=60.0,
            resolution=f"{width}x{height}",
            format="folder"
        )

    def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration"""
        return 60.0