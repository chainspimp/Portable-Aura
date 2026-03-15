"""
speech.py — AURA Portable Edition
Voice input via Vosk (offline), voice output via Piper TTS.
Both degrade gracefully if hardware or models are missing.
"""

import os
import logging
import subprocess
import tempfile
from config import VOSK_MODEL, PIPER_EXE, PIPER_VOICE, VOICE_ENABLED

logger = logging.getLogger(__name__)


# ── Speech Recognition (Vosk) ──────────────────────────────────────

def listen_once(timeout: float = 8.0) -> tuple[str, bool]:
    """
    Listen for one utterance. Returns (text, success).
    Blocks until speech is detected or timeout.
    """
    if not VOICE_ENABLED:
        return "", False
    if not os.path.exists(VOSK_MODEL):
        return "", False

    try:
        import sounddevice as sd
        import numpy as np
        from vosk import Model, KaldiRecognizer
        import json

        model = Model(VOSK_MODEL)
        rec   = KaldiRecognizer(model, 16000)

        SAMPLE_RATE = 16000
        CHUNK       = 4000
        frames_of_silence = 0
        MAX_SILENCE = int(timeout * SAMPLE_RATE / CHUNK)
        transcript  = ""
        recording   = True

        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=CHUNK,
                               dtype='int16', channels=1) as stream:
            while recording:
                data, _ = stream.read(CHUNK)
                if rec.AcceptWaveform(bytes(data)):
                    result = json.loads(rec.Result())
                    word = result.get("text", "")
                    if word:
                        transcript += " " + word
                        frames_of_silence = 0
                    else:
                        frames_of_silence += 1
                else:
                    partial = json.loads(rec.PartialResult()).get("partial", "")
                    if not partial:
                        frames_of_silence += 1
                    else:
                        frames_of_silence = 0

                if frames_of_silence >= MAX_SILENCE and transcript:
                    recording = False

        return transcript.strip(), bool(transcript.strip())

    except Exception as e:
        logger.error(f"Voice input error: {e}")
        return "", False


# ── Text-to-Speech (Piper) ─────────────────────────────────────────

def speak(text: str) -> bool:
    """
    Speak text using Piper TTS. Returns True on success.
    """
    if not VOICE_ENABLED:
        return False
    if not os.path.exists(PIPER_EXE) or not os.path.exists(PIPER_VOICE):
        return False

    # Truncate very long responses for TTS
    if len(text) > 600:
        text = text[:600] + "..."

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            wav_path = tf.name

        proc = subprocess.run(
            [PIPER_EXE, "--model", PIPER_VOICE, "--output_file", wav_path],
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=30,
        )
        if proc.returncode == 0 and os.path.exists(wav_path):
            # Play with Windows built-in
            subprocess.Popen(
                ["powershell", "-c",
                 f"(New-Object Media.SoundPlayer '{wav_path}').PlaySync()"],
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            )
            return True
    except Exception as e:
        logger.error(f"TTS error: {e}")
    finally:
        try:
            os.unlink(wav_path)
        except Exception:
            pass
    return False
