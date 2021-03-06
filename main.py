from flask import Flask, request, abort
import os
import requests
from bs4 import BeautifulSoup

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

pokeka_url = [
    "https://www.pokemoncenter-online.com/?p_cd=4521329313405",
    "https://www.pokemoncenter-online.com/?p_cd=4521329266541"
        ]
card = ["シャイニースターV" , "TAG TEAM GX BOX"]
result_str = ["売り切れ","予約受付中","在庫あるよ"]


@app.route("/")
def hello_world():
    return "hello world!"

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
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    my_header = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; NP06; rv:11.0) like Gecko"
    }
    if "シャイ" in event.message.text:
        i = 0
    if "TAG" in event.message.text:
        i = 1
    

    data = requests.get(pokeka_url[i], headers = my_header)
    data.encoding = data.apparent_encoding
    data = data.text
    soup = BeautifulSoup(data, "html.parser")
    detail = soup.find("table",class_="no_size")
    detailstr = str(detail)
    if "soldout" in detailstr:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=card[i]+result_str[0]))
    elif "yoyaku" in detailstr:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=card[i]+result_str[1]))
    elif "add_cart_btn" in detailstr:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=card[i]+result_str[2]))

            


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
