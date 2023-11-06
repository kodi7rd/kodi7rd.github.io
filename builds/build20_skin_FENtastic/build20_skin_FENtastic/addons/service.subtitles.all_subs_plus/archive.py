#///////////////////////////////////////local archive////////////////////////////////////////////////
'''
    info2=(PTN.parse(item['file_original_path'])) #video filename without the extension
    myLogger("LOCAL: item['file_original_path'] - " + repr(item['file_original_path']))
    myLogger("LOCAL: info2 - " + repr(info2))
    title_compare_file = title_ready(info2['title'])

    info3=(PTN.parse(xbmc.getInfoLabel("VideoPlayer.title"))) #video filename with the extension
    myLogger("LOCAL: VideoPlayer.title - " + repr(xbmc.getInfoLabel("VideoPlayer.title")))
    myLogger("LOCAL: info3 - " + repr(info3))
    title_compare_player = title_ready(info3['title'])
    season_compare_player = info3['season'] if 'season' in info3 else -1
    episode_compare_player = info3['episode'] if 'episode' in info3 else -1
'''
#///////////////////////////////////////yifi archive////////////////////////////////////////////////
#from yify_api.yify import search_yify

    #if all_setting["yify"]== 'true':# YIFY Search
        #num_of_subs,subtitle,saved_data=search_yify(item,imdb_id,mode_subtitle)

        '''
            elif 'yify$$$' in id:
                archive_file = path.join(MyZipFolder, 'yify.sub.'+id.replace('yify$$$','').replace('/subtitles/','')+'.zip')

                if not path.exists(archive_file):
                    urlretrieve("https://www.yifysubtitles.org/subtitle/"+id.replace('yify$$$','').replace('/subtitles/','')+".zip", archive_file)
        '''

#///////////////////////////////////////Subcenter archive////////////////////////////////////////////////
        '''
		<!-- <setting id="aa_subs" label="aa_subs [COLOR blue](http://aa_subs.com/)[/COLOR]" type="bool" default="false" />
		<setting type="action" label="אפס AA קאש" action="RunScript(service.subtitles.all_subs_plus, 1,action=clear_aa)" option="close" visible="true"/>
        <setting id="subscenter" label="Subscenter [COLOR blue](http://www.subscenter.org)[/COLOR]" type="bool" default="true" visible="false"/> -->

        <setting id="color_result_aa_subs" label="aa_subs" type="labelenum" values="custom|bisque|lightskyblue|yellow|limegreen|white|thistle|cyan|" default="thistle" visible= "eq(-11,true)" enable="eq(-11,true)"/>
        <setting id="color_result_aa_subs_custom" type="text" default="" visible= "eq(-12,true) + eq(-1,0)" enable="eq(-12,true) + eq(-1,0)" />
        '''

#from aa_subs_api.aa_subs import aa_subs, Download_aa

                    #  "color_result_aa_subs":MyAddon.getSetting("color_result_aa_subs"),
                    #  "color_result_aa_subs_custom":MyAddon.getSetting("color_result_aa_subs_custom"),
                    #  "Email":MyAddon.getSetting("Email"),
                    #  "Password":MyAddon.getSetting("Password"),

    # all_setting["aa_subs"]='false'
    # all_setting["yify"]='false'
    # "aa_subs":MyAddon.getSetting("aa_subs"),
    # "yify":MyAddon.getSetting("yify"),

    # cCustomAcat = all_setting["color_result_aa_subs_custom"]
    # cAcat = all_setting["color_result_aa_subs"]
    # color_acat = cCustomAcat if cAcat == custom else cAcat

'''
def aa_subs_Search(item,mode_subtitle):
    global links_subcenter

    myLogger("ACat_Search item:" + repr(item))

    subtitle_list,result = aa_subs(item,mode_subtitle,prefix_acat,color_acat)

    links_subcenter = subtitle_list

    return len(result),links_subcenter
'''

'''
if all_setting["aa_subs"]== 'true':# Subcenter Search
    threads.append(Thread(aa_subs_Search,item,mode_subtitle))
    #num_of_subs,subtitle,saved_data=subcenter_search(item,mode_subtitle)

'''

        #   if all_setting["aa_subs"]== 'true':
        #       string_dp += (prefix_acat.upper()+':[COLOR %s]%s[/COLOR] '%(tt[zz],len( links_subcenter)))
        #       zz += 1

    # save_all_data.append(links_subcenter)

     #and len(links_subcenter)==0

    # elif source=='aa_subs':
    #     myLogger('AA SUBS DOWNLOAD')
    #     subs = Download_aa(params["link"],mode_subtitle)

