import requests,json
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

def crawl(search_str):
    proxies = {
      'http': 'http://proxy.ncu.edu.tw/:3128'
    }
    headers = {'Content-Type': 'application/json',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
           'Referer': 'https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=123&newsearch=true'
              } 
    payload = {"queryText":search_str,"newsearch":"true"}
    r = requests.post('https://ieeexplore.ieee.org/rest/search', headers=headers, json=payload, proxies = proxies)
    #print(r.json())
    json_data = r.text
    dict = json.loads(json_data)
    #print(json.loads(json_data))
    ls = ""
    for i in range(10):           #列出十筆資料
        ls+="{}: {}\n\thttps://ieeexplore.ieee.org{}\n".format(i+1,dict['records'][i]['articleTitle'],dict['records'][i]['pdfLink'])
    return ls

app = Flask(__name__)

line_bot_api = LineBotApi('ZzRhxzX1H3hsEagEXhqqDBiO73fSOixUgTJXE2SoVdmzvyhnnyNLLkBoPp4oU65xxEbZzbD/iVNF7KnAJpKlsTQrd30qKVQoWQ8PezDaE8HMd7rhCFC50iqEAIF9/GhfzAb12Q48AqeMw0Z0nqhe+QdB04t89/1O/w1cDnyilFU=')
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
    if event.message.text.split()[0]!='s':
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='歡迎使用找論文!\n請輸入s+" 關鍵字(ex: s paper)"'))
    if event.message.text.split()[0] == "s":
        str_list = crawl(event.message.text.split()[1])
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=str_list))
        


if __name__ == "__main__":
    app.run()
