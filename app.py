from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 從環境變數讀取 LINE API 金鑰
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/manus-webhook", methods=['POST'])
def callback():
    # 取得 X-Line-Signature header
    signature = request.headers['X-Line-Signature']

    # 取得 request body
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 當收到文字訊息時，回覆 Hello World
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Hello World")
    )

# 測試環境變數是否讀到
@app.route("/check-env")
def check_env():
    return {
        "LINE_CHANNEL_ACCESS_TOKEN": bool(os.getenv("LINE_CHANNEL_ACCESS_TOKEN")),
        "LINE_CHANNEL_SECRET": bool(os.getenv("LINE_CHANNEL_SECRET"))
    }