'''
elif action =='clear_aa':
     cache.clear(['subs_aa','subs'])
     executebuiltin((u'Notification(%s,%s)' % (__scriptname__, __language__(32004))))
'''

def ManualSearch(title,option,mode_subtitle,imdb_id,item):  #burekas - not in use, need to be tested
    title=title.replace("&"," and ")
    filename = 'subs.search.wizdom.%s.json'%(quote(title))

    #url = "http://api.wizdom.xyz/search.manual.php?filename=%s"%(lowercase_with_underscores(title))
    url = "http://%s/search?action=by_id&imdb=%s" % (myWizdomDomain, imdb_id)

    subtitle_list=[]
    try:

        json = caching_json(filename,url)

        if "season" not in json:
          json['season']=0

        if "episode" not in json:
          json['episode']=0
        if json["type"]=="episode":
            json['year']=0

            #imdb_id = SearchMovie(str(json['title']),json['year'],item,mode_subtitle)
            imdb_id = searchForIMDBID(str(json['title']),item)
            if 'tt' not in imdb_id:
                imdb_id = urllib.request.urlopen("http://api.wizdom.xyz/search.tv.php?name="+quote(json['title'])).read()

            if imdb_id!='' and imdb_id!=0 and option==1:
                num_of_subs,subtitle,subtitle_list=GetWizJson(str(imdb_id),mode_subtitle,json['season'],json['episode'],lowercase_with_underscores(title))

        elif json["type"]=="movie":
            if "year" in json:
                #imdb_id = SearchMovie(str(json['title']),json['year'],item,mode_subtitle)
                imdb_id = searchForIMDBID(str(json['title']),item)
            else:
                json['year']=0
                item['year']=0000
                #imdb_id = SearchMovie(str(json['title']),0,item,mode_subtitle)
                imdb_id = searchForIMDBID(str(json['title']),item)
            if imdb_id and option==1:

                num_of_subs,subtitle,subtitle_list=GetWizJson(str(imdb_id),mode_subtitle,0,0,lowercase_with_underscores(title))

        return(json['title'],json['year'],imdb_id,json['season'],json['episode'],subtitle_list,num_of_subs,subtitle)
    except:    pass

#cinemast / Subcenter - not in use
'''
BASE_URL = "http://www.cinemast.org/he/cinemast/api/"
def login( notify_success=True):
    email = all_setting["Email"]
    password = all_setting["Password"]
    if email=='' or password=='':
        __settings__.openSettings()
        email = all_setting["Email"]
        password = all_setting["Password"]
    post_data = {'username': email, 'password': password}
    content = urlHandler.request(BASE_URL + "login/", post_data)

    if content['result'] == 'success':
        if notify_success:
            notify(32010)

        del content["result"]
        return content
    else:
        notify(32009)
        return None
'''

elif action =='login':
    login(True)

def wizdom_search(item,mode_subtitle,imdb_id):

      if str(imdb_id)[:2]=="tt":
                    num_of_subs,subtitle,subtitle_list=GetWizJson(imdb_id,mode_subtitle,0,0,item['file_original_path'])

      return num_of_subs,subtitle,subtitle_list,imdb_id


