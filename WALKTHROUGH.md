# YouTube Tech News Channel Automation Tool - Complete Walkthrough

A 100% free, local-only tool to automatically create YouTube videos using AI.

## Prerequisites

### Required Software
1. **Python 3.9+** - Download from python.org
2. **FFmpeg** - Required for video processing
   - Run `install_ffmpeg.bat` in the project folder, OR
   - Install via winget: `winget install ffmpeg`

### Local AI Models
This tool uses local AI (no cloud APIs, no costs):

1. **Ollama** - For script generation
   - Install: `winget install ollama.ollama`
   - Start: `ollama serve`
   - Model auto-downloads on first use

2. **Windows TTS** - Already built into Windows (no install needed)

## Setup Instructions

### Step 1: Install Dependencies
```bash
cd D:\AIprojects\youtubenewschannel
pip install -r requirements.txt
pip install pyttsx3 pywin32
```

### Step 2: Start Ollama (Local LLM)
Open a new terminal and run:
```bash
ollama serve
```
Keep this window open while using the app.

### Step 3: Run the Automation
In a new terminal:
```bash
cd D:\AIprojects\youtubenewschannel
python main.py
```

## What Each Step Does

### Step 1: News Gathering
- Fetches latest tech news from RSS feeds
- Collects 5-10 stories with titles and summaries
- Sources: TechCrunch, Ars Technica, Hacker News

### Step 2: Script Writing
- Uses local Ollama (llama3.2:1b model) to write a narration script
- Creates a 2-minute YouTube-style script with:
  - Hook/intro (10 seconds)
  - Main content covering each story
  - Call to action (10 seconds)
- Generates ~300-500 words

### Step 3: Text-to-Speech
- Uses Windows built-in TTS (SAPI)
- Generates voiceover as WAV file
- Saves to session folder as voiceover.mp3

### Step 4: Video Clips
- Generates animated backgrounds using PIL
- Creates 3 video clips from script topics
- Output format: GIF (can be converted to video)

### Step 5: Thumbnail
- Creates a YouTube thumbnail (1280x720)
- Uses PIL to generate a tech-styled image with title text

### Step 6: Video Assembly
- Creates CapCut-ready output folder
- Contains:
  - `voiceover.mp3` - Your audio
  - `background_loop.gif` - Animated background
  - `title_card.png` - Opening title screen
  - `IMPORT_THIS_INTO_CAPCUT.txt` - Instructions

## Output Location

All output goes to: `D:\AIprojects\youtubenewschannel\outputs\`

Latest session folder contains:
```
final_YYYYMMDD_HHMMSS/
├── background_loop.gif    # Animated background
├── title_card.png         # Opening title
├── voiceover.mp3          # Your voiceover
└── IMPORT_THIS_INTO_CAPCUT.txt
```

## How to Create Final Video

### Option A: CapCut (Recommended)
1. Open CapCut on PC/Mobile
2. Create new project
3. Import from the final_ folder:
   - Add voiceover.mp3 to timeline
   - Add background_loop.gif as video track
   - Add title_card.png at start
4. Export as MP4

### Option B: FFmpeg (Command Line)
```bash
ffmpeg -loop 1 -i background_loop.gif -i voiceover.mp3 -c:v libx264 -c:a aac -shortest output.mp4
```

## Customization

### Change News Sources
Edit `modules/news_gatherer.py` - add your preferred RSS feeds

### Change Voice
Edit `modules/local_tts.py` - the TTSEngine class uses Windows default voice. To change:
- Go to Windows Settings > Time & Language > Speech
- Select different voice

### Change Video Style
Edit `modules/video_editor.py` - customize the PIL-generated frames

### Use Different LLM Model
Edit `modules/local_llm.py` - change DEFAULT_MODEL to:
- "llama3.2:3b" (larger, better quality)
- "phi3" (faster)
- "mistral"

To download new model: `ollama pull llama3.2:3b`

## Troubleshooting

### Ollama not responding
- Make sure `ollama serve` is running in a terminal
- Check port 11434 is not blocked

### No audio generated
- Windows TTS should work automatically
- Check outputs folder for .txt file with script (fallback)

### Video clips not appearing
- PIL fallback generates GIF files
- Check outputs folder for clip_*.gif files

### FFmpeg errors
- Run `install_ffmpeg.bat` to install
- Or download from ffmpeg.org and add to PATH

## Project Structure

```
youtubenewschannel/
├── main.py              # Main orchestrator
├── config.py            # Configuration
├── modules/
│   ├── local_llm.py     # Ollama integration
│   ├── local_tts.py     # Windows TTS
│   ├── local_video.py  # Video generation
│   ├── news_gatherer.py # RSS feeds
│   ├── thumbnail.py    # Thumbnail generation
│   └── video_editor.py # Assembly
├── outputs/             # Generated content
├── utils/               # Helpers
└── requirements.txt    # Python packages
```

## Running Automatically

### Schedule Daily Videos
Create a batch file (run_daily.bat):
```batch
@echo off
cd D:\AIprojects\youtubenewschannel
python main.py
```

Add to Windows Task Scheduler to run daily at a set time.

### Watch Mode (Auto-run on new files)
```bash
python auto_watcher.py
```
Monitors for changes and runs automatically.

## Tips for Better Results

1. **More stories** - Edit config.py MAX_STORIES
2. **Longer scripts** - Adjust max_tokens in local_llm.py
3. **Better video** - Install Stable Diffusion locally for AI-generated images
4. **Different voice** - Use third-party TTS like Coqui TTS (requires GPU)

## Cost

**Total cost: $0** - Everything runs locally on your machine.

- Ollama: Free (local)
- TTS: Free (Windows built-in)
- Video: Free (PIL library)
- News: Free (RSS feeds)