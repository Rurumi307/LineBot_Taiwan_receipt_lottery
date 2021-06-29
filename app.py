from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,ImageMessage)
import json
# import formrecognizer_by_local 

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
            
    # local_image_path = './image/' + fileName       
    # formrecognizer = formrecognizer_by_local(local_image_path)
    # linebot回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage('收到您上傳的照片囉!'))
        
if __name__ == "__main__":
    app.run(host='0.0.0.0')