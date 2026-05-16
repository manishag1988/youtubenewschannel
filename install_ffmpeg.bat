@echo off
echo Installing FFmpeg for video assembly...
echo.

:: Check if chocolatey is installed
where choco >nul 2>nul
if %errorlevel% == 0 (
    choco install ffmpeg -y
) else (
    echo Chocolatey not found. Downloading FFmpeg manually...
    echo.

    :: Create temp directory
    if not exist "%TEMP%\ffmpeg_install" mkdir "%TEMP%\ffmpeg_install"
    cd "%TEMP%\ffmpeg_install"

    :: Download FFmpeg (static build)
    echo Downloading FFmpeg static build...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/GyanD/codexffmpeg/releases/download/7.1/ffmpeg-7.1-essentials_build.zip' -OutFile 'ffmpeg.zip'"

    echo Extracting...
    powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"

    :: Copy ffmpeg.exe to Windows\System32
    echo Installing...
    xcopy /Y "ffmpeg-7.1-essentials_build\bin\ffmpeg.exe" "C:\Windows\System32\"

    echo.
    echo FFmpeg installed! Run 'ffmpeg -version' to verify.
)

pause