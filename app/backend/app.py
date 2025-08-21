import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Services (see services/__init__.py exporting these symbols)
from .services import (
    speech_to_text,     # (file_like) -> str
    generate_response,  # (topic, user_text, summary=None, recent_messages=None) -> str
    synthesize_tts,     # (text) -> bytes
    get_random_topic,   # () -> str
)

# --- Paths & Flask static config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "public"))
MEDIA_DIR = os.path.join(PUBLIC_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path="")

# --- Helpers ---
def _save_bytes_to_media(data: bytes, ext: str = "mp3") -> str:
    name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(MEDIA_DIR, name)
    with open(path, "wb") as f:
        f.write(data)
    return f"/media/{name}"

# --- Static routes ---
@app.get("/")
def index():
    return app.send_static_file("index.html")

@app.get("/media/<path:filename>")
def media(filename: str):
    return send_from_directory(MEDIA_DIR, filename)

# --- API ---
@app.post("/api/speak")
def api_speak():
    """
    Expects multipart/form-data with 'audio' (Blob: audio/webm or similar).
    Returns: { topic, user_text, reply_text, audio_url }
    """
    if "audio" not in request.files:
        return jsonify({"error": "Missing 'audio' file"}), 400

    file_storage = request.files["audio"]
    _ = secure_filename(file_storage.filename or "utterance.webm")  # sanitized (not used further)

    # 1) Speech-to-text
    try:
        user_text = speech_to_text(file_storage).strip()
    except Exception as e:
        return jsonify({"error": f"STT failed: {e}"}), 500

    # 2) Topic (random from data/topics.txt)
    topic = get_random_topic()

    # 3) LLM reply
    try:
        reply_text = generate_response(topic=topic, user_text=user_text)
    except Exception as e:
        return jsonify({"error": f"LLM failed: {e}"}), 500

    # 4) TTS
    audio_url = None
    try:
        tts_bytes = synthesize_tts(reply_text)
        audio_url = _save_bytes_to_media(tts_bytes, ext="mp3")
    except Exception as e:
        # If TTS fails, still return text
        return jsonify({
            "topic": topic,
            "user_text": user_text,
            "reply_text": reply_text,
            "audio_url": None,
            "warning": f"TTS failed: {e}"
        }), 200

    return jsonify({
        "topic": topic,
        "user_text": user_text,
        "reply_text": reply_text,
        "audio_url": audio_url,
    })

# --- Dev server ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
