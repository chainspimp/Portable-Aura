@echo off
title AURA Portable — Stopping
color 0C
echo.
echo  Shutting down AURA Portable...
taskkill /F /IM ollama.exe   >nul 2>&1
taskkill /F /IM python.exe   >nul 2>&1
taskkill /F /IM pythonw.exe  >nul 2>&1
echo  [OK] All processes stopped.
echo  Safe to unplug your USB drive.
echo.
timeout /t 3 /nobreak >nul
