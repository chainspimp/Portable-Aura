"""
feature_gate.py — AURA Portable Edition

Defines which features are available on the USB version.
When a locked feature is requested (by chat trigger or button),
returns a friendly upgrade message pointing to the full AURA download.
"""

from config import DOWNLOAD_URL, VOICE_ENABLED, WEB_SEARCH_ENABLED

# ── Feature registry ───────────────────────────────────────────────
#  Each entry: "feature_key": { available, name, reason_locked, icon }

FEATURES = {
    # ── AVAILABLE on USB ──────────────────────────────────────────
    "chat": {
        "available": True,
        "name": "AI Chat",
        "icon": "💬",
        "description": "Talk to AURA via text.",
    },
    "web_search": {
        "available": WEB_SEARCH_ENABLED,
        "name": "Web Search",
        "icon": "🔍",
        "description": "Search the web with DuckDuckGo.",
    },
    "voice": {
        "available": VOICE_ENABLED,
        "name": "Voice I/O",
        "icon": "🎤",
        "description": "Speak to AURA and hear responses.",
        "reason_locked": "Piper TTS or Vosk model not found on this USB."
                         " Add them to runtime/piper/ and runtime/vosk/.",
    },
    "calculator": {
        "available": True,
        "name": "Calculator",
        "icon": "🧮",
        "description": "Evaluate math expressions safely.",
    },
    "memory": {
        "available": True,
        "name": "Session Memory",
        "icon": "🧠",
        "description": "AURA remembers the current conversation.",
    },

    # ── FULL VERSION ONLY ─────────────────────────────────────────
    "computer_use": {
        "available": False,
        "name": "Computer Use",
        "icon": "🖱️",
        "description": "Control your mouse, keyboard and open apps.",
        "reason_locked": "Computer Use requires the full AURA installation "
                         "with PyAutoGUI, screenshot models, and a dedicated "
                         "vision pipeline not included in the portable edition.",
    },
    "vision": {
        "available": False,
        "name": "Webcam Vision",
        "icon": "📷",
        "description": "AURA sees through your webcam in real time.",
        "reason_locked": "Real-time vision requires YOLO + large vision models "
                         "(qwen2.5-vl:7b) not included to keep this USB lightweight.",
    },
    "image_gen": {
        "available": False,
        "name": "Image Generation",
        "icon": "🎨",
        "description": "Generate images with SDXL-Turbo.",
        "reason_locked": "Image generation requires SDXL-Turbo (~6 GB model) "
                         "and a GPU. Not included in the portable edition.",
    },
    "agent_mode": {
        "available": False,
        "name": "Autonomous Agent",
        "icon": "🤖",
        "description": "AURA plans and executes multi-step tasks on its own.",
        "reason_locked": "The autonomous agent needs multiple large models, "
                         "a full tool suite, and persistent memory — only in full AURA.",
    },
    "deep_thinking": {
        "available": False,
        "name": "Deep Thinking Mode",
        "icon": "🧩",
        "description": "Uses DeepSeek-R1 for step-by-step reasoning.",
        "reason_locked": "Deep Thinking requires deepseek-r1:8b (~5 GB). "
                         "The portable edition uses a lightweight 1B model only.",
    },
    "coding_agent": {
        "available": False,
        "name": "VM / Coding IDE",
        "icon": "💻",
        "description": "Build entire projects in an isolated coding environment.",
        "reason_locked": "The VM Coding Agent requires deepseek-coder-v2:16b (~9 GB) "
                         "and a sandboxed execution environment.",
    },
    "security_agent": {
        "available": False,
        "name": "Security / Hacker Agent",
        "icon": "🔐",
        "description": "Penetration testing and network security tools.",
        "reason_locked": "The Security Agent requires WSL, nmap, specialized "
                         "models, and a full network stack not on this USB.",
    },
    "osint": {
        "available": False,
        "name": "OSINT Investigation",
        "icon": "🕵️",
        "description": "Open-source intelligence gathering and investigation tools.",
        "reason_locked": "OSINT tools require additional API keys, scrapers, "
                         "and a larger model context window.",
    },
    "spotify": {
        "available": False,
        "name": "Spotify Control",
        "icon": "🎵",
        "description": "Browse and control Spotify playback.",
        "reason_locked": "Spotify integration requires the Spotipy library "
                         "and API credentials configured in the full AURA setup.",
    },
    "music_recognition": {
        "available": False,
        "name": "Music Recognition",
        "icon": "🎼",
        "description": "Identify any song playing nearby.",
        "reason_locked": "Music recognition requires ACRCloud API credentials "
                         "and the sounddevice/numpy stack configured in full AURA.",
    },
    "self_improvement": {
        "available": False,
        "name": "Self-Improvement",
        "icon": "⚡",
        "description": "AURA rewrites its own code to improve itself.",
        "reason_locked": "Self-improvement modifies source files and requires "
                         "the full codebase and a powerful coding model.",
    },
    "deep_research": {
        "available": False,
        "name": "Deep Research",
        "icon": "📚",
        "description": "Multi-query research synthesised into a full report.",
        "reason_locked": "Deep research fires 5+ parallel searches and needs "
                         "a larger context model. Web Search is available instead.",
    },
}

