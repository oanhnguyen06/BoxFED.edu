# backend/app.py
import os
import re
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from docx import Document
import requests
from dotenv import load_dotenv

load_dotenv()  # optional .env

# --- Config ---
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2:9b")  # thay theo model của bạn
DATA_DIR = Path(__file__).parent / "data"
UPLOAD_DIR = Path(__file__).parent / "uploads"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder="../web", static_url_path="/")
CORS(app)

# --- Helpers ---
def docx_to_text(filepath: Path) -> str:
    """Trích toàn bộ text từ file .docx"""
    doc = Document(filepath)
    paragraphs = []
    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)

def find_relevant_snippets(full_text: str, keywords: list, max_chars=3000) -> str:
    """
    Lấy các đoạn chứa keyword. Trả về chuỗi nối các đoạn quan trọng,
    giới hạn tổng độ dài bằng max_chars.
    """
    text = full_text
    # split thành đoạn (break by newline)
    parts = [p.strip() for p in re.split(r'\n{1,}', text) if p.strip()]
    matched = []
    for p in parts:
        lower = p.lower()
        if any(k.lower() in lower for k in keywords):
            matched.append(p)
    # nếu không tìm thấy, fallback: tìm đoạn chứa keyword từng từ
    if not matched:
        for k in keywords:
            for p in parts:
                if k.lower() in p.lower():
                    matched.append(p)
    # Join and trim
    joined = "\n\n".join(matched)
    if len(joined) > max_chars:
        return joined[:max_chars] + "...\n\n[TRIMMED]"
    return joined or (full_text[:max_chars] + ("...\n\n[TRIMMED]" if len(full_text)>max_chars else ""))

def call_ollama_chat(prompt: str, model=OLLAMA_MODEL, max_tokens=512):
    """
    Gọi Ollama chat completion via HTTP API (compatible with OpenAI-like shape).
    Điều chỉnh theo API của Ollama (local).
    """
    url = f"{OLLAMA_BASE}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an assistant that answers questions based only on the provided context. If the answer is not in the context, say you don't know and suggest where to find it."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0
    }
    headers = {"Content-Type": "application/json"}
    # If your Ollama requires an API key header, add it via environment var OLLAMA_API_KEY
    api_key = os.getenv("OLLAMA_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # adjust depending on returned JSON structure
    # Expect something like: {'choices': [{'message': {'content': '...'}}], ...}
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        # fallback: return raw
        return json.dumps(data, ensure_ascii=False)

# --- Routes ---
@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Upload file .docx, lưu vào data/
    form-data: file
    """
    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "no selected file"}), 400
    # basic validation
    if not f.filename.lower().endswith(".docx"):
        return jsonify({"error": "only .docx allowed"}), 400
    save_path = DATA_DIR / f.filename
    f.save(save_path)
    return jsonify({"ok": True, "filename": f.filename})

@app.route("/files", methods=["GET"])
def list_files():
    files = [p.name for p in DATA_DIR.glob("*.docx")]
    return jsonify({"files": files})

@app.route("/chat", methods=["POST"])
def chat():
    """
    Body JSON:
    {
      "message": "Hỏi gì đó",
      "major": "CNTT",      # optional: tên ngành hoặc keyword
      "file": "CNTT.docx"   # optional: filename
    }
    """
    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "empty message"}), 400

    major = (data.get("major") or "").strip()
    filename = (data.get("file") or "").strip()

    # choose file: priority: explicit filename -> auto pick by major -> fallback first file
    chosen_path = None
    if filename:
        p = DATA_DIR / filename
        if p.exists():
            chosen_path = p
    if not chosen_path and major:
        # try to find file whose name contains major (case-insensitive)
        candidates = [p for p in DATA_DIR.glob("*.docx") if major.lower() in p.name.lower()]
        if candidates:
            chosen_path = candidates[0]
    if not chosen_path:
        # fallback: first docx
        candidates = list(DATA_DIR.glob("*.docx"))
        if candidates:
            chosen_path = candidates[0]

    if not chosen_path:
        return jsonify({"error": "no data file found on server. Upload first."}), 404

    full_text = docx_to_text(chosen_path)

    # build keywords: include major and split words
    keywords = [major] if major else []
    keywords += [w for w in re.split(r'[\s,;:/\-]+', major) if w] if major else []
    # ensure some default keywords: try filename base
    keywords.append(chosen_path.stem)

    # extract relevant snippets
    context_snippet = find_relevant_snippets(full_text, [k for k in keywords if k])

    # Compose prompt
    prompt = f"""
Bạn được cung cấp phần thông tin sau (context) trích từ file: {chosen_path.name}

CONTEXT:
{context_snippet}

Yêu cầu: Dựa trên CONTEXT ở trên, trả lời câu hỏi sau một cách ngắn gọn, rõ ràng và chính xác. Nếu thông tin không có trong CONTEXT thì hãy thành thực nói "Không có trong tài liệu" và gợi ý nơi tìm thông tin.

Câu hỏi: {message}
"""

    try:
        reply = call_ollama_chat(prompt)
    except requests.HTTPError as e:
        return jsonify({"error": "ollama error", "detail": str(e), "resp": e.response.text}), 500
    except Exception as e:
        return jsonify({"error": "internal error", "detail": str(e)}), 500

    return jsonify({"reply": reply, "file_used": chosen_path.name})

# route to serve frontend (optional)
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
