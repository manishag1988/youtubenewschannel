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

        Args:
            audio_path: Path to audio file
            video_clips: List of video clip paths
            images: List of image paths (for static visuals)
            output_name: Custom output filename

        Returns:
            FinalVideo object
        """
        logger.info("Starting video assembly...")

        if output_name is None:
            output_name = f"final_video_{int(time.time())}"

        output_path = Path(config.OUTPUT_DIR) / f"{output_name}.{self.output_format}"

        try:
            result = self._assemble_with_moviepy(
                audio_path,
                video_clips,
                images,
                output_path
            )
            logger.info(f"Video assembled: {result.path}")
            return result

        except ImportError:
            logger.warning("moviepy not available, using fallback assembly")
            return self._assemble_fallback(
                audio_path,
                video_clips,
                images,
                output_path
            )

        except Exception as e:
            logger.error(f"Video assembly failed: {e}")
            raise

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
        """Fallback assembly using ffmpeg directly"""
        import subprocess

        temp_dir = Path(config.OUTPUT_DIR) / "temp_assembly"
        temp_dir.mkdir(exist_ok=True)

        try:
            input_files = []

            if video_clips:
                for i, clip in enumerate(video_clips):
                    if clip.exists():
                        input_files.append(str(clip))

            if images:
                for img in images:
                    if img.exists():
                        input_files.append(str(img))

            if not input_files:
                dummy_video = temp_dir / "black.mp4"
                subprocess.run([
                    'ffmpeg', '-f', 'lavfi', '-i', 'color=c=black:s=1280x720:d=60',
                    '-c:v', 'libx264', '-t', '60', '-pix_fmt', 'yuv420p',
                    str(dummy_video)
                ], capture_output=True)
                input_files.append(str(dummy_video))

            if audio_path and audio_path.exists():
                audio_input = ['-i', str(audio_path)]
                audio_map = ['-map', '0:v', '-map', '1:a']
            else:
                audio_input = []
                audio_map = ['-map', '0:v']

            cmd = ['ffmpeg', '-y']

            for inp in input_files:
                cmd.extend(['-i', inp])

            cmd.extend(audio_input)
            cmd.extend(audio_map)
            cmd.extend([
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                str(output_path)
            ])

            result = subprocess.run(cmd, capture_output=True, timeout=300)

            if result.returncode == 0 and output_path.exists():
                duration = self._get_video_duration(output_path)
                return FinalVideo(
                    path=output_path,
                    duration=duration,
                    resolution=self.resolution,
                    format=self.output_format
                )
            else:
                logger.error(f"FFmpeg failed: {result.stderr.decode()}")
                raise Exception("Fallback assembly failed")

        finally:
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

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