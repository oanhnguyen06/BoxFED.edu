
import os
import re
import json
import pandas as pd 
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from docx import Document
import requests
from dotenv import load_dotenv
from werkzeug.utils import secure_filename 

load_dotenv() # optional .env

# --- Config ---
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2:9b") 
DATA_DIR = Path(__file__).parent / "data"
UPLOAD_DIR = Path(__file__).parent / "uploads"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# Cấu hình đường dẫn file CSV của giảng viên
CSV_FILENAME = "Book 4.xlsx - Sheet1.csv"
LECTURERS_CSV_PATH = Path(__file__).parent / CSV_FILENAME 

app = Flask(__name__, static_folder="../web", static_url_path="/")
CORS(app)

# ====================================================================
# --- Helpers (Giữ nguyên các hàm RAG cũ) ---
# ====================================================================
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
    api_key = os.getenv("OLLAMA_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return json.dumps(data, ensure_ascii=False)

# ====================================================================
# --- NEW: Hàm xử lý dữ liệu CSV cho Giảng viên ---
# ====================================================================

def remove_vietnamese_accent_and_normalize(text):
    """Chuẩn hóa chuỗi, loại bỏ dấu tiếng Việt và ký tự đặc biệt."""
    text = text.lower()
    text = text.replace('đ', 'd')
    text = re.sub(r'[^\w\s]', '', text) # Loại bỏ ký tự đặc biệt
    # Loại bỏ dấu
    text = text.normalize('NFD').encode('ascii', 'ignore').decode('utf-8')
    return text

def process_csv_data():
    """
    Đọc CSV, ánh xạ tên cột tiếng Việt sang key tiếng Anh trong JS và 
    chuyển các trường phức tạp thành list.
    """
    if not LECTURERS_CSV_PATH.exists():
        print(f"Lỗi: Không tìm thấy file CSV tại {LECTURERS_CSV_PATH}")
        return []
    
    try:
        df = pd.read_csv(LECTURERS_CSV_PATH, encoding='utf-8')
        
        # Ánh xạ tên cột từ file CSV bạn gửi sang key JavaScript mong muốn
        column_map = {
            'Họ tên': 'name',
            'Chức danh': 'title',
            'Đơn vị': 'dept',
            'Email': 'email',
            'Điện thoại': 'phone',
            'Đào tạo': 'train', 
            'Nghiên cứu': 'work', 
            'Lĩnh vực nghiên cứu': 'area',
            # Các cột khác sẽ bị loại bỏ nếu không được mapping
        }
        df.rename(columns=column_map, inplace=True)
        
        # Lọc chỉ giữ lại các cột đã được mapping và đảm bảo thứ tự
        required_cols = list(column_map.values())
        df = df[[col for col in required_cols if col in df.columns]]
        
        # Thêm cột 'key' và 'img'
        def generate_key_and_img(name):
            # Tạo key từ tên (ví dụ: PGS.TS. Lê Hiếu Học -> le_hieu_hoc)
            name_norm = remove_vietnamese_accent_and_normalize(name)
            # Loại bỏ chức danh và khoảng trắng dư thừa
            name_clean = re.sub(r'(pgs\.ts\.|ts\.|ths\.|cn\.)', '', name_norm).strip()
            key = '_'.join(name_clean.split())
            img = f"img/{key}.jpg"
            return key, img
        
        # Gán giá trị cho key và img
        df[['key', 'img']] = df['name'].apply(
            lambda x: pd.Series(generate_key_and_img(x))
        )
        
        # Các cột cần chuyển từ Chuỗi (String) thành Danh sách (List)
        list_columns = ['train', 'work', 'area'] 
        
        for col in list_columns:
            if col in df.columns:
                # Dùng dấu xuống dòng ('\n') làm ký tự phân tách
                df[col] = df[col].astype(str).str.split('\n').apply(
                    lambda x: [
                        # Loại bỏ ký tự gạch đầu dòng (•, ·, -) và khoảng trắng thừa
                        item.strip().lstrip('•\t·- ') 
                        for item in x if item.strip() and item.strip() != 'nan'
                    ]
                )

        # Chuyển DataFrame thành List of Dictionaries
        return df.to_dict(orient='records')

    except Exception as e:
        print(f"Lỗi khi xử lý file CSV: {e}")
        return []


# ====================================================================
# --- Routes (Endpoints API) ---
# ====================================================================

# --- NEW: Endpoint Giảng viên CSV ---
@app.route('/api/lecturers', methods=['GET'])
def get_lecturers_api():
    """Endpoint API phục vụ dữ liệu giảng viên đã xử lý từ CSV."""
    lecturers_data = process_csv_data()
    if not lecturers_data:
        return jsonify({"error": "Không thể tải hoặc xử lý dữ liệu giảng viên"}), 500
        
    return jsonify({"lecturers": lecturers_data}), 200

# --- Giữ nguyên các Routes cũ ---
@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Upload file .docx, lưu vào data/
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
      "file": "CNTT.docx"    # optional: filename
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
