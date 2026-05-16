@echo off
cd /d "%~dp0"
echo [%TIME%] Starting YouTube News Automator with activity logging...
python run_with_logging.py
if %ERRORLEVEL% NEQ 0 (
    echo [%TIME%] Process exited with code %ERRORLEVEL%
    pause
)
