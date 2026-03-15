"""
config.py — AURA Portable Edition
All paths are injected by LAUNCH_AURA.bat via the .env file.
Never hardcodes drive letters so this works on any PC.
"""

import os
from dotenv import load_dotenv

_HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_HERE, ".env"), override=True)

# ── Identity ───────────────────────────────────────────────────────
VERSION       = os.getenv("AURA_VERSION", "portable")
USB_ROOT      = os.getenv("AURA_USB_ROOT", _HERE)
DATA_DIR      = os.getenv("AURA_DATA_DIR", os.path.join(USB_ROOT, "data"))
DOWNLOAD_URL  = os.getenv("DOWNLOAD_URL", "https://github.com/YourRepo/AURA")

# ── AI ─────────────────────────────────────────────────────────────
OLLAMA_URL    = os.getenv("OLLAMA_URL", "http://localhost:11434")
AURA_MODEL    = os.getenv("AURA_MODEL", "llama3.2:1b")

# ── Voice ──────────────────────────────────────────────────────────
VOSK_MODEL    = os.getenv("VOSK_MODEL", "")
PIPER_EXE     = os.getenv("PIPER_EXE", "")
PIPER_VOICE   = os.getenv("PIPER_VOICE", "")
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "false").lower() == "true"

# Verify voice assets actually exist
if VOICE_ENABLED:
    if not os.path.exists(PIPER_EXE) or not os.path.exists(PIPER_VOICE):
        VOICE_ENABLED = False
    if not os.path.exists(VOSK_MODEL):
        VOICE_ENABLED = False

# ── Features ───────────────────────────────────────────────────────
WEB_SEARCH_ENABLED = os.getenv("WEB_SEARCH_ENABLED", "true").lower() == "true"

# ── Server ─────────────────────────────────────────────────────────
FLASK_PORT    = int(os.getenv("FLASK_PORT", 7860))

# ── Paths ──────────────────────────────────────────────────────────
LOG_DIR       = os.path.join(DATA_DIR, "logs")
MEMORY_FILE   = os.path.join(DATA_DIR, "memory", "memory.json")
CODE_DIR      = os.path.join(DATA_DIR, "code")
IMAGE_DIR     = os.path.join(DATA_DIR, "images")

for d in (LOG_DIR, os.path.dirname(MEMORY_FILE), CODE_DIR, IMAGE_DIR):
    os.makedirs(d, exist_ok=True)
