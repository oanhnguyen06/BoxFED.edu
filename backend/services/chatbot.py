# backend/services/chatbot.py
import os
import requests
from typing import List
from docx import Document

OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "gemma2:9b")  # chỉnh nếu cần

def read_docx(path: str) -> str:
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n".join(paragraphs)

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".docx"]:
        return read_docx(path)
    else:
        return read_text(path)

def load_documents(base_dir: str, filenames: List[str]) -> str:
    """Load multiple files and concat, with small separators. Truncate if too long."""
    parts = []
    for fn in filenames:
        p = os.path.join(base_dir, fn)
        if not os.path.exists(p):
            parts.append(f"[FILE NOT FOUND: {fn}]")
            continue
        try:
            text = load_file(p)
            # put filename header to help the model understand context
            header = f"--- BEGIN FILE: {fn} ---\n"
            footer = f"\n--- END FILE: {fn} ---\n"
            parts.append(header + text + footer)
        except Exception as e:
            parts.append(f"[ERROR READING {fn}: {e}]")
    full = "\n\n".join(parts)
      # Simple protection: cap length (characters) to avoid huge prompts
    MAX_CHARS = 60_000
    if len(full) > MAX_CHARS:
        full = full[:MAX_CHARS] + "\n\n...[TRUNCATED FOR LENGTH]..."

    return full
 