def Ktuvit_Search_old(item,mode_subtitle,imdb_id):
   global links_ktuvit
   import requests


   if item["tvshow"]:
       if 'tt' in imdb_id:
         query={"request":
            {
                "SearchPhrase": imdb_id,
                "SearchType": "ImdbID",
                "Version":"1.0",
                "Season":item["season"],
                "Episode":item["episode"]
            }
            }
       else:
         query={"request":
            {
                "SearchPhrase": item["tvshow"],
                "SearchType": "FilmName",
                "Version":"1.0",
                "Season":item["season"],
                "Episode":item["episode"]
            }
            }
       url_n='http://api.ktuvit.me/FindSeries'
   else:
       if 'tt' in imdb_id:
         query={"request":
            {
                "SearchPhrase": imdb_id,
                "SearchType": "ImdbID",
                "Version":"1.0",
                "Season":item["season"],
                "Episode":item["episode"]
            }
            }
       else:
         query={"request":
            {
                "SearchPhrase": item["title"],
                "SearchType": "FilmName",
                "Version":"1.0",
                "year":int(item['year'])
            }
            }

       url_n='http://api.ktuvit.me/FindFilm'

   subtitle=' '
   subtitle_list=[]


   x=requests.post(url_n,json=query,timeout=15).json()

   z=0
   responce=json.loads(x)

   for item_data in responce['Results']:

       url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, item_data["SubtitleName"], "Ktuvit$$$"+item_data["Identifier"])

       json_data={'url':url,
                         'label':"Hebrew",
                         'label2':'[COLOR '+color_open+']'+str(z)+'. '+prefix_ktuvit+' '+item_data["SubtitleName"]+'[/COLOR]',
                         'iconImage':"0",
                         'thumbnailImage':"he",
                         'hearing_imp':'false',
                         'sync': 'false'}



       subtitle_list.append(json_data)
       links_ktuvit=subtitle_list

       z=z+1

   return len(responce['Results']),subtitle,subtitle_list


'''
def download_subscene(url, lang):
    subscene = SubtitleAPI('Hebrew')
    myLogger("DDDDDDDDD : %s" %(params["link"]))
            download_url = subscene.get_download_link(params["link"], params["language"])
        subs = download(download_url)
'''

