@echo off
setlocal EnableDelayedExpansion
title AURA Portable
color 0A

:: ════════════════════════════════════════════════════
::  AURA PORTABLE — PLUG AND PLAY LAUNCHER
::  Auto-detects drive letter. Works on any Windows PC.
::  Just double-click from the USB drive.
:: ════════════════════════════════════════════════════

set "USB=%~dp0"
set "USB=%USB:~0,-1%"

set "PYTHON=%USB%\runtime\python\python.exe"
set "SITE=%USB%\runtime\python\Lib\site-packages"
set "OLLAMA=%USB%\runtime\ollama\ollama.exe"
set "VOSK=%USB%\runtime\vosk\vosk-model-small-en-us-0.15"
set "PIPER=%USB%\runtime\piper\piper.exe"
set "PIPER_VOICE=%USB%\runtime\piper\voices\en_US-hfc_female-medium.onnx"
set "SRC=%USB%\src"
set "DATA=%USB%\data"
set "LOG=%DATA%\logs\launch.log"

cls
echo.
echo  ░█████╗░██╗░░░██╗██████╗░░█████╗░
echo  ██╔══██╗██║░░░██║██╔══██╗██╔══██╗
echo  ███████║██║░░░██║██████╔╝███████║
echo  ██╔══██║██║░░░██║██╔══██╗██╔══██║
echo  ██║░░██║╚██████╔╝██║░░██║██║░░██║
echo  ╚═╝░░╚═╝░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝
echo.
echo   P O R T A B L E   E D I T I O N
echo   Drive: %USB%
echo.

:: ── Validate setup ──────────────────────────────────────
set "OK=1"
if not exist "%PYTHON%"         ( echo  [MISSING] Python   — Run SETUP_USB.bat first!  & set "OK=0" )
if not exist "%OLLAMA%"         ( echo  [MISSING] Ollama   — Run SETUP_USB.bat first!  & set "OK=0" )
if not exist "%SRC%\app.py"     ( echo  [MISSING] app.py   — Corrupt install?          & set "OK=0" )
if "%OK%"=="0" ( echo. & pause & exit /b 1 )

:: ── Detect optional voice components ────────────────────
set "VOICE=false"
if exist "%PIPER%"       set "VOICE=true"
if not exist "%PIPER%"   echo  [INFO] Piper TTS not found — voice output disabled.
if not exist "%VOSK%"    echo  [INFO] Vosk model not found — voice input disabled.

:: ── Set environment ──────────────────────────────────────
set "PYTHONPATH=%SITE%;%SRC%"
set "PYTHONHOME=%USB%\runtime\python"
set "PATH=%USB%\runtime\python;%USB%\runtime\python\Scripts;%USB%\runtime\ollama;%PATH%"
set "OLLAMA_MODELS=%USB%\runtime\ollama\models"
set "OLLAMA_HOME=%USB%\runtime\ollama"

:: ── Write resolved .env ──────────────────────────────────
echo  Writing configuration...
(
echo AURA_VERSION=portable
echo AURA_USB_ROOT=%USB%
echo AURA_DATA_DIR=%DATA%
echo OLLAMA_URL=http://localhost:11434
echo AURA_MODEL=llama3.2:1b
echo VOSK_MODEL=%VOSK%
echo PIPER_EXE=%PIPER%
echo PIPER_VOICE=%PIPER_VOICE%
echo VOICE_ENABLED=%VOICE%
echo WEB_SEARCH_ENABLED=true
echo FLASK_PORT=7860
echo DOWNLOAD_URL=https://github.com/YourRepo/AURA
) > "%SRC%\.env"
echo  [OK] Config written.

:: ── Start Ollama ─────────────────────────────────────────
echo.
echo  Starting Ollama AI engine...
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if %ERRORLEVEL%==0 (
    echo  [OK] Ollama already running.
) else (
    start "" /B "%OLLAMA%" serve >> "%DATA%\logs\ollama.log" 2>&1
    echo  Waiting for Ollama to be ready...
    set "READY=0"
    for /L %%i in (1,1,25) do (
        if "!READY!"=="0" (
            timeout /t 1 /nobreak >nul
            powershell -Command "try{$null=(Invoke-WebRequest 'http://localhost:11434' -TimeoutSec 1 -UseBasicParsing);exit 0}catch{exit 1}" >nul 2>&1
            if !ERRORLEVEL!==0 ( set "READY=1" & echo  [OK] Ollama is ready. )
        )
    )
    if "!READY!"=="0" echo  [WARN] Ollama slow to start — AURA may need a moment.
)

:: ── Launch AURA ──────────────────────────────────────────
echo.
echo  Launching AURA Portable...
cd /d "%SRC%"
start "" "%PYTHON%" app.py >> "%LOG%" 2>&1

:: Wait for Flask to start then open browser
timeout /t 3 /nobreak >nul
start "" "http://localhost:7860"

echo.
echo  ─────────────────────────────────────────────────
echo   AURA is running at http://localhost:7860
echo   Your browser should open automatically.
echo   Run STOP_AURA.bat before unplugging the USB.
echo  ─────────────────────────────────────────────────
echo.
timeout /t 5 /nobreak >nul
endlocal
