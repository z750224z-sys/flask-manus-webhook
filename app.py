from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os, requests

app = Flask(__name__)

# LINE API
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 首頁測試路由
@app.route("/")
def home():
    return "LINE Bot Webhook is running!"

# Webhook 路由
@app.route("/manus-webhook", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 當收到文字訊息時，呼叫四個 AI 引擎
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    # Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_reply = ""
    if gemini_key:
        try:
            gemini_resp = requests.post(
                "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
                headers={"Authorization": f"Bearer {gemini_key}"},
                json={"contents":[{"parts":[{"text":user_text}]}]}
            ).json()
            gemini_reply = gemini_resp.get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","")
        except Exception as e:
            gemini_reply = f"Gemini error: {e}"

    # Claude
    claude_key = os.getenv("CLAUDE_API_KEY")
    claude_reply = ""
    if claude_key:
        try:
            claude_resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": claude_key, "anthropic-version":"2023-06-01"},
                json={"model":"claude-3-sonnet-20240229","messages":[{"role":"user","content":user_text}]}
            ).json()
            claude_reply = claude_resp.get("content",[{}])[0].get("text","")
        except Exception as e:
            claude_reply = f"Claude error: {e}"

    # NVIDIA NIM
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    nvidia_reply = ""
    if nvidia_key:
        try:
            nvidia_resp = requests.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {nvidia_key}"},
                json={"model":"meta/llama-3.1-70b-instruct","messages":[{"role":"user","content":user_text}]}
            ).json()
            nvidia_reply = nvidia_resp.get("choices",[{}])[0].get("message",{}).get("content","")
        except Exception as e:
            nvidia_reply = f"NVIDIA error: {e}"

    # Manus
    manus_key = os.getenv("MANUS_API_KEY")
    manus_reply = ""
    if manus_key:
        try:
            manus_resp = requests.post(
                "https://api.manus.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {manus_key}"},
                json={"model":"manus-1.6","messages":[{"role":"user","content":user_text}]}
            ).json()
            manus_reply = manus_resp.get("choices",[{}])[0].get("message",{}).get("content","")
        except Exception as e:
            manus_reply = f"Manus error: {e}"

    # 整合回覆
    final_reply = f"Gemini: {gemini_reply}\nClaude: {claude_reply}\nNVIDIA: {nvidia_reply}\nManus: {manus_reply}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=final_reply[:2000]) # LINE 限制 2000 字
    )

# 測試環境變數是否讀到
@app.route("/check-env")
def check_env():
    return {
        "LINE_CHANNEL_ACCESS_TOKEN": bool(os.getenv("LINE_CHANNEL_ACCESS_TOKEN")),
        "LINE_CHANNEL_SECRET": bool(os.getenv("LINE_CHANNEL_SECRET")),
        "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY")),
        "CLAUDE_API_KEY": bool(os.getenv("CLAUDE_API_KEY")),
        "NVIDIA_API_KEY": bool(os.getenv("NVIDIA_API_KEY")),
        "MANUS_API_KEY": bool(os.getenv("MANUS_API_KEY"))
    }