# ── Trigger keywords that map chat input to a locked feature ───────
TRIGGER_MAP = {
    "computer use":        "computer_use",
    "use computer":        "computer_use",
    "control my":          "computer_use",
    "move mouse":          "computer_use",
    "click on":            "computer_use",
    "open chrome":         "computer_use",
    "open firefox":        "computer_use",
    "open app":            "computer_use",
    "take screenshot":     "computer_use",
    "what do you see":     "vision",
    "look at":             "vision",
    "webcam":              "vision",
    "camera":              "vision",
    "generate image":      "image_gen",
    "generate a picture":  "image_gen",
    "draw me":             "image_gen",
    "create image":        "image_gen",
    "agent mode":          "agent_mode",
    "autonomous":          "agent_mode",
    "deep think":          "deep_thinking",
    "think about":         "deep_thinking",
    "analyse deeply":      "deep_thinking",
    "reason through":      "deep_thinking",
    "hacker mode":         "security_agent",
    "pentest":             "security_agent",
    "hack ":               "security_agent",
    "security scan":       "security_agent",
    "osint":               "osint",
    "investigate ":        "osint",
    "spotify":             "spotify",
    "play music":          "spotify",
    "skip song":           "spotify",
    "what song":           "music_recognition",
    "recognize song":      "music_recognition",
    "identify song":       "music_recognition",
    "improve yourself":    "self_improvement",
    "rewrite your":        "self_improvement",
    "update your code":    "self_improvement",
    "vm mode":             "coding_agent",
    "build mode":          "coding_agent",
    "ide mode":            "coding_agent",
    "build me an app":     "coding_agent",
    "deep research":       "deep_research",
    "research report":     "deep_research",
    "write a report":      "deep_research",
}


def check_message(text: str) -> dict | None:
    """
    Scan a user message for locked-feature triggers.
    Returns a gate response dict if locked, or None if clear.
    """
    lower = text.lower()
    for trigger, key in TRIGGER_MAP.items():
        if trigger in lower:
            feature = FEATURES.get(key)
            if feature and not feature["available"]:
                return _locked_response(key, feature)
    return None


def get_upgrade_response(feature_key: str) -> dict:
    """Return upgrade info for a specific feature key."""
    feature = FEATURES.get(feature_key, {})
    return _locked_response(feature_key, feature)


def _locked_response(key: str, feature: dict) -> dict:
    name   = feature.get("name", key)
    reason = feature.get("reason_locked", "This feature is not available in the portable edition.")
    icon   = feature.get("icon", "🔒")
    return {
        "type":        "upgrade_prompt",
        "feature_key": key,
        "feature_name": name,
        "icon":        icon,
        "message": (
            f"{icon} **{name}** is not available in AURA Portable.\n\n"
            f"{reason}\n\n"
            f"To use this feature, download the full version of AURA:"
        ),
        "download_url": DOWNLOAD_URL,
        "download_label": "⬇️  Download Full AURA",
    }


def available_features() -> list:
    """Return list of features available in this portable build."""
    return [k for k, v in FEATURES.items() if v["available"]]


def locked_features() -> list:
    """Return list of features locked to full AURA."""
    return [k for k, v in FEATURES.items() if not v["available"]]
