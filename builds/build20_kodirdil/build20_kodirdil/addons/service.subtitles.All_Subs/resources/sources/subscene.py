# Import necessary libraries
import os,shutil
import sys
import traceback
import xbmcaddon,xbmc
global global_var,site_id,sub_color
global_var=[]
from resources.modules import log
import requests,json,re
import ssl,urllib3
import urllib,xbmcvfs
import urllib.parse
from resources.modules.extract_sub import extract
# SUBSCENE
from resources.modules import cloudscraper
from resources.modules import num2ordinal
from resources.modules.iso639 import iso639_langauge_convert
#########################################

Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_subscene'))
que=urllib.parse.quote_plus

########### Constants ###################
SUBSCENE_URL = "https://subscene.com"
site_id='[Subscene]'
sub_color='deepskyblue'
# global subscene title_href:
title_href=''
#########################################

################### CLOUDFLARE REUQESTS FUNCTIONS ###################################
class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = urllib3.poolmanager.PoolManager(num_pools=connections,
                                                           maxsize=maxsize,
                                                           block=block,
                                                           ssl_version=ssl.PROTOCOL_TLSv1_2,
                                                           ssl_context=ctx)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def __retry(request, response, next, cfscrape, retry=0):
    if retry > 5:
        return None

    if response.status_code in [503, 429, 409, 403]:
        if response.status_code == 503:
            xbmc.sleep(2000)
            retry = 5
        if response.status_code == 429:
            xbmc.sleep(3000)
        if response.status_code == 409:
            xbmc.sleep(3000)

        retry += 1
        request['validate'] = lambda response: __retry(request, response, next, cfscrape, retry)
        request['next'] = next
        request['cfscrape'] = cfscrape
        return request

def execute_request(request, session=None):
     
    try:
        default_timeout = int(Addon.getSetting("time_s"))
    except:
        default_timeout = 10
    request.setdefault('timeout', default_timeout)

    next = request.pop('next', None)

    cfscrape = 'cfscrape' in request
    request.pop('cfscrape', None)

    validate = request.pop('validate', None)
    if not validate:
        validate = lambda response: __retry(request, response, next, cfscrape)

    if next:
        request.pop('stream', None)

    log.warning('DEBUG | Subscene | execute_request params | %s ^ - %s, %s' % (request['method'], request['url'], json.dumps(request.get('params', {}))))
    try:
        if cfscrape:
            request.pop('cfscrape', None)
            if not session:
                session = cloudscraper.create_scraper(interpreter='native')
            response = session.request(**request)
        else:
            session = requests.session()
            session.mount('https://', TLSAdapter())
            response = session.request(**request)
        exc = ''
    except:
        try:
            if cfscrape:
                if not session:
                    session = cloudscraper.create_scraper(interpreter='native')
                response = session.request(verify=False, **request)
            else:
                response = requests.request(verify=False, **request)
            exc = ''
        except:
            exc = traceback.format_exc()
            response = lambda: None
            response.text = ''
            response.content = ''
            response.status_code = 500
    log.warning('DEBUG | Subscene | execute_request result | %s $ - %s - %s, %s' % (request['method'], request['url'], response.status_code, exc))

    alt_request = validate(response)
    if alt_request:
        return execute_request(alt_request)

    if next and response.status_code == 200:
        next_request = next(response)
        if next_request:
            return execute_request(next_request, session)
        else:
            return None

    return response
#####################################################################################


############## SUBSCENE SUBTTILES SEARCH FUNCTIONS ##################################

def get_episode_pattern(season_and_episode):

    parts = season_and_episode.split(':')
    
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
    
    
def __match_title(title, year, response):
    title_with_year = '%s (%s)' % (title, year)
    href_regex = r'<a href="(.*?)">' + re.escape(title_with_year) + r'</a>'
    return re.search(href_regex, response.text, re.IGNORECASE)