def search_subscene_old(item,mode_subtitle):
    global sc_subtitle
    import requests
    selected_lang=['heb']
    if MyAddon.getSetting("arabic")== 'true':
        selected_lang.append('ara')
    if MyAddon.getSetting("spanish")== 'true':
        selected_lang.append('spa')


    if len(MyAddon.getSetting("other_lang"))>0:
         all_lang=MyAddon.getSetting("other_lang").split(",")

         for items in all_lang:

            selected_lang.append(items)
    all_lang_codes={

        'Albanian': {'id': 1, '3let': 'alb', '2let': 'sq', 'name': 'Albanian'},
        'Arabic': {'id': 2, '3let': 'ara', '2let': 'ar', 'name': 'Arabic'},
        'Big 5 code': {'id': 3, '3let': 'chi', '2let': 'zh', 'name': 'Chinese'},
        'Brazillian Portuguese': {'id': 4, '3let': 'por', '2let': 'pb', 'name': 'Brazilian Portuguese'},
        'Bulgarian': {'id': 5, '3let': 'bul', '2let': 'bg', 'name': 'Bulgarian'},
        'Chinese BG code': {'id': 7, '3let': 'chi', '2let': 'zh', 'name': 'Chinese'},
        'Croatian': {'id': 8, '3let': 'hrv', '2let': 'hr', 'name': 'Croatian'},
        'Czech': {'id': 9, '3let': 'cze', '2let': 'cs', 'name': 'Czech'},
        'Danish': {'id': 10, '3let': 'dan', '2let': 'da', 'name': 'Danish'},
        'Dutch': {'id': 11, '3let': 'dut', '2let': 'nl', 'name': 'Dutch'},
        'English': {'id': 13, '3let': 'eng', '2let': 'en', 'name': 'English'},
        'Estonian': {'id': 16, '3let': 'est', '2let': 'et', 'name': 'Estonian'},
        'Farsi/Persian': {'id': 46, '3let': 'per', '2let': 'fa', 'name': 'Persian'},
        'Finnish': {'id': 17, '3let': 'fin', '2let': 'fi', 'name': 'Finnish'},
        'French': {'id': 18, '3let': 'fre', '2let': 'fr', 'name': 'French'},
        'German': {'id': 19, '3let': 'ger', '2let': 'de', 'name': 'German'},
        'Greek': {'id': 21, '3let': 'gre', '2let': 'el', 'name': 'Greek'},
        'Hebrew': {'id': 22, '3let': 'heb', '2let': 'he', 'name': 'Hebrew'},
        'Hungarian': {'id': 23, '3let': 'hun', '2let': 'hu', 'name': 'Hungarian'},
        'Icelandic': {'id': 25, '3let': 'ice', '2let': 'is', 'name': 'Icelandic'},
        'Indonesian': {'id': 44, '3let': 'ind', '2let': 'id', 'name': 'Indonesian'},
        'Italian': {'id': 26, '3let': 'ita', '2let': 'it', 'name': 'Italian'},
        'Japanese': {'id': 27, '3let': 'jpn', '2let': 'ja', 'name': 'Japanese'},
        'Korean': {'id': 28, '3let': 'kor', '2let': 'ko', 'name': 'Korean'},
        'Lithuanian': {'id': 43, '3let': 'lit', '2let': 'lt', 'name': 'Lithuanian'},
        'Malay': {'id': 50, '3let': 'may', '2let': 'ms', 'name': 'Malay'},
        'Norwegian': {'id': 30, '3let': 'nor', '2let': 'no', 'name': 'Norwegian'},
        'Polish': {'id': 31, '3let': 'pol', '2let': 'pl', 'name': 'Polish'},
        'Portuguese': {'id': 32, '3let': 'por', '2let': 'pt', 'name': 'Portuguese'},
        'Romanian': {'id': 33, '3let': 'rum', '2let': 'ro', 'name': 'Romanian'},
        'Russian': {'id': 34, '3let': 'rus', '2let': 'ru', 'name': 'Russian'},
        'Serbian': {'id': 35, '3let': 'scc', '2let': 'sr', 'name': 'Serbian'},
        'Slovak': {'id': 36, '3let': 'slo', '2let': 'sk', 'name': 'Slovak'},
        'Slovenian': {'id': 37, '3let': 'slv', '2let': 'sl', 'name': 'Slovenian'},
        'Spanish': {'id': 38, '3let': 'spa', '2let': 'es', 'name': 'Spanish'},
        'Swedish': {'id': 39, '3let': 'swe', '2let': 'sv', 'name': 'Swedish'},
        'Thai': {'id': 40, '3let': 'tha', '2let': 'th', 'name': 'Thai'},
        'Turkish': {'id': 41, '3let': 'tur', '2let': 'tr', 'name': 'Turkish'},
        'Vietnamese': {'id': 45, '3let': 'vie', '2let': 'vi', 'name': 'Vietnamese'}
    }
    seasons = ["Specials", "First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth", "Tenth"]
    seasons = seasons + ["Eleventh", "Twelfth", "Thirteenth", "Fourteenth", "Fifteenth", "Sixteenth", "Seventeenth",
                         "Eighteenth", "Nineteenth", "Twentieth"]
    seasons = seasons + ["Twenty-first", "Twenty-second", "Twenty-third", "Twenty-fourth", "Twenty-fifth", "Twenty-sixth",
                         "Twenty-seventh", "Twenty-eighth", "Twenty-ninth"]

    all_nam_lang={}
    ok_lang=[]
    if item['tvshow']:
        tv_movie='tv'
        name=item['tvshow']
        season=item['season']
        episode=item['episode']
        if len(episode)==1:
          episode_n="0"+episode
        else:
           episode_n=episode
        if len(season)==1:
          season_n="0"+season
        else:
          season_n=season
    else:
        tv_movie='movie'
        name=item['title']
        year=item['year']
    for items in all_lang_codes:
        all_nam_lang[items.lower()]=all_lang_codes[items]['2let']
        if all_lang_codes[items]['3let'] in selected_lang:
            ok_lang.append(items.lower())




    headers = {
        'authority': 'subscene.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'origin': 'https://subscene.com',
        'upgrade-insecure-requests': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'sec-fetch-user': '?1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        #'referer': 'https://subscene.com/subtitles/'+name+'-'+year,
        'accept-encoding': 'utf-8',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',

    }

    data = {
      'query': name,
      'l': ''
    }

    xx=0
    response='Please do not hammer on Subscene'
    x=0
    while 'Please do not hammer on Subscene'  in response:
        response = requests.post('https://subscene.com/subtitles/searchbytitle', headers=headers, data=data).content.decode('utf-8')
        xbmc.sleep(100)
        x+=1
        if x>10:
            break


    if tv_movie=='tv':
        regex='<h2>TV-Series</h2>.+?<ul>(.+?)</ul'
    else:
        regex='<h2 class="exact">Exact</h2>.+?<ul>(.+?)</ul'

    m_pre=re.compile(regex,re.DOTALL).findall(response)

    regex='<div class="title">.+?<a href="(.+?)">(.+?)<'
    m=re.compile(regex,re.DOTALL).findall(m_pre[0])
    sc_subtitle=[]
    all_lk=[]


    for lk,nm in m:
        check=False
        if tv_movie=='movie':
            tname=nm.split('(')[0].strip()

            if name.lower() == tname.lower() and str(year) in nm:
                check=True
        else:
            tname='%s - %s Season'%(name,seasons[int(season)])

            if tname.lower()==nm.lower():
                check=True

        if check:

            x=requests.get('https://subscene.com/'+lk,headers=headers).content.decode('utf-8')

            regex='<tr>(.+?)</tr'
            mm_pre2=re.compile(regex,re.DOTALL).findall(x)
            for itm in mm_pre2:
                regex='<a href="(.+?)">.+?<span class=".+?">(.+?)</span>.+?<span>(.+?)</span>'
                mm=re.compile(regex,re.DOTALL).findall(itm)
                if len(mm)>0:

                    lk2,lang,ver=mm[0]
                    lk2=lk2.replace('\t','').replace('\r','').replace('\n','').strip()
                    lang=lang.replace('\t','').replace('\r','').replace('\n','').strip()
                    ver=ver.replace('\t','').replace('\r','').replace('\n','').strip()
                    if tv_movie=='tv':
                        if ('S%sE%s.'%(season_n,episode_n)).lower() not in ver.lower() and ('S%sE%s '%(season_n,episode_n)).lower() not in ver.lower():
                            continue
                    if lk2  in all_lk:
                        continue
                    if lang.lower() not in ok_lang:
                        continue
                    all_lk.append(lk2)
                    xx+=1

                    cd=''
                    hearing='false'
                    if 'td class="a41"' in itm:
                        hearing='true'
                    bad=''
                    if 'l r bad-icon' in itm:
                        bad='[COLOR red]-BAD SUBTITLE-[/COLOR]'
                    if lang.lower() in all_nam_lang:
                        cd=all_nam_lang[lang.lower()]
                    url = "plugin://%s/?action=download&link=%s&filename=%s&source=%s&language=%s" % (MyScriptID,
                                                                'https://subscene.com/'+lk2,
                                                                ver,
                                                                'subscene',
                                                                lang)
                    json_data={'url':url,
                                 'label':lang,
                                 'label2':str(xx)+'. '+prefix_subscene+bad+ver,
                                 'iconImage':"0",
                                 'thumbnailImage':cd,
                                 'hearing_imp':hearing,
                                 'sync': 'false'}
                    sc_subtitle.append(json_data)
    return sc_subtitle

