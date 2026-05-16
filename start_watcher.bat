@echo off
cd /d "%~dp0"
echo Starting auto-watcher for YouTubeNewsChannel...
echo Press Ctrl+C to stop.
python auto_watcher.py
pause
