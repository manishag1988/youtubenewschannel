# YouTube Tech News Channel Automation Tool

A fully automated tool for creating tech news YouTube videos using 100% free AI tools with automatic fallback support, local AI inference, and CI/CD deployment.

## Features

- **News Gathering**: Automatic RSS aggregation from 7+ top tech sources (TechCrunch, The Verge, Ars Technica, Wired, Engadget, NYT)
- **Script Writing**: AI-powered script generation with multi-provider LLM support (ChatGPT, Gemini, Claude, DeepSeek) + fallback templates
- **Local LLM**: Offline script generation via Ollama (llama3.2, Mistral, Phi-3, Gemma)
- **Text-to-Speech**: Multiple TTS options — Windows SAPI, Piper, Coqui XTTS, or placeholder audio
- **Video Generation**: AI video clips via local Stable Diffusion, ComfyUI, or PIL-based fallback animation
- **Thumbnail Creation**: Auto-generated PIL-based thumbnails with title overlay
- **Video Assembly**: Complete CapCut-ready output with background animation, title cards, and import guide
- **Activity Logging**: Structured JSONL logging of all workflow activity with automatic log interception
- **Rate Limiting**: Daily credit tracking across all services to prevent abuse
- **Auto-Watcher**: File system monitoring with automatic git commit, changelog update, and push
- **CI/CD Ready**: GitHub Actions workflow for cloud execution with artifact upload

## Installation

```bash
pip install -r requirements.txt
```

### Optional Local AI (for offline/fully-free operation)

1. **Ollama** (local LLM): Run `local_ai/ollama/install.ps1` or install from https://ollama.ai
2. **Piper TTS** (local voice): Extract `local_ai/piper/piper.zip`
3. **Stable Diffusion**: Install Automatic1111 at http://127.0.0.1:7860
4. **FFmpeg**: Run `install_ffmpeg.bat` or install manually

## Usage

```bash
# Standard run
python main.py

# With activity logging
python run_with_logging.py

# Or double-click the batch files
start_with_logging.bat
start_watcher.bat
```

## Project Structure

```
youtubenewschannel/
├── main.py                          # Main orchestrator (6-step pipeline)
├── config.py                        # Central configuration (all service settings)
├── activity_logger.py               # Standalone JSONL activity logging
├── run_with_logging.py              # Log interception wrapper
├── auto_watcher.py                  # Git auto-watcher with changelog updates
├── install_ffmpeg.bat               # FFmpeg installer
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
├── CHANGELOG.md                     # Auto-generated changelog
├── activity_log.jsonl               # Structured activity log
├── workflow_log.txt                 # Workflow execution log
│
├── modules/
│   ├── news_gatherer.py             # RSS news aggregation + AI curation
│   ├── script_writer.py             # LLM script gen (ChatGPT/Gemini/Claude/DeepSeek)
│   ├── tts.py                       # Text-to-speech (placeholder)
│   ├── video_generator.py           # PIL-based animated GIF generation
│   ├── thumbnail.py                 # PIL-based thumbnail generation
│   ├── video_editor.py              # CapCut-ready video assembly
│   ├── local_llm.py                 # Ollama local LLM integration
│   ├── local_tts.py                 # Windows SAPI / Piper / Coqui TTS
│   ├── local_video.py               # Stable Diffusion / PIL video gen
│   └── __init__.py                  # Module exports
│
├── utils/
│   ├── logger.py                    # Colored console + file logging
│   ├── rate_limiter.py              # API rate limit tracking
│   ├── file_manager.py              # File I/O and session management
│   └── __init__.py                  # Utility exports
│
├── local_ai/
│   ├── ollama/install.ps1           # Ollama setup script
│   └── piper/piper.zip              # Piper TTS binary
│
├── .github/workflows/
│   └── run_automation.yml           # GitHub Actions CI/CD pipeline
│
├── outputs/                         # Generated videos, scripts, thumbnails
│   └── .gitkeep
│
├── test_steps.py                    # End-to-end pipeline test
└── test_video_editor.py             # Video editor integration test
```

## Workflow (6-Step Pipeline)

1. **News Gathering** → Fetch from TechCrunch, The Verge, Ars Technica, etc.
2. **Script Writing** → Generate engaging narration via LLM (local or cloud)
3. **Voiceover** → Convert script to audio via local TTS or placeholder
4. **Video Generation** → Create AI B-roll clips (SD or PIL animation)
5. **Thumbnail** → Generate click-worthy thumbnail with title overlay
6. **Assembly** → Combine all into CapCut-ready output with import guide

## API Configuration

### Optional API Keys (for enhanced quality)

```bash
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export CLAUDE_API_KEY="your-key"
export DEEPSEEK_API_KEY="your-key"
export KLING_API_KEY="your-key"
export LEONARDO_API_KEY="your-key"
```

### Without API Keys — 100% Free + Local

The tool works with **zero API keys** using these free/local services:

| Service | Type | Description |
|---------|------|-------------|
| Ollama | Local LLM | llama3.2, Mistral, Phi-3, Gemma |
| Piper/Coqui | Local TTS | Windows SAPI voice synthesis |
| Stable Diffusion | Local Video | Automatic1111 / ComfyUI |
| PIL | Fallback | Animated GIF + thumbnail generation |
| RSS Feeds | Free News | TechCrunch, The Verge, Ars, Wired, etc. |

## Activity Logging

All workflow runs are automatically logged to `activity_log.jsonl` in structured JSONL format:

```json
{"timestamp": "...", "level": "INFO", "source": "main", "message": "...", "detail": {...}}
```

View activity summary:
```python
from activity_logger import summary, read_filter
print(summary())
print(read_filter(level="ERROR"))
```

## CI/CD (GitHub Actions)

Push to GitHub and the workflow runs automatically. Configure secrets in GitHub repo settings:
- `OPENAI_API_KEY`, `GEMINI_API_KEY`, `KLING_API_KEY`, `LEONARDO_API_KEY`

Workflow uploads: generated content, logs, and all outputs as build artifacts.

## Changelog

All changes auto-tracked in `CHANGELOG.md` via the auto-watcher. See the file for full history.

## License

MIT