def aa_subs_old(item,mode_subtitle):
    global links_subcenter
    import requests
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
    }
    results2=[]
    db=[]
    subtitle=' '


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
    if 'tvshow' in item and len(item['tvshow'])>0:
        base_addr='http://185.165.240.137:8080/SUB/Series/'

        title=item["tvshow"].replace(':',' ').replace("'",'').replace(",",' ').replace('  ',' ').lower()
        title2=item["tvshow"].replace(':',' ').replace("'",'').replace(",",' ').replace('  ',' ').replace(' ','.').lower()
        search_string=[title+ep_str,title+ep_str2,title+ep_str3]
        options=[ep_str,ep_str2,ep_str3]
        tv_mode=True
    else:
        base_addr='http://185.165.240.137:8080/SUB/Movies/'
        title=item["title"].replace(':',' ').replace("'",'').replace(",",' ').replace('  ',' ').lower()
        title2=item["title"].replace(':',' ').replace("'",'').replace(",",' ').replace('  ',' ').replace(' ','.').lower()
        tv_mode=False


    progress='requests key'


    req = urllib2.Request(base_addr+'?search='+title.replace(' ','%20'), None, headers)
    resp = urllib2.urlopen(req)
    response=resp.read()

    regex="input type='checkbox' class='selector' name='selection' value=\".+?\".+?<a href=\"(.+?)\"><img src=\".+?\">(.+?)<"
    m=re.compile(regex,re.DOTALL).findall(response)
    count=1

    for lk,items2 in m:

        c_name=items2.replace(':',' ').replace("'",'').replace(",",' ').replace('_',' ').replace('  ',' ').lower()

        if title not in c_name and title2 not in c_name :
            continue

        '''
        regex='.*(\.[1-3][0-9]{3}\.)'
        year_pre=re.compile(regex).findall(items2['name'])
        if len(year_pre)>0:
            myLogger(items2['name'])
            myLogger(year_pre[0])
            myLogger(item['year'])
            if str(item['year'])!=str(year_pre[0]):
                continue
        '''
        ok=True
        if tv_mode:
            ok=False
            for items in options:
                if items.lower()  in items2.lower():
                    ok=True
                    break
        if ok:

            url_down=base_addr+lk

            #z=requests.get(url,headers=headers,stream=True).url
            #myLogger(z)
            url = "plugin://%s/?action=download&link=%s&id=%s&filename=%s&language=%s&source=%s" % (
                MyScriptID,urllib.quote_plus(url_down), items2, items2, 'he','aa_subs')

            if mode_subtitle>1:
                json_data={'url':url,
                             'label':'hebrew',
                             'label2':'[COLOR lightskyblue]'+str(count)+'. '+' [AA]' +items2+'[/COLOR]',
                             'iconImage':"0",
                             'thumbnailImage':"he",
                             'hearing_imp':'false',
                             'sync': 'false'}
                db.append(json_data)
                count+=1
                links_subcenter=db

    return results2,subtitle,db



