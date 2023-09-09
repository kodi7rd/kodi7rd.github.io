import uuid,os,gzip,shutil
import xbmcaddon,xbmc
global global_var,stop_all,site_id,sub_color#global
global_var=[]
from resources.modules import log
import requests,json,re
from resources.modules import cache
Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
from resources.modules import cloudscraper
import requests,ssl,urllib3
import urllib,xbmcvfs
import urllib.parse
from resources.modules.extract_sub import extract
from urllib.request import urlopen
from urllib.request import Request
url_encode=urllib.parse.urlencode
xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_subscene'))
que=urllib.parse.quote_plus
site_id='[SS]'
sub_color='khaki'
main_url = "https://subscene.com"
class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        ctx.check_hostname = False
        self.poolmanager = urllib3.poolmanager.PoolManager(num_pools=connections,
                                                           maxsize=maxsize,
                                                           block=block,
                                                           ssl_version=ssl.PROTOCOL_TLSv1_2,
                                                           ssl_context=ctx)
def get_episode_pattern(episode):
    parts = episode.split(':')
    if len(parts) < 2:
        return "%%%%%"
    season = int(parts[0])
    epnr = int(parts[1])
    patterns = [
        "s%#02de%#02d" % (season, epnr),
        "%#02dx%#02d" % (season, epnr),
    ]
    if season < 10:
        patterns.append("(?:\A|\D)%dx%#02d" % (season, epnr))
    return '(?:%s)' % '|'.join(patterns)                                                    
                                                           
def get_subs(item):
    Addon=xbmcaddon.Addon()
    global global_var
    log.warning('Searching Subcene')
    
    selected_lang=[]
    if Addon.getSetting("language_hebrew")=='true':
        selected_lang.append('heb')
    if Addon.getSetting("language_english")=='true':
        selected_lang.append('eng')
    if Addon.getSetting("language_russian")=='true':
        selected_lang.append('rus')
    if Addon.getSetting("language_arab")=='true':
        selected_lang.append('ara')
    if len(Addon.getSetting("other_lang"))>0:
         all_lang=Addon.getSetting("other_lang").split(",")
         
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
    episode=""
    if item['TVshowtitle']:
        tv_movie='tv'
        name=item['OriginalTitle']
        season=item['season']
        episode=item['season']+':'+item['episode']
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
        name=item['OriginalTitle']
        year=item['year']
    try:
        
        s_title=re.compile("([ .\w']+?)(\W\d{4}\W?.*)").findall(name)[0][0]
    except:
        s_title=name
            
    for items in all_lang_codes:
        all_nam_lang[items.lower()]=all_lang_codes[items]['2let']
        if all_lang_codes[items]['3let'] in selected_lang:
            ok_lang.append(items.lower())
        
        
        
    
       
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://subscene.com',
        'Connection': 'keep-alive',
        'Referer': 'https://subscene.com/subtitles/searchbytitle',
        # 'Cookie': '_ga=GA1.2.1911444577.1676157427; _gid=GA1.2.826212615.1676157427; __cf_bm=U6vk6_ayA3eGJOawuM5ziO3G0MNx.xmU9bv8n3f63Pk-1676157428-0-Ab5tPbuawh9No7AMAdQzwKFPDv9/ukvntu7svSdPjDMgw1IXkiQq7qVs/j6IeRUCvs9QWAY3KTuyNoOjatY5Sfv495P9U2Z3NqeWvgjekVV20mGbHRBKAe7+fL5+UkQ+6rPL0Uheu/AnTBDTBup1WqM=',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    data = {
      'query': name,
      'l': ''
    }
    

    scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
    scraper.mount('https://', TLSAdapter())
    xx=0
    response='Please do not hammer on Subscene'
    x=0
    while 'Please do not hammer on Subscene'  in response:
        response = scraper.post('https://subscene.com/subtitles/searchbytitle?query='+s_title, headers=headers, data=data)
        if response.status_code in [503, 429, 403]:
            if response.status_code == 503:
                xbmc.sleep(2000)
             
            if response.status_code == 429:
                xbmc.sleep(3000)
        else:
            response=response.content.decode('utf-8')
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
    m=re.compile(regex,re.DOTALL).findall(response)
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
            
           
            
            xx=0
            response='Please do not hammer on Subscene'
            x=0
            while 'Please do not hammer on Subscene'  in response:
                response = scraper.get('https://subscene.com/'+lk,headers=headers)
                if response.status_code in [503, 429, 403]:
                    if response.status_code == 503:
                        xbmc.sleep(2000)
                     
                    if response.status_code == 429:
                        xbmc.sleep(3000)
                else:
                    response=response.content.decode('utf-8')
                xbmc.sleep(100)
                x+=1
                if x>10:
                    break
            x=response
           
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
                        
                        if ('S%sE%s.'%(season_n,episode_n)).lower() not in ver.lower() and ('S%sE%s '%(season_n,episode_n)).lower() not in ver.lower() and ('S%s.'%(season_n)).lower() not in ver.lower():
                            continue
                    
                    if lk2  in all_lk:
                        continue
                    if Addon.getSetting("all_lang")== 'false': 
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
                    download_data={}
                    download_data['link']='https://subscene.com/'+lk2
                    download_data['episode']=episode
                    url = "plugin://%s/?action=download&download_data=%s&filename=%s&language=%s&source=subscene" % (MyScriptID,
                                                                que(json.dumps(download_data)),
                                                                que(ver),
                                                                lang)
                    json_data={'url':url,
                                 'label':lang,
                                 'label2':site_id+' '+bad+ver,
                                 'iconImage':"0",
                                 'thumbnailImage':cd,
                                 'hearing_imp':hearing,
                                 'site_id':site_id,
                                 'sub_color':sub_color,
                                 'filename':ver,
                                 'sync': 'false'}
                    sc_subtitle.append(json_data)
                    global_var=sc_subtitle
