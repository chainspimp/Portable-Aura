@echo off
setlocal EnableDelayedExpansion
title AURA Portable — First Time Setup
color 0A

set "USB=%~dp0"
set "USB=%USB:~0,-1%"

cls
echo.
echo  ╔═══════════════════════════════════════════════════════╗
echo  ║        AURA PORTABLE — FIRST TIME SETUP              ║
echo  ║   Run this ONCE to build the full USB environment.   ║
echo  ╚═══════════════════════════════════════════════════════╝
echo.
echo   USB Root : %USB%
echo.
echo   Downloads needed:
echo    - Python 3.11 Embeddable    ~25  MB
echo    - Python packages           ~400 MB
echo    - Ollama (portable)         ~50  MB
echo    - Vosk speech model         ~40  MB
echo    - AI model (llama3.2:1b)    ~1.3 GB   <- tiny, runs on anything
echo.
echo   Total: ~2 GB minimum.  Recommended USB size: 8 GB+
echo.
pause

:: ── Internet check ──────────────────────────────────────────────────
ping -n 1 8.8.8.8 >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] No internet connection. Connect and re-run.
    pause & exit /b 1
)
echo  [OK] Internet available.

:: ── Folder structure ────────────────────────────────────────────────
echo.
echo  [1/7] Creating folder structure...
for %%D in (
    runtime\python
    runtime\python\Lib\site-packages
    runtime\python\Scripts
    runtime\ollama
    runtime\ollama\models
    runtime\piper
    runtime\piper\voices
    runtime\vosk
    src\templates
    src\static
    data\logs
    data\memory
    data\code
    data\images
) do mkdir "%USB%\%%D" 2>nul
echo   [OK] Folders created.

:: ── Python embeddable ────────────────────────────────────────────────
echo.
echo  [2/7] Downloading Python 3.11 embeddable (64-bit)...
if exist "%USB%\runtime\python\python.exe" (
    echo   [SKIP] Already installed.
) else (
    powershell -Command "$p='SilentlyContinue';$ProgressPreference=$p;[Net.ServicePointManager]::SecurityProtocol='Tls12';(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip','%USB%\runtime\python\_py.zip')"
    if errorlevel 1 ( echo  [ERROR] Python download failed. & pause & exit /b 1 )
    powershell -Command "Expand-Archive '%USB%\runtime\python\_py.zip' '%USB%\runtime\python' -Force"
    del "%USB%\runtime\python\_py.zip" 2>nul

    :: Unlock site-packages for embeddable Python
    powershell -Command "(Get-Content '%USB%\runtime\python\python311._pth') -replace '#import site','import site' | Set-Content '%USB%\runtime\python\python311._pth'"

    :: Bootstrap pip
    echo   Installing pip...
    powershell -Command "$ProgressPreference='SilentlyContinue';(New-Object Net.WebClient).DownloadFile('https://bootstrap.pypa.io/get-pip.py','%USB%\runtime\python\get-pip.py')"
    "%USB%\runtime\python\python.exe" "%USB%\runtime\python\get-pip.py" --no-warn-script-location -q
    del "%USB%\runtime\python\get-pip.py" 2>nul
    echo   [OK] Python + pip ready.
)

:: ── Python packages ──────────────────────────────────────────────────
echo.
echo  [3/7] Installing Python packages...
set "PIP=%USB%\runtime\python\Scripts\pip.exe"
set "SITE=%USB%\runtime\python\Lib\site-packages"

"%PIP%" install flask requests python-dotenv duckduckgo-search ^
    vosk sounddevice numpy pyautogui keyboard ^
    --target="%SITE%" --no-warn-script-location -q

if errorlevel 1 ( echo  [ERROR] Package install failed. & pause & exit /b 1 )
echo   [OK] Packages installed.