def get_user_token( force_update=False):
    if force_update:
        subtitle_cache().delete('credentials')

    results = subtitle_cache().get('credentials')
    if results:
        results = json.loads(results)
    else:
        results = login(False)
        if results:
            subtitle_cache().set('credentials', json.dumps(results))

    return results

def subcenter_search_old(item,mode_subtitle):
        global links_subcenter
        results = []

        id_collection=[]
        search_string = re.split(r'\s\(\w+\)$', item["tvshow"])[0] if item["tvshow"] else item["title"]
        user_token =  get_user_token()

        if user_token:
            query = {"q": search_string.encode("utf-8").replace("%20"," "), "user": user_token["user"], "token": user_token["token"]}
            if item["tvshow"]:
                query["type"] = "series"
                query["season"] = item["season"]
                query["episode"] = item["episode"]
            else:
                query["type"] = "movies"
                if item["year"]:
                    query["year_start"] = int(item["year"])
                    query["year_end"] = int(item["year"])

            search_result =  urlHandler.request( BASE_URL + "search/", query)

            if search_result is not None and search_result["result"] == "failed":
                # Update cached token
                user_token =  get_user_token(True)
                query["token"] = user_token["token"]
                search_result =  urlHandler.request( BASE_URL + "search/", query)

            if search_result is not None and search_result["result"] == "failed":
                notify(32009)
                if mode_subtitle>1:
                   return results," "," "
                else:
                   return len(results)," "," "

            myLogger("Results: %s" % search_result)

            if search_result is None or search_result["result"] != "success" or search_result["count"] < 1:
                if mode_subtitle>1:
                   return results," "," "
                else:
                    return len(results)," "," "

            results = search_result# _filter_results(search_result["data"], search_string, item)


            myLogger("Filtered: %s" % results)

        else:
            notify(32009)
        ret = []
        ok=True
        lang=[]
        lang.append('he')
        if all_setting["english"]== 'true':
          lang.append('eng')
        for result in results['data']:
            total_downloads = 0
            counter = 0

            subs_list = result

            if subs_list is not None:


                for language in subs_list['subtitles']:


                       if language in lang:
                    #if xbmc.convertLanguage(language, xbmc.ISO_639_2) in item["3let_language"]:
                        for current in subs_list['subtitles'][language]:


                            counter += 1
                            title = current["version"]
                            subtitle_rate = 0
                            total_downloads += int(current["downloads"])
                            ret.append(
                                {   'lang_index':'0',# item["3let_language"].index('heb'),
                                    'filename': title,
                                    'link': current["key"],
                                    'language_name': xbmc.convertLanguage(language, xbmc.ENGLISH_NAME),
                                    'language_flag': language,
                                    'id': current["id"],
                                    'rating': current["downloads"],
                                    'sync': subtitle_rate >= 3.8,
                                    'hearing_imp': False,
                                    'is_preferred':
                                        xbmc.convertLanguage(language, xbmc.ISO_639_2) == item[
                                            'preferredlanguage']
                                })
            # Fix the rating
            if total_downloads:
                for it in ret[-1 * counter:]:
                    it["rating"] = str(min(int(round(float(it["rating"]) / float(total_downloads), 1) * 8), 5))

        number_of_subs=0
        x=1
        saved_data=[]
        results2= sorted(ret, key=lambda x: (x['is_preferred'], x['lang_index'], x['sync'], x['rating']), reverse=True)
        subtitle=" "
        json_data=[]
        db=[]
        if results2:
         for it in results2:

            number_of_subs=number_of_subs+1
            listitem = ListItem(label=it["language_name"],
                                        label2='[COLOR lightskyblue]'+str(x)+'. '+' [SC]' +it["filename"]+'[/COLOR]',
                                        iconImage=it["rating"],
                                        thumbnailImage=it["language_flag"]
                                        )
            if it["sync"]:
                listitem.setProperty("sync", "true")
                sync='true'
            else:
                listitem.setProperty("sync", "false")
                sync='false'

            if it.get("hearing_imp", False):
                listitem.setProperty("hearing_imp", "true")
                hearing_imp='true'
            else:
                listitem.setProperty("hearing_imp", "false")
                hearing_imp="false"

            url = "plugin://%s/?action=download&link=%s&id=%s&filename=%s&language=%s" % (
                MyScriptID, it["link"], it["id"], it["filename"], it["language_flag"])
            if it["id"] not in id_collection:
              id_collection.append(it["id"])
              if mode_subtitle>1:
                json_data={'url':url,
                             'label':it["language_name"],
                             'label2':'[COLOR lightskyblue]'+str(x)+'. '+' [SC]' +it["filename"]+'[/COLOR]',
                             'iconImage':it["rating"],
                             'thumbnailImage':it["language_flag"],
                             'hearing_imp':hearing_imp,
                             'sync':sync}
                db.append(json_data)
                links_subcenter=db
                x=x+1



        return results2,subtitle,db

