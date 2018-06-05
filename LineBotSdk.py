import requests,json,re
from flask import Flask, request, abort


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

paper_dict ={}
def crawl(payload):
    proxies = {
      'http': 'http://proxy.ncu.edu.tw/:3128'
   
    }
    headers = {'Content-Type': 'application/json',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
           'Referer': 'https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=123&newsearch=true'
              } 
    
    
    r = requests.post('https://ieeexplore.ieee.org/rest/search', headers=headers, json=payload)
    json_data = r.text

    dict = json.loads(json_data)
    
    for i in range(25):           #列出十筆資料
        #ls+="{}: {}\n".format(i+1+start,dict['records'][i]['articleTitle'])
        paper_dict[i+1] = {'document_url' : 'https://ieeexplore.ieee.org'+dict['records'][i]['documentLink']+"\n",
                                    'title' : dict['records'][i]['articleTitle']}
def check_attr(key_str):
    attr={}
    kwd_idx = 0
    pat = '\d{4}'#find years
    #string = "s 1999-2018"
    match = re.findall(pat,key_str)
    if match:
        str_fmt = "start_end_Year"
        str_fmt = str_fmt.replace('start',match[0])
        str_fmt = str_fmt.replace('end',match[1])
        attr['ranges'] = list(str_fmt)#payload要求
        kwd_idx+=1    
    pat = '[!&|]\w+'#find exclusive words
    match = re.findall(pat,a)
    if match:
        attr['matchBoolean'] = "true"
        exp = ""#expression for payload
        for _ in range(len(match)+1):
            exp+='('
        exp += '"Document Title":search_text)'
        for token in match:
            if token[0]=='!':
                exp += ' NOT "Document Title":{})'.format(token[1:])
            elif token[0]=='&':
                exp += ' AND "Document Title":{})'.format(token[1:])
            elif token[0]=='|':
                exp += ' OR "Document Title":{})'.format(token[1:])
            kwd_idx+=1    
        search_text = " ".join(key_str.split()[kwd_idx:])
        exp = exp.replace('search_text',search_text)
        attr['queryText'] = exp
    else:
        attr['queryText'] = " ".join(key_str.split()[kwd_idx:])
    return attr
    
    
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
        attr ={}
        key_word = " "
        key_word= key_word.join(event.message.text.split()[1:])#list to string
        attr = check_attr(key_word)
        crawl(attr)
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
        TextSendMessage(text=str_list+"end of search"))
   
            
    buttons_template = TemplateSendMessage(
        alt_text='請使用手機版喔!',
        template=ButtonsTemplate(
            title='歡迎使用找論文',
            text='還有一些bug請見諒',
            thumbnail_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Ieee_blue.jpg/320px-Ieee_blue.jpg',
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
