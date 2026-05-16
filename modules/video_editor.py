"""
Video editing module to assemble final video from audio, clips, and images
"""

import os
import time
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
    Video editor that assembles audio, video clips, and images into final video
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
        output_name: str = None
    ) -> FinalVideo:
        """
        Assemble final video from components
        Creates CapCut-ready output with separate files
        """
        logger.info("Starting video assembly for CapCut import...")

        if output_name is None:
            output_name = f"capcut_project_{int(time.time())}"

        session_dir = Path(config.OUTPUT_DIR) / output_name
        session_dir.mkdir(exist_ok=True)

        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
        except ImportError:
            logger.error("PIL required for video generation")
            raise Exception("PIL not available")

        width, height = 1920, 1080

        logger.info("Creating background animation frames...")
        frames = []
        for i in range(60):
            img = Image.new('RGB', (width, height), color=(15, 15, 25))
            draw = ImageDraw.Draw(img)

            for j in range(5):
                x = ((i * 30) + j * 400) % (width + 200) - 100
                y = height // 2 + int(50 * ((i + j) % 3))
                size = 30 + j * 10
                draw.ellipse([x-size, y-size, x+size, y+size],
                           fill=(50 + j*30, 100 + j*20, 200), outline=(255, 255, 255), width=1)

            text_y = height - 100
            draw.text((50, 50), "Tech News", fill=(255, 255, 255))
            draw.text((50, text_y), f"Frame {i+1}/60", fill=(150, 150, 150))

            frames.append(img)

        bg_path = session_dir / "background_loop.gif"
        frames[0].save(
            bg_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )
        logger.info(f"Created background: {bg_path.name}")

        title_path = session_dir / "title_card.png"
        title_img = Image.new('RGB', (width, height), color=(20, 20, 35))
        title_draw = ImageDraw.Draw(title_img)
        title_draw.rectangle([0, 0, width, height], outline=(100, 150, 255), width=5)
        title_draw.text((width//2 - 200, height//2 - 50), "TECH NEWS", fill=(255, 255, 255))
        title_draw.text((width//2 - 250, height//2 + 20), "Automated Video", fill=(200, 200, 200))
        title_path.save(title_path)
        logger.info(f"Created title card: {title_path.name}")

        if audio_path and audio_path.exists():
            import shutil
            audio_dest = session_dir / "voiceover.mp3"
            shutil.copy2(audio_path, audio_dest)
            logger.info(f"Copied audio: {audio_dest.name}")

        file_list = session_dir / "IMPORT_THIS_INTO_CAPCUT.txt"
        with open(file_list, 'w') as f:
            f.write("CAPCUT IMPORT GUIDE\n")
            f.write("=" * 40 + "\n\n")
            f.write("1. Open CapCut\n")
            f.write("2. Click 'Import'\n")
            f.write("3. Import these files in order:\n\n")
            f.write(f"   - {title_path.name} (1st - intro)\n")
            f.write(f"   - {bg_path.name} (background loop)\n")
            f.write(f"   - voiceover.mp3 (your script)\n\n")
            f.write("4. Arrange timeline:\n")
            f.write("   Title -> Background (loop) -> Audio\n\n")
            f.write("5. Add transitions, effects, and export!\n")

        logger.info(f"Created import guide: {file_list.name}")

        return FinalVideo(
            path=session_dir,
            duration=60.0,
            resolution=f"{width}x{height}",
            format="folder"
        )

    def _assemble_with_moviepy(
        self,
        audio_path: Path,
        video_clips: List[Path],
        images: List[Path],
        output_path: Path
    ) -> FinalVideo:
        """Assemble video using moviepy"""
        from moviepy.editor import (
            AudioFileClip, VideoFileClip, ImageClip,
            CompositeVideoClip, concatenate_videoclips
        )

        clips = []

        audio_duration = 0
        if audio_path and audio_path.exists():
            audio = AudioFileClip(str(audio_path))
            audio_duration = audio.duration

        if video_clips:
            for clip_path in video_clips:
                if clip_path.exists():
                    try:
                        clip = VideoFileClip(str(clip_path))
                        clips.append(clip)
                    except Exception as e:
                        logger.warning(f"Failed to load clip {clip_path}: {e}")

        if images and not clips:
            for img_path in images:
                if img_path.exists():
                    try:
                        clip = ImageClip(str(img_path)).set_duration(5)
                        clips.append(clip)
                    except Exception as e:
                        logger.warning(f"Failed to load image {img_path}: {e}")

        if not clips:
            logger.warning("No video clips or images, creating black background")
            from moviepy.editor import ColorClip
            bg = ColorClip(size=(1920, 720), color=(0, 0, 0), duration=audio_duration or 60)
            clips.append(bg)

        final_clip = concatenate_videoclips(clips, method="compose")

        if audio_path and audio_path.exists():
            final_clip = final_clip.set_audio(audio)

        width, height = self._parse_resolution(self.resolution)
        final_clip = final_clip.resize((width, height))

        final_clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            fps=self.fps,
            preset='ultrafast'
        )

        duration = final_clip.duration

        for clip in clips:
            try:
                clip.close()
            except:
                pass

        return FinalVideo(
            path=output_path,
            duration=duration,
            resolution=self.resolution,
            format=self.output_format
        )

    def _assemble_fallback(
        self,
        audio_path: Path,
        video_clips: List[Path],
        images: List[Path],
        output_path: Path
    ) -> FinalVideo:
        """Fallback assembly without ffmpeg - using PIL to create simple video"""
        logger.info("Using PIL-based video assembly (no ffmpeg required)")

        try:
            from PIL import Image, ImageDraw, ImageFont
            import io

            width, height = 1280, 720

            frames = []
            frame_count = 30

            for i in range(frame_count):
                img = Image.new('RGB', (width, height), color=(20, 20, 30))
                draw = ImageDraw.Draw(img)

                x = (i * 40) % width
                draw.ellipse([x-30, height//2-30, x+30, height//2+30],
                           fill=(100, 150, 255), outline=(255, 255, 255), width=2)

                draw.text((50, 50), "YouTube Tech News", fill=(255, 255, 255))
                draw.text((50, height-50), "Automated Video", fill=(200, 200, 200))

                frames.append(img)

            output_path = output_path.with_suffix('.gif')
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=100,
                loop=0
            )

            logger.info(f"Created simple animated video: {output_path}")
            return FinalVideo(
                path=output_path,
                duration=float(frame_count) / 10.0,
                resolution="1280x720",
                format="gif"
            )

        except ImportError:
            logger.error("PIL not available for fallback assembly")
            raise Exception("No video generation possible")
        except Exception as e:
            logger.error(f"PIL assembly failed: {e}")
            raise

    def _parse_resolution(self, res_str: str) -> tuple:
        """Parse resolution string to tuple"""
        parts = res_str.split('x')
        return int(parts[0]), int(parts[1])

    def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration using ffprobe"""
        import subprocess

        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            return float(result.stdout.strip())
        except:
            return 60.0

    def add_captions(
        self,
        video_path: Path,
        srt_path: Path = None,
        output_path: Path = None
    ) -> Path:
        """Add captions to video"""
        logger.info(f"Adding captions to {video_path}")

        if output_path is None:
            output_path = video_path.with_suffix('.captions.mp4')

        try:
            import subprocess

            if srt_path and srt_path.exists():
                cmd = [
                    'ffmpeg', '-i', str(video_path),
                    '-vf', f"subtitles='{srt_path}'",
                    '-c:a', 'copy',
                    str(output_path)
                ]
            else:
                logger.warning("No SRT file provided, skipping captions")
                return video_path

            result = subprocess.run(cmd, capture_output=True, timeout=300)

            if result.returncode == 0:
                return output_path
            else:
                logger.error(f"Caption addition failed: {result.stderr.decode()}")
                return video_path

        except Exception as e:
            logger.error(f"Caption error: {e}")
            return video_path

    def add_watermark(
        self,
        video_path: Path,
        watermark_path: Path = None,
        position: str = "bottom-right",
        output_path: Path = None
    ) -> Path:
        """Add watermark to video"""
        logger.info(f"Adding watermark to {video_path}")

        if output_path is None:
            output_path = video_path.with_suffix('.watermarked.mp4')

        if not watermark_path or not watermark_path.exists():
            logger.warning("No watermark file, skipping")
            return video_path

        try:
            import subprocess

            positions = {
                "top-left": "10:10",
                "top-right": "W-w-10:10",
                "bottom-left": "10:H-h-10",
                "bottom-right": "W-w-10:H-h-10"
            }

            pos = positions.get(position, positions["bottom-right"])

            cmd = [
                'ffmpeg', '-i', str(video_path), '-i', str(watermark_path),
                '-filter_complex', f"overlay={pos}",
                '-c:a', 'copy',
                str(output_path)
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=300)

            if result.returncode == 0:
                return output_path
            else:
                logger.error(f"Watermark failed: {result.stderr.decode()}")
                return video_path

        except Exception as e:
            logger.error(f"Watermark error: {e}")
            return video_path