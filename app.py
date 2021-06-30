from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import json
from model import formrecognizer_by_local,receipt,selectdb


app = Flask(__name__)

secretFile = json.load(open("secretFile.txt",'r'))
channelAccessToken = secretFile['channelAccessToken']
channelSecret = secretFile['channelSecret']

line_bot_api = LineBotApi(channelAccessToken)
handler = WebhookHandler(channelSecret)

@app.route("/callback", methods=['POST'])
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


# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     message_content = line_bot_api.get_message_content(event.message.id)
#     data = selectdb.Mongo_select(int(message_content))
#     ans = receipt(list('12345678'),data)

#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=ans))


#     print(event.message.text) # 接收用戶訊息

if __name__ == "__main__":
    app.run(host='0.0.0.0')