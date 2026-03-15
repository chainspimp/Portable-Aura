"""
llm.py — AURA Portable Edition
Streams responses from Ollama using the small local model.
"""

import json
import logging
import requests
from typing import Generator
from config import OLLAMA_URL, AURA_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are AURA — Advanced Unified Reasoning Assistant, Portable Edition.
You are a helpful, direct, and friendly AI assistant running entirely offline on a USB drive.
You have a dark, sleek personality with a dry wit. Keep responses concise and useful.

Portable Edition limits:
- You run on a lightweight 1B model so stay focused and precise.
- You can chat, search the web, do math, and answer questions.
- You do NOT have computer vision, image generation, security tools, or autonomous agents.
  If someone asks for those, you will let them know politely.

Never make up URLs, code outputs, or facts you're unsure about.
If you don't know, say so briefly."""


def check_ollama() -> bool:
    """Return True if Ollama is reachable."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def get_models() -> list[str]:
    """Return list of available model names."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        data = r.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def best_model() -> str:
    """Pick the best available small model. Falls back through options."""
    available = get_models()
    preference = ["llama3.2:1b", "phi3:mini", "gemma3n:e2b", "gemma:2b", "mistral:7b"]
    for m in preference:
        if m in available:
            return m
    # Return whatever's available first
    return available[0] if available else AURA_MODEL


def stream_chat(messages: list[dict], model: str = None) -> Generator[str, None, None]:
    """
    Stream a chat response token by token.
    messages: list of {"role": "user"|"assistant"|"system", "content": "..."}
    Yields string tokens as they arrive.
    """
    model = model or best_model()

    # Prepend system prompt if not already there
    if not messages or messages[0].get("role") != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    payload = {
        "model":    model,
        "messages": messages,
        "stream":   True,
        "options": {
            "temperature":  0.7,
            "num_predict":  512,   # keep responses snappy on small model
            "num_ctx":      4096,
        },
    }

    try:
        with requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
    except requests.exceptions.ConnectionError:
        yield "\n\n⚠️ Cannot reach Ollama. Make sure LAUNCH_AURA.bat started it correctly."
    except requests.exceptions.Timeout:
        yield "\n\n⚠️ Response timed out. The model may be loading — try again in a moment."
    except Exception as e:
        logger.error(f"LLM error: {e}")
        yield f"\n\n⚠️ Error: {str(e)}"


def simple_chat(messages: list[dict], model: str = None) -> str:
    """Non-streaming version. Returns full response string."""
    return "".join(stream_chat(messages, model))
