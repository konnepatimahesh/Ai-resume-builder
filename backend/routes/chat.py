from flask import Blueprint, request, jsonify
from utils.decorators import login_required_api
from groq import Groq
import os
import re

chat_bp = Blueprint("chat", __name__)

# Groq models in priority order — verified available on this account
_CHAT_MODELS = [
    "qwen/qwen3.8-27b",
    "qwen/qwen3.6-27b",
    "openai/gpt-oss-120b",
]

@chat_bp.route("/chat", methods=["POST"])
@login_required_api
def chat():
    data     = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    system   = data.get("system", (
        "You are an expert AI career coach and resume consultant. "
        "Help users improve their resumes, prepare for interviews, and advance their careers. "
        "Give specific, actionable advice. Be encouraging but honest."
    ))

    if not messages:
        return jsonify({"error": "No messages provided."}), 400

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "AI service not configured. Please contact support."}), 500

    client = Groq(api_key=api_key)
    full_messages = [{"role": "system", "content": system}] + messages

    last_error = None
    for model in _CHAT_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=full_messages,
                max_tokens=1024,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            # Strip any thinking tags that some models emit
            reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
            return jsonify({"reply": reply}), 200
        except Exception as e:
            last_error = e
            print(f"[CHAT] Model {model} failed: {type(e).__name__}: {e}")
            continue

    print(f"[CHAT ERROR] All models failed. Last: {last_error}")
    return jsonify({"error": "AI service temporarily unavailable. Please try again."}), 500