def __find_title_result(title, year, response, subscene_lang_ids):

    # Try match with the previous year
    previous_year = int(year) - 1
    # Try match with the next year
    next_year = int(year) + 1
    result = __match_title(title, year, response) or __match_title(title, previous_year, response) or __match_title(title, next_year, response) or None

    if not result:
        return None

    global title_href
    title_href = result.group(1)

    request = {
        'cfscrape': True,
        'method': 'GET',
        'url': SUBSCENE_URL + title_href
    }

    # Add LanguageFilter parameter as a cookie (from subscene_lang_ids)
    if subscene_lang_ids: # If empty - will search in all languages
        languages_ids_filter = f"LanguageFilter={','.join(map(str, subscene_lang_ids))}"
        request['headers'] = {}
        request['headers']['Cookie'] = languages_ids_filter

    return request

def build_search_requests(media_type, title, year, season, subscene_lang_ids):

    if media_type == 'tv':
        ordinal_season = num2ordinal.convert(season).strip()
        title = '%s - %s Season' % (title, ordinal_season)

    request = {
        'cfscrape': True,
        'method': 'GET',
        'url': SUBSCENE_URL + ('/subtitles/searchbytitle?query=' + que(title)),
        'next': lambda response: __find_title_result(title, year, response, subscene_lang_ids),
    }

    return request

def parse_search_response(media_type, season, episode, search_response):
    global title_href
    any_regex = r'.*?'

    results_regex = (
            r'<a href="' + re.escape(title_href) + r'(.*?)">' +
                any_regex + r'</span>' + any_regex +
                r'<span>(.*?)</span>' + any_regex +
            r'</a>' + any_regex +
            r'(<td class="a41">)?' + any_regex +
        r'</tr>'
    )

    results = re.findall(results_regex, search_response.text, re.DOTALL)
    if not results:
        return None

    if media_type == 'tv':
        season_number = season.zfill(2)
        episode_number = episode.zfill(2)
        episodeid = 's%se%s' % (season_number, episode_number)
        # Regex Options: .S01. | S01E01 | 01x01
        identifier = r'(\.s%s\.|%s|\b%sx%s\b)' % (season_number, episodeid, season_number, episode_number)
        results = list(filter(lambda x: re.search(identifier, x[1], re.IGNORECASE), results))

    def map_result(result):
    
        # Example: https://subscene.com/argylle/hebrew/3297430
        download_href_url = '%s%s%s' % (SUBSCENE_URL, title_href, result[0])
        
        # Example: hebrew
        lang_from_subscene = result[0].split('/')[1]
        # Example: Hebrew
        FullLanguageName = iso639_langauge_convert.get_lang_id(lang_from_subscene.split('_')[-1].capitalize(), xbmc.ENGLISH_NAME) or lang_from_subscene.split('_')[-1].capitalize()
        # Example: he
        thumbnailImageLanguageName = iso639_langauge_convert.get_lang_id(FullLanguageName, xbmc.ISO_639_1)
        
        subtitle_file_name = result[1].strip()
        
        impaired = "true" if result[2] != '' else "false"
        
        download_data={}
        download_data['lang_from_subscene'] = lang_from_subscene
        download_data['download_href_url'] = download_href_url
        download_data['season_and_episode'] = f'{season}:{episode}'
        download_data['media_type'] = media_type
        url = "plugin://%s/?action=download&download_data=%s&filename=%s&language=%s&source=subscene" % (MyScriptID,
                                                    que(json.dumps(download_data)),
                                                    que(subtitle_file_name),
                                                    FullLanguageName)
        json_data={'url':url,
                     'label':FullLanguageName,
                     'label2':site_id+' '+subtitle_file_name,
                     'iconImage':"0",
                     'thumbnailImage':thumbnailImageLanguageName,
                     'hearing_imp':impaired,
                     'site_id':site_id,
                     'sub_color':sub_color,
                     'filename':subtitle_file_name,
                     'sync':'false',
                     'download_href_url':download_href_url}
                     
        return json_data

    return list(map(map_result, results))
#####################################################################################

############## SUBSCENE SUBTTILES DOWNLOAD FUNCTIONS ##################################
def build_download_request(download_href_url, lang_from_subscene):
    download_url = '/subtitles/%s-text/' % lang_from_subscene.lower()
    href_regex = r'<a href="(' + re.escape(download_url) + r'.*?)"'

    def find_download_href(response):
        result = re.search(href_regex, response.text)
        if not result:
            return None

        return {
            'cfscrape': True,
            'method': 'GET',
            'url': '%s%s' % (SUBSCENE_URL, result.group(1)),
            'stream': True
        }

    request = {
        'cfscrape': True,
        'method': 'GET',
        'url': download_href_url,
        'next': lambda response: find_download_href(response)
    }

    return request
