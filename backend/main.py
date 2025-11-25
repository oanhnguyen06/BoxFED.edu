from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dữ liệu ngành học
with open("data/majors.txt", "r", encoding="utf-8") as f:
    KNOWLEDGE = f.read()


OLLAMA_URL = "http://localhost:11434/api/generate"   # Ollama mặc định

@app.post("/chat")
async def chat(message: dict):
    user_input = message["msg"]

    prompt = f"""
Bạn là chatbot tư vấn ngành học.
Dưới đây là dữ liệu ngành học:

{KNOWLEDGE}

Người dùng hỏi: {user_input}
Trả lời dựa trên dữ liệu trên.
"""

    payload = {
        "model": "llama3.2",   # model bạn đang chạy trong Ollama
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    result = response.json()

    return {"reply": result["response"]}