def geturl(url, cookies=None):
    import io
    
    try:
        request = Request(url)
        request.add_header('Accept-encoding', 'gzip')
        if cookies:
            request.add_header('Cookie', cookies)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:41.0) Gecko/20100101 Firefox/41.0')
        response = urlopen(request)
        
        if response.info().get('Content-Encoding') == 'gzip':
            buf = io.BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            content = f.read()
        else:
            content = response.read()
       
        # Fix non-unicode characters in movie titles
        strip_unicode = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?<>\\]+|[^\s]+)")
        content = strip_unicode.sub('', content.decode("utf-8"))
        return_url = response.geturl()
       
    except Exception as e:
        log.warning( "Failed to get url: %s" % e)
        content = None
        return_url = None
    return content, return_url
    
def download(download_data,MySubFolder):
    
    try:
        shutil.rmtree(MyTmp)
    except Exception as e:
        log.warning(e)
        pass
    xbmcvfs.mkdirs(MyTmp)
    link=download_data['link']
    episode=download_data['episode']
    
    
    session = cloudscraper.create_scraper(interpreter='native')
    session.mount('https://', TLSAdapter())
    subtitle_list = ''
    exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass"]
    downloadlink_pattern = "...<a href=\"(.+?)\" rel=\"nofollow\" onclick=\"DownloadSubtitle"

    uid = uuid.uuid4()


    content, response_url = geturl(link)
    match = re.compile(downloadlink_pattern).findall(content)
    if match:
        downloadlink = main_url + match[0]
        viewstate = 0
        previouspage = 0
        subtitleid = 0
        typeid = "zip"
        filmid = 0
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://subscene.com',
            'Connection': 'keep-alive',
            'Referer': 'https://subscene.com/subtitles/searchbytitle',
            # 'Cookie': '_ga=GA1.2.1911444577.1676157427; _gid=GA1.2.826212615.1676157427; __cf_bm=U6vk6_ayA3eGJOawuM5ziO3G0MNx.xmU9bv8n3f63Pk-1676157428-0-Ab5tPbuawh9No7AMAdQzwKFPDv9/ukvntu7svSdPjDMgw1IXkiQq7qVs/j6IeRUCvs9QWAY3KTuyNoOjatY5Sfv495P9U2Z3NqeWvgjekVV20mGbHRBKAe7+fL5+UkQ+6rPL0Uheu/AnTBDTBup1WqM=',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            # Requests doesn't support trailers
            # 'TE': 'trailers',
        }
        postparams = url_encode(
            {'__EVENTTARGET': 's$lc$bcr$downloadLink', '__EVENTARGUMENT': '', '__VIEWSTATE': viewstate,
             '__PREVIOUSPAGE': previouspage, 'subtitleId': subtitleid, 'typeId': typeid, 'filmId': filmid}).encode('utf-8')
        
        useragent = ("User-Agent=Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) "
                       "Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)")
        headers2 = {'User-Agent': useragent, 'Referer': link}
       
        #request = Request(downloadlink, postparams, headers)

        # xbmc.log('bla bla'+str(request), 5)
        response=session.get(downloadlink,headers=headers,verify=False,stream=True)
        #response = urlopen(request)
        # request = urllib2.Request(downloadlink, postparams, headers)
        # response = urllib2.urlopen(request)
        

        local_tmp_file = os.path.join(MyTmp, "subscene.xxx")
        packed = False

        try:
       
            with open(local_tmp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=512):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            # Check archive type (rar/zip/else) through the file header (rar=Rar!, zip=PK)
            myfile = xbmcvfs.File(local_tmp_file, "rb")
            myfile.seek(0,0)
            if myfile.read(1) == 'R':
                typeid = "rar"
                packed = True
                
            else:
                myfile.seek(0,0)
                if myfile.read(1) == 'P':
                    typeid = "zip"
                    packed = True
                    
                else:
                    typeid = "srt"
                    packed = False
            
            myfile.close()
            local_tmp_file = os.path.join(MyTmp, "subscene." + typeid)
            xbmcvfs.rename(os.path.join(MyTmp, "subscene.xxx"), local_tmp_file)
            
        except:
            log.warning( "Failed to save subtitle to %s" % local_tmp_file)
        xbmc.sleep(100)
        log.warning('Extract')
        sub_file=extract(local_tmp_file,MyTmp)
        

        episode_pattern = None
        if episode != '':
         
            episode_pattern = re.compile(get_episode_pattern(episode), re.IGNORECASE)
   
        for dir in xbmcvfs.listdir(MyTmp)[0]:
            for file in xbmcvfs.listdir(os.path.join(MyTmp, dir))[1]:
                if os.path.splitext(file)[1] in exts:

                    if episode_pattern and not episode_pattern.search(file):
                        continue
                   
                    subtitle_list=(os.path.join(MyTmp, dir, file))

        for file in xbmcvfs.listdir(MyTmp)[1]:
            if os.path.splitext(file)[1] in exts:
               
                if episode_pattern and not episode_pattern.search(file):
                    continue
                
                subtitle_list=(os.path.join(MyTmp, file))


    return subtitle_list