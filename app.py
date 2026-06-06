from flask import Flask, request, abort
import os
import json

app = Flask(__name__)

# 讀取環境變數
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
CLAUDE_KEY = os.getenv("CLAUDE_API_KEY")
NIM_KEY = os.getenv("NIM_API_KEY")
MANUS_KEY = os.getenv("MANUS_API_KEY")

@app.route("/", methods=["GET"])
def index():
    return "Hello, Flask Webhook!"

@app.route("/manus-webhook", methods=["POST"])
def manus_webhook():
    try:
        data = request.json
        if not data:
            abort(400, "No JSON payload received")

        # 這裡可以放 LINE Bot 或 AI API 的邏輯
        # 目前先回傳測試用的 JSON
        response = {
            "status": "ok",
            "received": data,
            "LINE_TOKEN": bool(LINE_TOKEN),
            "GEMINI_KEY": bool(GEMINI_KEY),
            "CLAUDE_KEY": bool(CLAUDE_KEY),
            "NIM_KEY": bool(NIM_KEY),
            "MANUS_KEY": bool(MANUS_KEY)
        }
        return json.dumps(response, ensure_ascii=False), 200, {"Content-Type": "application/json"}

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False), 500, {"Content-Type": "application/json"}
