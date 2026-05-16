"""
YouTube Tech News Channel Automation Tool - Main Orchestrator
Fully automated workflow - optimized local version
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

from config import config
from utils.logger import setup_logger, get_logger
from utils.rate_limiter import RateLimiter
from utils.file_manager import FileManager

from modules.news_gatherer import NewsGatherer, NewsStory
from modules.local_llm import get_script_writer
from modules.local_tts import TTSEngine
from modules.local_video import VideoGenerator
from modules.thumbnail import ThumbnailGenerator, Thumbnail


logger = get_logger(__name__)


class WorkflowResult:
    """Result of the entire workflow"""

    def __init__(self):
        self.success: bool = False
        self.news: List[NewsStory] = []
        self.script: Optional[Script] = None
        self.audio: Optional[AudioFile] = None
        self.video_clips: List[VideoClip] = []
        self.thumbnail: Optional[Thumbnail] = None
        self.final_video: Optional[FinalVideo] = None

        self.start_time: datetime = None
        self.end_time: datetime = None
        self.errors: List[str] = []

        self.session_dir: Path = None

    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0


class YouTubeNewsAutomator:
    """Main orchestrator for the YouTube tech news automation workflow"""

    def __init__(self, api_keys: Dict[str, str] = None, output_dir: Path = None):
        self.api_keys = api_keys or {}
        self.output_dir = output_dir or config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.rate_limiter = RateLimiter()
        self.file_manager = FileManager(self.output_dir)

        self._init_modules()

        logger.info("YouTube News Automator initialized")

    def _init_modules(self):
        """Initialize all production modules"""
        logger.info("Initializing production modules...")

        self.news_gatherer = NewsGatherer(self.rate_limiter)
        self.script_writer = get_script_writer(self.api_keys, self.rate_limiter)
        self.tts_engine = TTSEngine(self.api_keys, self.rate_limiter)
        self.video_generator = VideoGenerator(self.api_keys, self.rate_limiter)
        self.thumbnail_generator = ThumbnailGenerator(self.api_keys, self.rate_limiter)
        self.video_editor = VideoEditor()

        logger.info("All modules initialized")
        
        # Check for local services
        from modules.local_llm import LocalLLM
        llm = LocalLLM()
        if llm.is_available():
            logger.info("✅ Local LLM (Ollama) is available")
        else:
            logger.info("ℹ️  Install Ollama for local AI script generation: https://ollama.ai")
        
        from modules.local_tts import LocalTTS
        tts = LocalTTS()
        if tts.is_available():
            logger.info("✅ Local TTS (Piper) is available")
        else:
            logger.info("ℹ️  Install Piper for local voice: https://github.com/rhasspy/piper")
        
        from modules.local_video import LocalSD
        sd = LocalSD()
        if sd.is_available():
            logger.info("✅ Local Stable Diffusion is available")
        else:
            logger.info("ℹ️  Install Stable Diffusion for local video generation")

    def run_full_workflow(self) -> WorkflowResult:
        """Execute the complete automated workflow"""
        result = WorkflowResult()
        result.start_time = datetime.now()

        session_name = f"video_{result.start_time.strftime('%Y%m%d_%H%M%S')}"
        result.session_dir = self.file_manager.create_session_dir(session_name)

        logger.info("=" * 60)
        logger.info("STARTING FULL AUTOMATED WORKFLOW")
        logger.info("=" * 60)

        try:
            logger.info("\n[STEP 1/6] Gathering news...")
            result.news = self._step_gather_news()
            logger.info(f"Gathered {len(result.news)} stories")

            logger.info("\n[STEP 2/6] Writing script...")
            result.script = self._step_write_script(result.news)
            logger.info(f"Script written: {result.script.word_count} words")

            logger.info("\n[STEP 3/6] Generating voiceover...")
            result.audio = self._step_generate_audio(result.script, result.session_dir)
            logger.info(f"Audio generated: {result.audio.duration:.1f}s")

            logger.info("\n[STEP 4/6] Generating video clips...")
            result.video_clips = self._step_generate_video(result.script)
            logger.info(f"Generated {len(result.video_clips)} video clips")

            logger.info("\n[STEP 5/6] Generating thumbnail...")
            result.thumbnail = self._step_generate_thumbnail(result.script.title, result.session_dir)
            logger.info(f"Thumbnail generated: {result.thumbnail.path.name}")

            logger.info("\n[STEP 6/6] Assembling final video...")
            result.final_video = self._step_assemble_video(
                result.audio.path,
                result.video_clips,
                result.session_dir
            )
            logger.info(f"Final video assembled: {result.final_video.path.name}")

            result.success = True
            logger.info("\n" + "=" * 60)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)

        except Exception as e:
            error_msg = f"Workflow failed: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)

        result.end_time = datetime.now()
        self._log_summary(result)

        return result

    def _step_gather_news(self) -> List[NewsStory]:
        """Step 1: Gather news from RSS feeds"""
        max_retries = config.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                stories = self.news_gatherer.fetch_all_news()
                if stories:
                    return stories
                logger.warning(f"No stories found (attempt {attempt + 1})")
            except Exception as e:
                logger.warning(f"News gathering error (attempt {attempt + 1}): {e}")

        return []

    def _step_write_script(self, stories):
        """Step 2: Generate script from stories"""
        if not stories:
            raise ValueError("No stories available for script")

        for attempt in range(config.MAX_RETRIES):
            try:
                script = self.script_writer.generate_script(stories)
                if script:
                    return script
            except Exception as e:
                logger.warning(f"Script writing error (attempt {attempt + 1}): {e}")

        raise Exception("Script generation failed")

    def _step_generate_audio(self, script, session_dir: Path):
        """Step 3: Convert script to audio"""
        for attempt in range(config.MAX_RETRIES):
            try:
                audio = self.tts_engine.generate(
                    script.full_text,
                    output_path=session_dir / f"audio_{int(time.time())}.wav"
                )
                if audio:
                    return audio
            except Exception as e:
                logger.warning(f"Audio generation error (attempt {attempt + 1}): {e}")

        raise Exception("Audio generation failed")

    def _step_generate_video(self, script):
        """Step 4: Generate video clips from script"""
        prompts = script.broll_prompts if script.broll_prompts else []
        if not prompts:
            prompts = ["technology background", "news background", "digital animation"]

        for attempt in range(config.MAX_RETRIES):
            try:
                clips = self.video_generator.generate_clips(prompts, count=3)
                if clips:
                    return clips
            except Exception as e:
                logger.warning(f"Video generation error (attempt {attempt + 1}): {e}")

        return []

    def _step_generate_thumbnail(self, title: str, session_dir: Path) -> Thumbnail:
        """Step 5: Generate thumbnail"""
        for attempt in range(config.MAX_RETRIES):
            try:
                thumbnail = self.thumbnail_generator.generate(title, count=1)
                if thumbnail:
                    return thumbnail[0]
            except Exception as e:
                logger.warning(f"Thumbnail generation error (attempt {attempt + 1}): {e}")

        raise Exception("Thumbnail generation failed")

    def _step_assemble_video(self, audio_path: Path, video_clips: List[VideoClip], session_dir: Path) -> FinalVideo:
        """Step 6: Assemble final video"""
        clip_paths = [c.path for c in video_clips if c.path.exists()]

        for attempt in range(config.MAX_RETRIES):
            try:
                final_video = self.video_editor.assemble(
                    audio_path,
                    video_clips=clip_paths,
                    output_name=f"final_{int(time.time())}"
                )
                if final_video:
                    return final_video
            except Exception as e:
                logger.warning(f"Video assembly error (attempt {attempt + 1}): {e}")

        raise Exception("Video assembly failed")

    def _log_summary(self, result: WorkflowResult):
        """Log workflow summary"""
        logger.info("\n" + "=" * 60)
        logger.info("WORKFLOW SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Status: {'SUCCESS' if result.success else 'FAILED'}")
        logger.info(f"Duration: {result.duration:.1f} seconds")
        logger.info(f"Stories: {len(result.news)}")
        logger.info(f"Script: {result.script.title if result.script else 'N/A'}")
        logger.info(f"Audio: {result.audio.duration if result.audio else 'N/A'}s")
        logger.info(f"Video clips: {len(result.video_clips)}")
        logger.info(f"Thumbnail: {result.thumbnail.path.name if result.thumbnail else 'N/A'}")
        logger.info(f"Final video: {result.final_video.path.name if result.final_video else 'N/A'}")

        if result.errors:
            logger.warning("Errors encountered:")
            for error in result.errors:
                logger.warning(f"  - {error}")


def main():
    """Main entry point"""
    setup_logger()
    logger.info("Starting YouTube Tech News Automator...")

    api_keys = {
        "openai": os.environ.get("OPENAI_API_KEY"),
        "gemini": os.environ.get("GEMINI_API_KEY"),
        "claude": os.environ.get("CLAUDE_API_KEY"),
    }
    api_keys = {k: v for k, v in api_keys.items() if v}

    if api_keys:
        logger.info(f"API keys configured: {list(api_keys.keys())}")
    else:
        logger.info("No API keys - using local services only")

    try:
        automator = YouTubeNewsAutomator(api_keys=api_keys)
        result = automator.run_full_workflow()

        if result.success:
            logger.info("\n✅ Workflow completed successfully!")
            logger.info(f"📁 Output directory: {result.session_dir}")
            return 0
        else:
            logger.error("\n❌ Workflow failed")
            return 1

    except KeyboardInterrupt:
        logger.info("\n⚠️ Workflow interrupted by user")
        return 130

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())