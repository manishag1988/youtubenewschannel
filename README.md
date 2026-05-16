# YouTube Tech News Channel Automation Tool

A fully automated tool for creating tech news YouTube videos using 100% free AI tools with automatic fallback support.

## Features

- **News Gathering**: Automatic RSS aggregation from top tech sources
- **Script Writing**: AI-powered script generation using LLMs (with fallback)
- **Text-to-Speech**: Multiple free TTS services (TTSMP3, SoundTools, Out Loud)
- **Video Generation**: AI video clips from Kling, LoreMotion, Free.ai (with fallback)
- **Thumbnail Creation**: Auto-generated thumbnails (Thumb-Free, Canva, Leonardo)
- **Video Assembly**: Complete video assembly with audio and clips
- **Fallback Support**: Every module has fallback services if primary fails

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Configuration

### API Keys (Optional - Fallbacks Work Without)

Set environment variables for enhanced services:

```bash
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export KLING_API_KEY="your-key"
export LEONARDO_API_KEY="your-key"
```

### No API Keys? No Problem!

The tool works with **zero API keys** using these free services:

| Service | Type | Limit |
|---------|------|-------|
| TTSMP3 | Browser TTS | Unlimited |
| LoreMotion | Video Generation | Unlimited (ad-supported) |
| Feedly | News | Free tier |
| Thumb-Free | Thumbnails | Unlimited |
| ChatGPT Fallback | Script | Template-based |

## Project Structure

```
youtubenewschannel/
├── main.py                 # Main orchestrator
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── README.md              # This file
├── modules/
│   ├── news_gatherer.py    # RSS news aggregation
│   ├── script_writer.py    # Script generation with LLM
│   ├── tts.py             # Text-to-speech
│   ├── video_generator.py # AI video generation
│   ├── thumbnail.py       # Thumbnail generation
│   └── video_editor.py    # Video assembly
├── utils/
│   ├── logger.py          # Logging
│   ├── rate_limiter.py    # API rate limiting
│   └── file_manager.py    # File handling
└── outputs/               # Generated content
```

## Workflow

1. **News Gathering** → Fetch from TechCrunch, The Verge, Ars Technica, etc.
2. **Script Writing** → Generate engaging narration from news
3. **Voiceover** → Convert script to audio
4. **Video Generation** → Create AI B-roll clips
5. **Thumbnail** → Generate click-worthy thumbnail
6. **Assembly** → Combine all into final video

## Requirements

- Python 3.8+
- requests
- feedparser
- moviepy (for video assembly)
- Pillow (for placeholder thumbnails)
- ffmpeg (optional, for advanced video assembly)

## Notes

- All tools verified as 100% free as of May 2026
- Most services work without signup
- Fallbacks ensure workflow never fails
- Rate limiters prevent service abuse

---

## Running on GitHub Actions (Cloud)

You can run the automation in the cloud without your local machine!

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Add GitHub Actions workflow"
git push origin main
```

### 2. Configure Secrets (Optional - for better AI quality)

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets (get free keys from each service):

| Secret Name | Service | Free Tier |
|-------------|---------|-----------|
| `OPENAI_API_KEY` | OpenAI | Limited |
| `GEMINI_API_KEY` | Google Gemini | Yes |
| `KLING_API_KEY` | Kling AI | 66/day |
| `LEONARDO_API_KEY` | Leonardo AI | 150/day |

**Without secrets**, the app still works using fallback services!

### 3. Run Workflow

1. Go to **Actions** tab in your GitHub repo
2. Click **YouTube News Automation** → **Run workflow**
3. Choose number of videos or run on schedule

### 4. Download Outputs

After workflow completes, download artifacts:
- **generated-content**: Scripts, audio, thumbnails
- **automation-logs**: Full execution logs
- **youtube-automation-outputs**: All generated files

---

### Scheduled Runs

The workflow can run automatically. Edit `.github/workflows/run_automation.yml` to adjust:

```yaml
# Run every day at 8 AM UTC
schedule:
  - cron: '0 8 * * *'

# Or manually trigger anytime
workflow_dispatch:
```

---

## License

MIT