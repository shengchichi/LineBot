import requests,json
from flask import Flask, request, abort


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

paper_dict ={}
def crawl(search_str):
    proxies = {
      'http': 'http://proxy.ncu.edu.tw/:3128'
    }
    page = 1
    headers = {'Content-Type': 'application/json',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
           'Referer': 'https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=123&newsearch=true'
              } 
    start = 0
    while page < 3:#先爬個50筆
        payload = {"queryText":search_str,"newsearch":"true",'pageNumber':str(page)}
        r = requests.post('https://ieeexplore.ieee.org/rest/search', headers=headers, json=payload, proxies = proxies)
    
        json_data = r.text
        dict = json.loads(json_data)
    
        for i in range(25):           #列出十筆資料
            #ls+="{}: {}\n".format(i+1+start,dict['records'][i]['articleTitle'])
            paper_dict[i+1+start] = {'document_url' : 'https://ieeexplore.ieee.org'+dict['records'][i]['documentLink']+"\n",
                                     'title' : dict['records'][i]['articleTitle']}
        page+=1
        start+=25
    

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
    
    
    
    if event.message.text == "開始":
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='歡迎使用找論文!\n請輸入s+" 關鍵字"\nEx:s paper'))
    
    if event.message.text == "關於我":
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='不告訴你哩!'))
        
    if event.message.text.split()[0] == "s":
        
        crawl(event.message.text.split()[1:])
        str_list = ""
        for i in range(10):
            index = str(i+1)+': '
            str_list += index
            str_list += paper_dict[i+1]['title']
            str_list += '\n'
            str_list += paper_dict[i+1]['document_url']
            str_list += '\n'
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='輸入next "數字"顯示更多喔!\nEx:next 10\n\n'+str_list))
    '''    
    elif event.message.text.split()[0] == 'next':
        str_list = ""
        add = int(event.message.text.split()[1])
        if not paper_dict:
            str_list += '"請使用 s+" 關鍵字"'
        else:
            for i in range(add):
                index = str(i+1+add)+': '
                str_list += index
                str_list += paper_dict[i+1+add]['title']
                str_list += '\n'
                str_list += paper_dict[i+1+add]['document_url']
                str_list += '\n'
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="更多\n\n"+str_list))
    '''    
    buttons_template = TemplateSendMessage(
        alt_text='請使用手機版喔!',
        template=ButtonsTemplate(
            title='歡迎使用找論文',
            text='還有一些bug請見諒',
            thumbnail_image_url='https://commons.wikimedia.org/wiki/File:Ieee_blue.jpg',
            actions=[
                MessageTemplateAction(
                    label='開始',
                    text='開始'
                ),
                 MessageTemplateAction(
                    label='關於我',
                    text='關於我'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, buttons_template)
    


if __name__ == "__main__":
    app.run()
