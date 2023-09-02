from myLogger import myLogger

def get_aa_server(url,it):
    import requests,os,shutil
    import xbmcvfs
    import os
    from service import xbmc_translate_path,__profile__
    MyTmp_aa = xbmc_translate_path(os.path.join(__profile__, 'aa_buff'))

    try:
        shutil.rmtree(MyTmp_aa)
    except: pass
    xbmcvfs.mkdirs(MyTmp_aa)

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',

            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
    x=requests.get(url,headers=headers).content

    if it == 'tv':
        fi_name='aa_tv.txt'
    else:
        fi_name='aa_movie.txt'

    output_file=os.path.join(MyTmp_aa,fi_name)

    file = open(output_file, 'w')

    file.write(str(x))
    file.close()
    return output_file


def aa_subs(item,mode_subtitle,prefix_acat,color_acat):
    import xbmcaddon
    import cache,re
    import base64
    #from ..PTN import PTN
    from service import is_local_file_tvshow

    global links_subcenter

    MyScriptID = xbmcaddon.Addon().getAddonInfo('id')
    base_aa='aHR0cHM6Ly9yb2NrLnNlZWRob3N0LmV1L2tjYXQxMjMvSHViLw=='

    if item["tvshow"] or is_local_file_tvshow(item):
        x_pre=cache.get(get_aa_server,100,base64.b64decode(base_aa).decode('utf-8')+'Series/','tv', table='subs_aa')

        file = open(x_pre, 'r')

        x=file.read()#.decode('utf-8','ignore')
        file.close()

        regex='<td><a href="(.+?)"'

        m=re.compile(regex).findall(x)
        ret = []
        item["season"]=str(item["season"])
        item["episode"]=str(item["episode"])
        if len(item["season"])==1:
            lseason='0'+item["season"]
        else:
            lseason=item["season"]

        if len(item["episode"])==1:
            lepisode='0'+item["episode"]
        else:
            lepisode=item["episode"]
        ep_str=('.s%se%s.'%(lseason,lepisode)).lower()
        ep_str2=('.%sx%s.'%(item["season"],item["episode"])).lower()
        ep_str3=('.%se%s.'%(item["season"],lepisode)).lower()

        #x=1
        subtitles=[]

        for items in m:
            f_item=items.lower().replace(' ','.')

            if (is_local_file_tvshow(item)):
                item["tvshow"] = item["title"]

            if item["tvshow"].replace(' ','.').lower() in f_item and ((ep_str in f_item) or (ep_str2 in f_item) or(ep_str3 in f_item)) :
                nlabel = "Hebrew" #he
                nlabel2 = '[COLOR '+color_acat+']'+items+'[/COLOR]'
                #nlabel2 = '[COLOR '+color_acat+']'+prefix_acat+' ' +items+'[/COLOR]'
                #nlabel2 = '[COLOR '+color_acat+']'+str(x)+'. '+prefix_acat+' ' +items+'[/COLOR]'
                nicon = '[COLOR '+color_acat+']'+prefix_acat+'[/COLOR]'
                nthumb = "he"

                url = "plugin://%s/?action=download&link=%s&id=%s&filename=%s&language=%s&source=%s" % (
                    MyScriptID,base64.b64decode(base_aa).decode('utf-8')+'Series/'+ items, items, items, 'he','aa_subs')
                if mode_subtitle>1:
                    json_data={'url':url,
                                 'label':nlabel,
                                 'label2':nlabel2,
                                 'iconImage':nicon,
                                 'thumbnailImage':nthumb,
                                 'hearing_imp':'false',
                                 'sync': 'false'}
                    subtitles.append(json_data)
                    #x=x+1

    else:
        x_pre=cache.get(get_aa_server,100,base64.b64decode(base_aa).decode('utf-8')+'Movies/','movie', table='subs_aa')

        file = open(x_pre, 'r')

        x=file.read()#.decode('utf-8','ignore')
        file.close()


        regex='<td><a href="(.+?)"'

        m=re.compile(regex).findall(x)
        ret = []

        #x=1
        subtitles=[]
        subtitle=" "

        for items in m:
            f_item=items.lower().replace(' ','.').lower()

            if item["title"].replace(' ','.').lower() in f_item.lower() and str(item['year']) in f_item :
                nlabel = "Hebrew" #he
                nlabel2 = '[COLOR '+color_acat+']'+items+'[/COLOR]'
                #nlabel2 = '[COLOR '+color_acat+']'+prefix_acat+' ' +items+'[/COLOR]'
                #nlabel2 = '[COLOR '+color_acat+']'+str(x)+'. '+prefix_acat+' ' +items+'[/COLOR]'
                nicon = '[COLOR '+color_acat+']'+prefix_acat+'[/COLOR]'
                nthumb = "he"
                url = "plugin://%s/?action=download&link=%s&id=%s&filename=%s&language=%s&source=%s" % (
                    MyScriptID,base64.b64decode(base_aa).decode('utf-8')+'Movies/'+ items, items, items, 'he','aa_subs')

                if mode_subtitle>1:
                    json_data={'url':url,
                                 'label':nlabel,
                                 'label2':nlabel2,
                                 'iconImage':nicon,
                                 'thumbnailImage':nthumb,
                                 'hearing_imp':'false',
                                 'sync': 'false'}
                    subtitles.append(json_data)
                    #x=x+1

    return subtitles,m

def Download_aa(url,mode_subtitle):
    import requests
    import xbmcvfs,shutil,cgi
    from os import path
    from service import MyTmp,unquote_plus,KODI_VERSION

    myLogger('Download aa')
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)

    subtitle_list=[]
    archive_file = path.join(MyTmp, 'aa_sub.srt')

    f_url=unquote_plus(url).strip()
    myLogger('f_url:'+f_url)
    headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Authorization': 'Basic YWFhOmFhYQ==',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'utf-8',
    'Accept-Language': 'en-US,en;q=0.9',
    }
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    #'Referer': 'http://185.165.240.137:8080/SUB/',
    'Upgrade-Insecure-Requests': '1',
    'Accept-Encoding': 'utf-8',
    }

    r=requests.get(f_url,headers=headers,stream=True)
    params = cgi.parse_header(r.headers.get('content-type'))[0]
    server_encoding = ('charset' in params) and params['charset'].strip("'\"") or None
    r.encoding = server_encoding or r.apparent_encoding
    text = r.text

    #file = open(archive_file, 'w')
    if KODI_VERSION>18:
        with open(archive_file, mode="w", encoding="utf8") as f:
             f.write(text)
    else:
        with open(archive_file, mode="w") as f:
             f.write(text)
    #file.write(text)
    #file.close()
    #urlretrieve(z, archive_file)
    subtitle_list.append(archive_file)
    if mode_subtitle>1:
      return subtitle_list
    else:
     #xbmc.Player().setSubtitles(subtitle_list[0])

     if len (subtitle_list)>0:
       sub_result=subtitle_list[0]
     else:
       sub_result='0'
     return sub_result