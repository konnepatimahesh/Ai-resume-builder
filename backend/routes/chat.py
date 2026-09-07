from flask import Blueprint, request, jsonify
from utils.decorators import login_required_api
from groq import Groq
import os
import re

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
@login_required_api
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    system = data.get("system", "You are a helpful AI career assistant.")
    if not messages:
        return jsonify({"error": "No messages provided."}), 400
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=1024,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
        return jsonify({"reply": reply}), 200
    except Exception as e:
        print(f"[CHAT ERROR] {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500