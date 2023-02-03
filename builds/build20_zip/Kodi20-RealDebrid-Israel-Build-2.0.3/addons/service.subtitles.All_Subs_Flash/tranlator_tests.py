def translate_subs_test(input_file,output_file):
    import requests
    file = open(input_file, 'r')
    text=file.read()

    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'multipart/form-data; boundary=---------------------------987779034590',
        'Host': 'www.syedgakbar.com',
        'Pragma': 'no-cache',
        'Referer': 'http://www.syedgakbar.com/projects/dst',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
        'X-Requested-With': 'XMLHttpRequest',
    }
    head=\
    '''
-----------------------------987779034590
Content-Disposition: form-data; name="file"; filename="test.srt"
Content-Type: application/octet-stream
    '''
    sub=\
    '''
-----------------------------987779034590--
    '''
    data=head+text+sub

    response = requests.post('http://www.syedgakbar.com/projects/subtitles-translate/file-upload', headers=headers, data=data).content

    a=a+1
def translate_subs_free(input_file,output_file):
    import requests
    file = open(input_file, 'r')
    text=file.read()
    headers = {
        'Host': 'www.free-translation.info',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'http://www.free-translation.info/',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
    ax=split_string(text,10000)

    all_txt=''
    for tx in ax:
        data={'action':'btplugin_translate',
        'sl':'en',
        'text':tx,
        'tl':'he'}

        response = requests.post('http://www.free-translation.info/wp-admin/admin-ajax.php', headers=headers,data=data).content
        all_txt=all_txt+response
        
        
    
    file = open(output_file, 'w')

    file.write(all_txt.replace('<br />','\n')) 
    file.close()
def translate_subs_tl2(input_file,output_file):
    import requests
    file = open(input_file, 'r')
    text=file.readlines()
    import requests
    from googletrans import Translator
    translator = Translator()
    token=translator.translate('hellow', dest='he')

    headers = {
        'Referer': 'http://www.syedgakbar.com/projects/dst',
        'Origin': 'http://www.syedgakbar.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }


    params = (
        ('anno', '3'),
        ('client', 'te'),
        ('format', 'html'),
        ('v', '1.0'),
        ('key', ''),
        ('logld', 'vTE_20170911_00'),
        ('sl', 'auto'),
        ('tl', 'iw'),
        ('sp', 'nmt'),
        ('tc', '10'),
        ('sr', '1'),
        ('tk', str(token)),
        ('mode', '1'),
    )

    data = [
      ('q', ' \n(drumroll) '),
      ('q', ' \n(rousing orchestral fanfare playing) '),
      ('q', ' \nAmericasCardroom.com brings poker back\nMillion Dollar Sunday Tournament every Sunday '),
      ('q', ' \n(fanfare ends) '),
      ('q', ' \n(ominous chord plays) '),
      ('q', ' \n(electronic tone pulsing) '),
      ('q', ' \n(electronic whir increasing in volume) '),
      ('q', ' \n(electricity crackles) '),
      ('q', ' \n(electronic snap and buzz) '),
      ('q', ' \n(crackling and whooshing) '),
      ('q', ' \n(low, distant electronic pulsing) '),
      ('q', ' \n(eerie tones playing) '),
      ('q', ' \n(ominous, dramatic theme begins) '),
      ('q', ' \n(deep whooshing) '),
      ('q', ' \n## '),
      ('q', ' \n(thud, squishing) '),
      ('q', ' \n(screeching) '),
      ('q', ' \n(engines whooshing) '),
      ('q', ' \n(slimy slithering) '),
      ('q', ' \n(deep growling) '),
      ('q', ' \n(footsteps passing by,\nlow growling) '),
      ('q', ' \n(gurgling, chittering) '),
      ('q', ' \n(low, guttural croaking) '),
      ('q', ' \n(flame hissing) '),
      ('q', ' \n(scream) '),
      ('q', ' \n(distant snarling) '),
      ('q', ' \nMAN: Okay, now, take your time. '),
      ('q', ' \n(whispering): There you go. '),
      ('q', ' \n(explosion, rumbling) '),
      ('q', ' \nDad! Dad! It&#39;s up here! '),
      ('q', ' \nSlow down, Sam, slow down. '),
      ('q', ' \n(ominous theme plays) '),
      
    ]

    response = requests.post('https://translate.googleapis.com/translate_a/t', headers=headers, params=params, data=data).content


    #NB. Original query string below. It seems impossible to parse and
    #reproduce query strings 100% accurately so the one below is given
    #in case the reproduced version is not "correct".
    # response = requests.post('https://translate.googleapis.com/translate_a/t?anno=3&client=te&format=html&v=1.0&key&logld=vTE_20170911_00&sl=auto&tl=iw&sp=nmt&tc=1&sr=1&tk=671199.804154&mode=1', headers=headers, data=data)


    a=a+1