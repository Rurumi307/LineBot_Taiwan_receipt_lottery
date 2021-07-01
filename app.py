from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import json
from model import formrecognizer_by_url,receipt,selectdb
from datetime import datetime
import pyimgur

app = Flask(__name__)

# LINE BOT info
secretFile = json.load(open("secretFile.txt",'r'))
channelAccessToken = secretFile['channelAccessToken']
channelSecret = secretFile['channelSecret']

line_bot_api = LineBotApi(channelAccessToken)
handler = WebhookHandler(channelSecret)

@app.route("/callback", methods=['POST'])
def callback():
    # signature:LINE官方提供用來檢查該訊息是否透過LINE官方APP傳送
    signature = request.headers['X-Line-Signature']
    # 用戶傳送的訊息，並且是以JSON的格式傳送
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# Message event
@handler.add(MessageEvent)
def handle_message(event):
    # 接收訊息
    message_type = event.message.type
    user_id = event.source.user_id

    if message_type=='image':
        message_id = event.message.id
        message_content = line_bot_api.get_message_content(message_id)
        fileName = message_id + '.jpg'
        with open('./image/' + fileName, 'wb')as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
        #上傳圖片   

        CLIENT_ID = secretFile['Client_ID']
        PATH = './image/' + fileName #A Filepath to an image on your computer"

        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(PATH, title="Uploaded with PyImgur")
        image_url = uploaded_image.link
        number_id = formrecognizer_by_url.formrecognizer_by_url(image_url) 
        invoice_date = number_id['日期']       
        invoice_number = number_id['發票號碼']  
        receipt_data = selectdb.Mongo_select(int(invoice_date))
        ans = receipt.receipt_mechine([invoice_number],receipt_data)

        # 回傳訊息的方法
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=ans[0][2]))
    elif message_type== 'text':
        message = event.message.text
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "error"))
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     message_content = line_bot_api.get_message_content(event.message.id)
#     data = selectdb.Mongo_select(int(message_content))
#     ans = receipt(list('12345678'),data)

#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=ans))

# if __name__ == "__main__":
#     app.run(host='0.0.0.0')