:: ── Ollama portable ──────────────────────────────────────────────────
echo.
echo  [4/7] Downloading Ollama portable binary...
if exist "%USB%\runtime\ollama\ollama.exe" (
    echo   [SKIP] Already downloaded.
) else (
    powershell -Command "$ProgressPreference='SilentlyContinue';[Net.ServicePointManager]::SecurityProtocol='Tls12';(New-Object Net.WebClient).DownloadFile('https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip','%USB%\runtime\ollama\_ol.zip')"
    if errorlevel 1 ( echo  [ERROR] Ollama download failed. & pause & exit /b 1 )
    powershell -Command "Expand-Archive '%USB%\runtime\ollama\_ol.zip' '%USB%\runtime\ollama' -Force"
    del "%USB%\runtime\ollama\_ol.zip" 2>nul
    echo   [OK] Ollama downloaded.
)

:: ── Vosk speech model ────────────────────────────────────────────────
echo.
echo  [5/7] Downloading Vosk speech model (~40MB)...
if exist "%USB%\runtime\vosk\vosk-model-small-en-us-0.15\README" (
    echo   [SKIP] Already downloaded.
) else (
    powershell -Command "$ProgressPreference='SilentlyContinue';(New-Object Net.WebClient).DownloadFile('https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip','%USB%\runtime\vosk\_vosk.zip')"
    powershell -Command "Expand-Archive '%USB%\runtime\vosk\_vosk.zip' '%USB%\runtime\vosk' -Force"
    del "%USB%\runtime\vosk\_vosk.zip" 2>nul
    echo   [OK] Vosk model downloaded.
)

:: ── Pull AI model ────────────────────────────────────────────────────
echo.
echo  [6/7] Pulling AI model...
echo   Using llama3.2:1b  (1.3 GB — runs on ANY device, even low-end PCs)
echo   This model is small enough to run on CPU with 4GB RAM.
echo.
set "OLLAMA_MODELS=%USB%\runtime\ollama\models"
set "OLLAMA_HOME=%USB%\runtime\ollama"
set "PATH=%USB%\runtime\ollama;%PATH%"

:: Start Ollama temporarily to pull
start "" /B "%USB%\runtime\ollama\ollama.exe" serve
timeout /t 5 /nobreak >nul

"%USB%\runtime\ollama\ollama.exe" pull llama3.2:1b

echo.
set /p PULL_PHI="   Also pull phi3:mini (2.3GB, smarter but needs 8GB RAM)? (Y/N): "
if /i "!PULL_PHI!"=="Y" "%USB%\runtime\ollama\ollama.exe" pull phi3:mini

:: Stop temp Ollama instance
taskkill /F /IM ollama.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: ── Write config ─────────────────────────────────────────────────────
echo.
echo  [7/7] Writing configuration...
(
echo AURA_VERSION=portable
echo AURA_MODEL=llama3.2:1b
echo OLLAMA_URL=http://localhost:11434
echo VOSK_MODEL=__VOSK__
echo PIPER_EXE=__PIPER__
echo PIPER_VOICE=__PIPER_VOICE__
echo VOICE_ENABLED=false
echo WEB_SEARCH_ENABLED=true
echo FLASK_PORT=7860
echo DOWNLOAD_URL=https://github.com/YourRepo/AURA
) > "%USB%\src\.env.template"
echo   [OK] Config template written.

echo.
echo  ╔═══════════════════════════════════════════════════════╗
echo  ║                  SETUP COMPLETE!                     ║
echo  ║                                                       ║
echo  ║   OPTIONAL: Add Piper TTS for voice output           ║
echo  ║   1. Download piper_windows_amd64.zip from:          ║
echo  ║      github.com/rhasspy/piper/releases               ║
echo  ║   2. Extract into:  runtime\piper\                   ║
echo  ║   3. Get a voice model (.onnx) from:                 ║
echo  ║      rhasspy.github.io/piper-samples                 ║
echo  ║   4. Put it in:     runtime\piper\voices\            ║
echo  ║                                                       ║
echo  ║   Then plug into any PC and run LAUNCH_AURA.bat      ║
echo  ╚═══════════════════════════════════════════════════════╝
echo.
pause
endlocal
