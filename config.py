"""
Configuration for the YouTube News Channel Automation Tool
All tools are 100% free with verified free tiers as of May 2026
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

class NewsConfig:
    """News aggregation configuration"""
    RSS_FEEDS = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "https://www.wired.com/feed/rss",
        "https://www.engadget.com/rss.xml",
        "https://feeds.feedburner.com/TechCrunch",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    ]

    MAX_STORIES_PER_CHECK = 10
    MIN_SCORE_THRESHOLD = 5.0

class ScriptConfig:
    """Script generation configuration"""
    MAX_WORD_COUNT = 400
    VIDEO_DURATION_SECONDS = 180

    STRUCTURE = {
        "hook": 10,
        "context": 30,
        "main_story": 100,
        "takeaway": 20
    }

class TTSConfig:
    """Text-to-Speech configuration"""
    PRIMARY_VOICE = "adam"
    FALLBACK_VOICES = ["adam", "brian", "daniel", "Rachel"]

    MAX_CHUNK_SIZE = 4500

    SERVICES = {
        "ttsmp3": {
            "name": "TTSMP3",
            "url": "https://ttsmp3.org/sapi/",
            "type": "browser",
            "free": True,
            "no_signup": True
        },
        "soundtools": {
            "name": "SoundTools",
            "url": "https://soundtools.io/text-to-speech/",
            "type": "browser",
            "free": True,
            "no_signup": True
        },
        "outloud": {
            "name": "Out Loud",
            "url": "offline",
            "type": "desktop",
            "free": True,
            "no_signup": True
        },
        "anyvoicelab": {
            "name": "AnyVoice Lab",
            "url": "https://anyvoicelab.com/",
            "type": "cloud",
            "free": True,
            "signup_required": True
        }
    }

class VideoConfig:
    """AI Video generation configuration"""
    PRIMARY_SERVICE = "kling"
    MAX_CLIP_DURATION = 10

    ASPECT_RATIO = "16:9"

    SERVICES = {
        "kling": {
            "name": "Kling AI",
            "url": "https://klingai.com/",
            "credits_per_day": 66,
            "max_duration": 10,
            "resolution": "720p",
            "watermark": False,
            "type": "cloud"
        },
        "loremotion": {
            "name": "LoreMotion",
            "url": "https://loremotion.com/",
            "unlimited": True,
            "max_duration": 8,
            "resolution": "720p",
            "watermark": False,
            "ad_supported": True,
            "type": "cloud"
        },
        "freeai": {
            "name": "Free.ai",
            "url": "https://free.ai/video/",
            "tokens_per_day": 2500,
            "max_duration": 6,
            "resolution": "480p",
            "watermark": False,
            "no_signup": True,
            "type": "cloud"
        },
        "pika": {
            "name": "Pika Labs",
            "url": "https://pika.art/",
            "credits_per_month": 80,
            "max_duration": 4,
            "resolution": "1080p",
            "watermark": True,
            "type": "cloud"
        },
        "luma": {
            "name": "Luma Dream Machine",
            "url": "https://lumalabs.ai/dream-machine",
            "videos_per_month": 8,
            "max_duration": 6,
            "resolution": "720p",
            "watermark": True,
            "type": "cloud"
        }
    }

class ThumbnailConfig:
    """Thumbnail generation configuration"""
    PRIMARY_SERVICE = "thumbfree"
    WIDTH = 1280
    HEIGHT = 720

    SERVICES = {
        "thumbfree": {
            "name": "Thumb-Free",
            "url": "https://thumb-free.com/",
            "unlimited": True,
            "no_login": True,
            "type": "cloud"
        },
        "canva": {
            "name": "Canva",
            "url": "https://canva.com/",
            "credits_per_day": 5,
            "type": "cloud"
        },
        "leonardo": {
            "name": "Leonardo AI",
            "url": "https://leonardo.ai/",
            "credits_per_day": 150,
            "type": "cloud"
        },
        "editthispic": {
            "name": "EditThisPic",
            "url": "https://editthispic.com/",
            "free_per_week": 1,
            "type": "cloud"
        }
    }

class LLMConfig:
    """LLM for script generation"""
    PRIMARY = "chatgpt"
    TEMPERATURE = 0.7
    MAX_TOKENS = 1000

    SERVICES = {
        "chatgpt": {
            "name": "ChatGPT",
            "url": "https://chat.openai.com/",
            "model": "gpt-4o",
            "free_tier": True,
            "type": "cloud"
        },
        "gemini": {
            "name": "Google Gemini",
            "url": "https://gemini.google.com/",
            "model": "gemini-1.5-pro",
            "free_tier": True,
            "type": "cloud"
        },
        "claude": {
            "name": "Claude",
            "url": "https://claude.ai/",
            "model": "claude-3-haiku",
            "free_tier": True,
            "type": "cloud"
        },
        "deepseek": {
            "name": "DeepSeek",
            "url": "https://www.deepseek.com/",
            "model": "deepseek-chat",
            "free_tier": True,
            "type": "cloud"
        }
    }

class VideoEditorConfig:
    """Video editing configuration"""
    PRIMARY = "capcut"
    FALLBACK = "ffmpeg"

    OUTPUT_FORMAT = "mp4"
    OUTPUT_CODEC = "h264"
    OUTPUT_RESOLUTION = "1920x1080"
    OUTPUT_FPS = 30

class LoggingConfig:
    """Logging configuration"""
    LOG_LEVEL = "INFO"
    LOG_FILE = BASE_DIR / "automation.log"
    CONSOLE_OUTPUT = True

class GlobalConfig:
    """Global configuration container"""
    news = NewsConfig()
    script = ScriptConfig()
    tts = TTSConfig()
    video = VideoConfig()
    thumbnail = ThumbnailConfig()
    llm = LLMConfig()
    editor = VideoEditorConfig()
    logging = LoggingConfig()

    PROJECT_NAME = "YouTube Tech News Automator"
    VERSION = "1.0.0"

    MAX_RETRIES = 3
    RETRY_DELAY = 5

    ENABLE_FALLBACKS = True

    OUTPUT_DIR = BASE_DIR / "outputs"
    OUTPUT_DIR.mkdir(exist_ok=True)

config = GlobalConfig()