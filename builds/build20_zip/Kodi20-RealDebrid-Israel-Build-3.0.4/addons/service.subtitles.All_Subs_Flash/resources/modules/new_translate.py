
from resources.modules import srt
from resources.modules import log

def translate_text(all_text):
    import requests
    headers = {
        "Referer": "http://translate.google.{}/".format('cn'),
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/47.0.2526.106 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    data = []
    for items in all_text:
        data.append(('q',str(all_text[items])))
    url_base = "https://translate.googleapis.com/translate_a/t"
   
    response = requests.Request(method='POST',
                                 url=url_base,
                                 data=data,
                                 headers=headers,
                                )
    with requests.Session() as s:
            
            r = s.send(request=response.prepare(),
                       verify=False,
                       timeout=10)
    log.warning(r.content)
def translate_now(txt):
    fixed_sub=srt.parse(txt)
    all_text={}
    count=0
    for items in fixed_sub:
        
        all_text[items.index]=items.content
        count+=1
        if (count>29):
            translate_text(all_text)
            a+=1
    log.warning(all_text)