#####################################################################################

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

def get_subs(item):

    Addon=xbmcaddon.Addon()
    global global_var
    log.warning('DEBUG | Subscene | Searching Subcene')

    title = item.get('OriginalTitle', '')
    media_type = item.get('media_type', '')
    season = item.get('season', '')
    episode = item.get('episode', '')
    year = item.get('year', '')
    
    #############################################################################
    from resources.modules.general import remove_year_from_title
    title = remove_year_from_title(title)
    #############################################################################
    
    
    ######################### LANGUAGE FILTER ####################################
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
    if Addon.getSetting("all_lang")=='true':
        selected_lang=['ALL']


    subscene_lang_ids = []
    if not selected_lang==['ALL']:
        for lang in selected_lang:
            for lang_name, lang_info in all_lang_codes.items():
                if lang == lang_info['3let']:
                    subscene_lang_ids.append(lang_info['id'])
        subscene_lang_ids.sort()
    log.warning(f"DEBUG | Subscene | LanguageFilter is: {str(selected_lang)} | {str(subscene_lang_ids)}")
    ################################################################################
            

    search_request = build_search_requests(media_type, title, year, season, subscene_lang_ids)
    search_response = execute_request(search_request)
    log.warning(f"DEBUG | Subscene | get_subs | search_response.status_code={search_response.status_code}")

    subtitles_search_results = []
    if search_response and search_response.status_code == 200 and search_response.text:
        subtitles_search_results = parse_search_response(media_type, season, episode, search_response)
    else:
        log.warning(f"DEBUG | Subscene | get_subs | no results.")
        return []
    
    subscene_subtitles_results =[]
    all_links=[]
    
    for subtitle_search_result in subtitles_search_results:
        if subtitle_search_result["download_href_url"] in all_links:
            continue
        all_links.append(subtitle_search_result["download_href_url"])
        subscene_subtitles_results.append(subtitle_search_result)
        
    global_var=subscene_subtitles_results
    
def download(download_data,MySubFolder):

    try:
        shutil.rmtree(MyTmp)
    except Exception as e:
        log.warning(e)
        pass
        
    sub_file = ''
        
    try:
        xbmcvfs.mkdirs(MyTmp)
        download_href_url = download_data['download_href_url']
        media_type = download_data['media_type']
        season_and_episode = download_data['season_and_episode']
        lang_from_subscene = download_data['lang_from_subscene']
        

        download_request = build_download_request(download_href_url, lang_from_subscene)
        download_response = execute_request(download_request)
        log.warning(f"DEBUG | Subscene | download | download_response.status_code={download_response.status_code}")
        

        local_tmp_file = os.path.join(MyTmp, "subscene.xxx")
        packed = False
        typeid = "zip"

        try:
            with open(local_tmp_file, 'wb') as f:
                f.write(download_response.content)
        
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
            log.warning("DEBUG | Subscene | Failed to save subtitle to %s" % local_tmp_file)
            
        xbmc.sleep(100)
        log.warning('DEBUG | Subscene | Extract')
        extract(local_tmp_file,MyTmp)
        
        episode_pattern = None
        if media_type == 'tv':
            episode_pattern = re.compile(get_episode_pattern(season_and_episode), re.IGNORECASE)
            
        exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass"]   
        for dir in xbmcvfs.listdir(MyTmp)[0]:
            for file in xbmcvfs.listdir(os.path.join(MyTmp, dir))[1]:
                if os.path.splitext(file)[1] in exts:

                    if episode_pattern and not episode_pattern.search(file):
                        continue
                   
                    sub_file=(os.path.join(MyTmp, dir, file))

        for file in xbmcvfs.listdir(MyTmp)[1]:
            if os.path.splitext(file)[1] in exts:
               
                if episode_pattern and not episode_pattern.search(file):
                    continue
                
                sub_file=(os.path.join(MyTmp, file))

    except Exception as e:
        import linecache
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        log.warning('DEBUG | Subscene | Error in Download subs:'+str(e)+','+'line:'+str(lineno))
        
    log.warning(f"DEBUG | Subscene | download | sub_file={str(sub_file)}")
    return sub_file
    