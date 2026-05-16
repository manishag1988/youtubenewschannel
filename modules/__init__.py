"""Production modules for the automation tool"""

from .news_gatherer import NewsGatherer, NewsStory
from .script_writer import ScriptWriter, Script
from .tts import TTSEngine, AudioFile
from .video_generator import VideoGenerator, VideoClip
from .thumbnail import ThumbnailGenerator, Thumbnail
from .video_editor import VideoEditor, FinalVideo

__all__ = [
    'NewsGatherer', 'NewsStory',
    'ScriptWriter', 'Script',
    'TTSEngine', 'AudioFile',
    'VideoGenerator', 'VideoClip',
    'ThumbnailGenerator', 'Thumbnail',
    'VideoEditor', 'FinalVideo'
]