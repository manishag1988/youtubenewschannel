# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Initial CHANGELOG.md to track project changes

---

## 2026-05-16

### auto: update 14:23
- **video_generator.py**: Added 15 lines of new functionality

### auto: update 14:22
- **video_generator.py**: Added 50 lines of new functionality

### auto: update 14:22
- **video_generator.py**: Refactored and optimized (23 insertions, 33 deletions)

### auto: update 14:21
- **install_ffmpeg.bat**: Created batch script for ffmpeg installation (32 lines)

### auto: update 14:18
- **config.py**: Updated configuration values

### auto: update 14:17
- **tts.py**: Cleaned up code (1 insertion, 3 deletions)

### auto: update 14:15
- **tts.py**: Removed 9 lines of unused code

### auto: update 14:14
- **tts.py**: Simplified TTS module (4 insertions, 26 deletions)

### auto: update 14:14
- **config.py**: Added 3 new configuration options

### auto: update 14:13
- **logger.py**: Fixed logging format (2 insertions, 1 deletion)

### auto: update 14:13
- **logger.py**: Improved log formatting (2 insertions, 1 deletion)

### auto: update 14:10
- **.github/workflows/run_automation.yml**: Added GitHub Actions CI/CD workflow (88 lines)
- **README.md**: Expanded documentation (58 lines)

### Add auto-watcher script, .gitignore, and .gitkeep
- **auto_watcher.py**: Created file system watcher for automatic git commits/pushes (92 lines)
- **.gitignore**: Added ignore rules for Python cache, logs, env, and outputs
- **outputs/.gitkeep**: Added placeholder to track outputs directory
- **start_watcher.bat**: Created batch script to launch auto-watcher

### Initial commit
- **main.py**: Core orchestrator with 6-step YouTube video automation pipeline (387 lines)
- **config.py**: Central configuration with dataclass-style config groups (241 lines)
- **modules/**: Core pipeline modules:
  - **script_writer.py**: LLM-powered script generation with multi-provider support (392 lines)
  - **tts.py**: Text-to-speech engine with multiple fallback providers (369 lines)
  - **video_generator.py**: AI video clip generation with multiple providers (375 lines)
  - **video_editor.py**: Final video assembly with moviepy/ffmpeg (341 lines)
  - **thumbnail.py**: Thumbnail generation with multiple providers (368 lines)
  - **news_gatherer.py**: RSS news aggregation from 7+ tech feeds (229 lines)
  - **__init__.py**: Module exports (17 lines)
- **utils/**: Utility modules:
  - **file_manager.py**: File I/O and session management (103 lines)
  - **logger.py**: Colored console + file logging (76 lines)
  - **rate_limiter.py**: API rate limit tracking with daily resets (109 lines)
  - **__init__.py**: Utility exports (7 lines)
- **requirements.txt**: Python dependencies (33 lines)
- **free_ai_youtube_roadmap.md**: Comprehensive free AI tools guide (192 lines)
- **README.md**: Project documentation (101 lines)

### auto: update 14:53
- **odules/tts.py**: Modified

### auto: update 14:57
- **odules/tts.py**: Modified

### auto: update 15:04
- **odules/tts.py**: Modified

### auto: update 15:15
- **odules/tts.py**: Modified
