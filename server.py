from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

app = Flask(__name__)
CORS(app)

@app.post("/chat")
def chat():
    data = request.json
    msg = data["message"]

    response = client.chat.completions.create(
        model="gemma2:9b",
        messages=[{"role": "user", "content": msg}]
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

app.run(port=3000)
