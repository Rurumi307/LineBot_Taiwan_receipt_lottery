from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import json

app=Flask(__name__) # __name__代表目前執行的模組

# LINE BOT info
line_bot_api = LineBotApi('sBIB8FLCO7qzl4tQCbbT1MQChyb/uiYCTxySE4rLqholm+kTjgsxXUfFCQkvl/k95dMJLUDo87Afy7u8dS4biwLzezr0Bb6bu2PUdjKie7+aTxmgX5QHUplrn+oHAdOTUNMdspQXJ9AuzA2lRjMfAgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b9f7acc632cb65d50b8af479e73cfc87')

@app.route('/callback', methods=['POST']) # 函式的裝飾(Decorator): 以函式為基礎,提供附加的功能
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=(ImageMessage))
def handle_image_message(event):
    # 使用者傳送的照片
    message_content = line_bot_api.get_message_content(event.message.id)

    # 照片儲存名稱
    fileName = event.message.id + '.jpg'

    # 儲存照片
    with open('./image/' + fileName, 'wb')as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    # linebot回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='收到您上傳的照片囉!'))

# @app.route("/test") # 代表我們要處理的網站路徑
# def test():
#     return "This is test"

if __name__=="__main__": # 如果以主程式執行
    app.run() 