def download(mode_subtitle,filename):
    if filename!='':
        subtitle_list = []
        exts = [".srt", ".sub"]

        zip_filename = os.path.join(__temp__, "subs.zip")

        try:
            shutil.rmtree(__temp__)
        except: pass

        xbmcvfs.mkdirs(__temp__)

        query = {"v": filename,"key": key,"sub_id": id}

        user_token = get_user_token()

        url = BASE_URL + "subtitle/download/" + language + "/?" + urllib.urlencode(query)

        f = urlHandler.request(url, user_token)

        if f==None:
            if mode_subtitle>1:
                return '',False
            else:
                return 'NO',False

        if len(f)<100:
            if mode_subtitle==3:
                xbmcgui.Dialog().ok("Subscenter",str(f))
            else:
                xbmcgui.Dialog().notification('Subcenter Download', str(f), xbmcgui.NOTIFICATION_INFO,1000 )
            return 'NO',False
        else:
            with open(zip_filename, "wb") as subFile:
                subFile.write(f)
            subFile.close()
            xbmc.sleep(500)
            try:
                with contextlib.closing(ZipFile(zip_filename , "r")) as z:
                    z.extractall(__temp__)
            except:
                with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                    zip_ref.extractall(__temp__)
            #with zipfile.ZipFile(zip_filename) as zf:
            #    zf.extractall(__temp__)

        file_list=(os.listdir(__temp__ ))

        for file in file_list:
            full_path = os.path.join(__temp__, file)

            if os.path.splitext(full_path)[1] in exts:
                subtitle_list.append(full_path)

        if mode_subtitle>1:
            return subtitle_list," "
        else:
            #xbmc.Player().setSubtitles(subtitle_list[0])

            if len (subtitle_list)>0:
                sub_result=subtitle_list[0]
            else:
                sub_result='0'
            return sub_result,True


