"""
app.py — AURA Portable Edition
Flask web app. Serves the chat UI and handles all API routes.
"""

import json
import logging
import os
import re
import ast
import operator
import webbrowser
import threading
import time
from flask import Flask, render_template, request, jsonify, Response, stream_with_context

import config
import llm
import web_search
import feature_gate
import speech

# ── Logging ────────────────────────────────────────────────────────
logging.basicConfig(
    filename=os.path.join(config.LOG_DIR, "aura.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")

# ── In-memory conversation history ────────────────────────────────
conversation: list[dict] = []
MAX_HISTORY = 20  # keep last N turns to stay within small model context


def trim_history():
    global conversation
    if len(conversation) > MAX_HISTORY * 2:
        conversation = conversation[-(MAX_HISTORY * 2):]


# ── Safe calculator ────────────────────────────────────────────────
_SAFE_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.Mod: operator.mod, ast.FloorDiv: operator.floordiv,
}

def _safe_eval(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        op = _SAFE_OPS.get(type(node.op))
        if op is None:
            raise ValueError("Unsupported operator")
        return op(_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _SAFE_OPS.get(type(node.op))
        if op is None:
            raise ValueError("Unsupported operator")
        return op(_safe_eval(node.operand))
    raise ValueError(f"Unsupported node: {type(node)}")

def calc(expr: str) -> str:
    try:
        tree = ast.parse(expr.strip(), mode="eval")
        result = _safe_eval(tree.body)
        return f"{expr.strip()} = {result}"
    except Exception as e:
        return f"Math error: {e}"

_CALC_RE = re.compile(
    r'\b(calculate|compute|what is|eval|solve)\b.*?([\d\s\+\-\*\/\^\%\(\)\.]+)',
    re.IGNORECASE
)

def try_calc(text: str) -> str | None:
    m = _CALC_RE.search(text)
    if m:
        expr = m.group(2).strip()
        if any(c.isdigit() for c in expr):
            return calc(expr)
    return None


# ── Routes ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html",
        version=config.VERSION,
        model=llm.best_model(),
        voice_enabled=config.VOICE_ENABLED,
        web_search_enabled=config.WEB_SEARCH_ENABLED,
        download_url=config.DOWNLOAD_URL,
        available=feature_gate.available_features(),
        locked=feature_gate.locked_features(),
        features=feature_gate.FEATURES,
    )


@app.route("/api/status")
def api_status():
    ollama_ok = llm.check_ollama()
    return jsonify({
        "ollama":        ollama_ok,
        "model":         llm.best_model(),
        "voice":         config.VOICE_ENABLED,
        "web_search":    config.WEB_SEARCH_ENABLED,
        "version":       config.VERSION,
        "download_url":  config.DOWNLOAD_URL,
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Non-streaming chat endpoint."""
    data    = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    # 1. Feature gate check
    gate = feature_gate.check_message(message)
    if gate:
        return jsonify({"type": "upgrade", "gate": gate})

    # 2. Calculator shortcut
    calc_result = try_calc(message)
    if calc_result:
        conversation.append({"role": "user", "content": message})
        conversation.append({"role": "assistant", "content": calc_result})
        trim_history()
        return jsonify({"type": "text", "content": calc_result})

    # 3. Web search injection
    search_context = ""
    if config.WEB_SEARCH_ENABLED and web_search.should_search(message):
        results = web_search.search(message)
        if results:
            search_context = "\n\nWeb search results:\n" + web_search.format_for_context(results)

    # 4. Build messages
    user_content = message
    if search_context:
        user_content = message + "\n\n[Context from web search]\n" + search_context

    conversation.append({"role": "user", "content": user_content})
    trim_history()

    response_text = llm.simple_chat(conversation)

    conversation.append({"role": "assistant", "content": response_text})
    trim_history()

    return jsonify({"type": "text", "content": response_text,
                    "searched": bool(search_context)})


@app.route("/api/stream", methods=["POST"])
def api_stream():
    """Streaming chat endpoint using SSE."""
    data    = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    # Feature gate
    gate = feature_gate.check_message(message)
    if gate:
        def gate_stream():
            yield f"data: {json.dumps({'type': 'upgrade', 'gate': gate})}\n\n"
            yield "data: [DONE]\n\n"
        return Response(stream_with_context(gate_stream()),
                        mimetype="text/event-stream")

    # Calculator
    calc_result = try_calc(message)
    if calc_result:
        conversation.append({"role": "user", "content": message})
        conversation.append({"role": "assistant", "content": calc_result})
        trim_history()
        def calc_stream():
            yield f"data: {json.dumps({'type': 'token', 'content': calc_result})}\n\n"
            yield "data: [DONE]\n\n"
        return Response(stream_with_context(calc_stream()),
                        mimetype="text/event-stream")

    # Web search
    search_context = ""
    searched = False
    if config.WEB_SEARCH_ENABLED and web_search.should_search(message):
        results = web_search.search(message)
        if results:
            search_context = "\n\n[Context from web search]\n" + web_search.format_for_context(results)
            searched = True

    user_content = message + search_context
    conversation.append({"role": "user", "content": user_content})
    trim_history()

    def generate():
        full = ""
        if searched:
            yield f"data: {json.dumps({'type': 'meta', 'searched': True})}\n\n"

        for token in llm.stream_chat(list(conversation)):
            full += token
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        conversation.append({"role": "assistant", "content": full})
        trim_history()

        # Optional TTS
        if config.VOICE_ENABLED:
            threading.Thread(target=speech.speak, args=(full,), daemon=True).start()

        yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/api/voice/listen", methods=["POST"])
def api_voice_listen():
    """Capture voice input and return transcription."""
    if not config.VOICE_ENABLED:
        gate = feature_gate.get_upgrade_response("voice")
        return jsonify({"type": "upgrade", "gate": gate})
    text, ok = speech.listen_once()
    return jsonify({"success": ok, "text": text})


@app.route("/api/feature/<key>")
def api_feature(key: str):
    """Return feature info / upgrade prompt for a given key."""
    feat = feature_gate.FEATURES.get(key)
    if not feat:
        return jsonify({"error": "Unknown feature"}), 404
    if feat["available"]:
        return jsonify({"available": True, "feature": feat})
    return jsonify({"available": False, "gate": feature_gate.get_upgrade_response(key)})


@app.route("/api/clear", methods=["POST"])
def api_clear():
    global conversation
    conversation = []
    return jsonify({"ok": True})


# ── Entry point ────────────────────────────────────────────────────

def open_browser():
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{config.FLASK_PORT}")

if __name__ == "__main__":
    logger.info("AURA Portable starting...")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="0.0.0.0", port=config.FLASK_PORT, debug=False, threaded=True)
