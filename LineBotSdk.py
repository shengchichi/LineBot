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

app = Flask(__name__)

line_bot_api = LineBotApi('ZzRhxzX1H3hsEagEXhqqDBiO73fSOixUgTJXE2SoVdmzvyhnnyNLLkBoPp4oU65xxEbZzbD/iVNF7KnAJpKlsTQrd30qKVQoWQ8PezDaE8HMd7rhCFC50iqEAIF9/GhfzAb12Q48AqeMw0Z0nqhe+QdB04t89/1O/w1cDnyilFU=
')
handler = WebhookHandler('cf5c0712f8bf8a4b7413a066d9dc9a9f')


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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()