'''
class popupBtns(xbmcgui.WindowDialog):
    def __init__(self, title='', btns=[], width=1):
        self.w = width
        self.selected = -1
        self.btns = btns
        self.btnCnts = [0]
        for i in range(len(btns)-1): # There has to be a better way to do this. zeros doesn't work...
            self.btnCnts.append(0)

#   def onInit(self):
        w = self.w
        w = int(self.getWidth()*width)
        pad = self.getHeight()/100
        hCnt = 5*pad
        yo = pad

        h = len(self.btns) * (hCnt + 5) + yo
        mediaDir = os.path.join(os.getcwd().replace(";",""),'resources','skins','DefaultSkin','media')
        rw = self.getWidth()
        rh = self.getHeight()
        x = rw/2 - w/2
        y = rh/2 - h/2

        # Background
        self.imgBg = xbmcgui.ControlImage(0+x-4*pad,0+y-4*pad,w+8*pad,h+8*pad, os.path.join(mediaDir,'gs-bg-menu.png'))
        self.addControl(self.imgBg)

        i = 0
        while i < len(self.btns):
            self.btnCnts[i] = xbmcgui.ControlButton(pad+x, yo+y, w-2*pad, hCnt, str(self.btns[i]), os.path.join(mediaDir,'button_focus.png'), '', font='font12', textColor='0xFFFFFFFF', alignment=2)
            self.addControl(self.btnCnts[i])
            yo += hCnt + 5
            i += 1

        self.setFocus(self.btnCnts[0])

    def onControl(self, action):
        pass

    def onAction(self, action):
        if action == 10:
            self.close()
        elif (action == 3) or (action == 4) or (action == 7) or (action == 9):
            try:
                cnt = self.getFocus()
            except:
                self.setFocus(self.btnCnts[0])
                return None

            d = 0
            if action == 3: # Up
                d = -1
            elif action == 4: # Down
                d = 1
            l = len(self.btnCnts)
            for i in range(l):
                if self.btnCnts[i] == cnt:
                    if action == 7: # Select
                        self.selected = i
                        self.close()
                    elif action == 9: # Back
                        self.close()
                    elif i+d > l-1:
                        self.setFocus(self.btnCnts[0])
                    elif i+d < 0:
                        self.setFocus(self.btnCnts[l-1])
                    else:
                        self.setFocus(self.btnCnts[i+d])

'''



'''
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmc_translate_path(addonInfo('profile')).decode('utf-8')
cacheFile = os.path.join(dataPath, 'subs_history.db')
xbmcvfs.mkdir(dataPath)
dbcon = database.connect(cacheFile)
dbcur = dbcon.cursor()


dbcur.execute("CREATE TABLE IF NOT EXISTS AllData ( ""title TEXT, ""episode TEXT, ""season TEXT, ""year TEXT, ""tvshow TEXT, ""file_original_path TEXT, ""full_path TEXT, ""subs TEXT);")
try:
    dbcur.execute("VACUUM 'AllData';")
    dbcur.execute("PRAGMA auto_vacuum;")
    dbcur.execute("PRAGMA JOURNAL_MODE=MEMORY ;")
    dbcur.execute("PRAGMA temp_store=MEMORY ;")
except:
 pass
dbcon.commit()
'''


'''
myLogger('sub path')
myLogger(sub)
fh = open(sub, 'r')

f_text=(fh.read())
encoding=(chardet.detect(f_text)['encoding'])
final_txt=(f_text.decode(encoding).encode("utf8"))
'''
'''
dbcur.execute("SELECT * FROM AllData WHERE title = '%s'  AND season='%s' AND episode = '%s' AND year='%s' AND tvshow='%s' and file_original_path='%s' and full_path='%s'"%(item['title'].replace("'"," "),item['season'],item['episode'],item['year'],item['tvshow'].replace("'"," "),item['file_original_path'].replace("'"," "),item['full_path'].replace("'"," ")))

match = dbcur.fetchone()

if 'filename' in params:
    final_txt=params['filename'].replace('.srt','').replace('.sub','')
elif 'versioname' in params:
    final_txt=params['versioname'].replace('.srt','').replace('.sub','')

if match==None:


    dbcur.execute("INSERT INTO AllData Values ('%s', '%s', '%s', '%s','%s', '%s', '%s','%s');" %  (item['title'].replace("'"," "),item['season'],item['episode'],item['year'],item['tvshow'].replace("'"," "),item['file_original_path'].replace("'"," "),item['full_path'].replace("'"," "),final_txt.replace("'"," ")))

    dbcon.commit()
else:
    dbcur.execute("UPDATE AllData SET subs='%s' WHERE title= '%s'  AND season='%s' AND episode = '%s' AND year='%s' AND tvshow='%s' and file_original_path='%s' and full_path='%s' " %  (final_txt.replace("'"," "),item['title'].replace("'"," "),item['season'],item['episode'],item['year'],item['tvshow'].replace("'"," "),item['file_original_path'].replace("'"," "),item['full_path'].replace("'"," ")))

    dbcon.commit()
'''