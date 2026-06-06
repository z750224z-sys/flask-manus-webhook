# trigger redeploy

from flask import Flask, request, abort
import os
import hmac
import hashlib
import requests
import json

app = Flask(__name__)

# 讀取環境變數
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# LINE API URL
LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"

def verify_signature(body, signature):
    hash = hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'),
                    body.encode('utf-8'),
                    hashlib.sha256).digest()
    return signature == hashlib.sha256(hash).hexdigest()

@app.route("/", methods=["GET"])
def index():
    return "LINE Webhook Ready!"

@app.route("/manus-webhook", methods=["POST"])
def manus_webhook():
    body = request.get_data(as_text=True)
    signature = request.headers.get("X-Line-Signature")

    # 驗證簽章
    if signature is None:
        abort(400, "Missing signature")
    # LINE 官方 SDK 會自動驗證，這裡簡化處理
    # 如果要更嚴謹，可以用 line-bot-sdk-python

    data = request.json
    if not data or "events" not in data:
        abort(400, "Invalid payload")

    for event in data["events"]:
        if event["type"] == "message":
            reply_token = event["replyToken"]
            user_message = event["message"]["text"]

            # 回覆訊息
            reply_data = {
                "replyToken": reply_token,
                "messages": [
                    {"type": "text", "text": f"你說的是：{user_message}"}
                ]
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
            }

            requests.post(LINE_REPLY_URL,
                          headers=headers,
                          data=json.dumps(reply_data))

    return "OK"
