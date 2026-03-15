# ⚡ AURA Portable

> A fully self-contained, plug-and-play AI assistant that lives on a USB drive.  
> No installation. No internet required (after setup). Works on any Windows PC.

---

## What's included

| Feature | Portable | Full AURA |
|---|---|---|
| AI Chat | ✅ | ✅ |
| Web Search (DuckDuckGo) | ✅ | ✅ |
| Calculator | ✅ | ✅ |
| Session Memory | ✅ | ✅ |
| Voice I/O (if Piper added) | ✅ | ✅ |
| Computer Use (mouse/keyboard) | ❌ → prompts download | ✅ |
| Webcam Vision | ❌ → prompts download | ✅ |
| Image Generation | ❌ → prompts download | ✅ |
| Deep Thinking (DeepSeek-R1) | ❌ → prompts download | ✅ |
| Autonomous Agent | ❌ → prompts download | ✅ |
| Coding / VM IDE | ❌ → prompts download | ✅ |
| Security / Hacker Agent | ❌ → prompts download | ✅ |
| OSINT Tools | ❌ → prompts download | ✅ |
| Spotify Control | ❌ → prompts download | ✅ |
| Music Recognition | ❌ → prompts download | ✅ |
| Self-Improvement | ❌ → prompts download | ✅ |
| Deep Research | ❌ → prompts download | ✅ |

Locked features show a friendly in-chat card with a download link to full AURA.

---

## USB structure

```
USB:\
├── LAUNCH_AURA.bat       ← Double-click to start
├── STOP_AURA.bat         ← Run before unplugging
├── SETUP_USB.bat         ← Run ONCE to build everything
├── README.md
│
├── src\                  ← AURA Portable source (don't edit)
│   ├── app.py
│   ├── config.py
│   ├── feature_gate.py
│   ├── llm.py
│   ├── web_search.py
│   ├── speech.py
│   └── templates\
│       └── index.html
│
├── runtime\              ← Built by SETUP_USB.bat
│   ├── python\           ← Portable Python 3.11 + packages
│   ├── ollama\           ← Ollama binary + AI models
│   ├── piper\            ← Piper TTS (manual download)
│   └── vosk\             ← Vosk speech model
│
└── data\                 ← Your data (stays on USB)
    ├── memory\
    ├── logs\
    ├── code\
    └── images\
```

---

## First-time setup

1. Copy all files to a **USB 3.0 drive (8GB+ recommended)**
2. Run **`SETUP_USB.bat`** — takes ~20 min, downloads everything automatically
3. *(Optional)* Add Piper TTS for voice:
   - Download from https://github.com/rhasspy/piper/releases
   - Extract into `runtime\piper\`
   - Download a voice model (.onnx) from https://rhasspy.github.io/piper-samples/
   - Place in `runtime\piper\voices\`

---

## Daily use

1. Plug in USB
2. Double-click **`LAUNCH_AURA.bat`**
3. Your browser opens at `http://localhost:7860`
4. Run **`STOP_AURA.bat`** before unplugging

---

## AI Model

The portable edition uses **llama3.2:1b** — a 1.3 GB model that runs on any PC including old laptops with no GPU. It's fast and capable for chat and Q&A.

If you have more RAM and storage, `SETUP_USB.bat` offers to also pull **phi3:mini** (2.3 GB, smarter).

---

## How locked features work

When you click a 🔒 feature in the sidebar **or** ask AURA to do something only in the full version (e.g. "generate an image", "pentest this IP", "control my computer"), AURA shows an in-chat upgrade card explaining why it's locked and linking to the full download.

It detects these requests by scanning your message for trigger keywords — no false positives, no crashes.

---

## Troubleshooting

**"Python not found"** → Run `SETUP_USB.bat` first.

**AURA doesn't open** → Check `data\logs\aura.log` and `data\logs\ollama.log`.

**Ollama won't start** → Try opening a cmd window and running `runtime\ollama\ollama.exe serve` manually to see errors.

**Slow responses** → Use a USB 3.0 port. The 1B model is fast even on CPU but USB 2.0 slows file reads.
