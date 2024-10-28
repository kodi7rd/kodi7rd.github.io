# Import necessary libraries
import shutil
import xbmcaddon,os,xbmc
global global_var,site_id,sub_color#global
global_var=[]
from resources.modules import log
import requests,json
import urllib
from resources.modules.extract_sub import extract
from resources.modules.general import DEFAULT_REQUEST_TIMEOUT
from resources.modules.general import extract_season_episode_numbers
import xbmcvfs
import re
#########################################

que=urllib.parse.quote_plus
Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
MyAddonName = Addon.getAddonInfo('name')
MyAddonVersion    = Addon.getAddonInfo('version') # Module version
USER_AGENT = '%s v%s' %(MyAddonName, MyAddonVersion)
xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_subsource'))

########### Constants ###################
site_id='[SubSource]'
sub_color='deepskyblue'
SUBSOURCE_URL = "https://subsource.net"
SUBSOURCE_BASE_API_URL = "https://api.subsource.net/api"
SUBSOURCE_SEARCH_API_URL = f"{SUBSOURCE_BASE_API_URL}/searchMovie"
SUBSOURCE_LIST_SUBS_API_URL = f"{SUBSOURCE_BASE_API_URL}/getMovie"
SUBSOURCE_DOWNLOAD_API_URL = f"{SUBSOURCE_BASE_API_URL}/downloadSub"
        
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
    'content-type': 'application/json',
    'origin': SUBSOURCE_URL,
    'priority': 'u=1, i',
    'referer': SUBSOURCE_URL,
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

all_lang_codes = {
    'sqi': 'Albanian',
    'ara': 'Arabic',
    'ben': 'Bengali',
    'por': 'Brazilian Portuguese',
    'bul': 'Bulgarian',
    'zho': 'Chinese',
    'hrv': 'Croatian',
    'ces': 'Czech',
    'dan': 'Danish',
    'nld': 'Dutch',
    'eng': 'English',
    'fas': 'Farsi/Persian',
    'fin': 'Finnish',
    'fre': 'French',
    'deu': 'German',
    'ell': 'Greek',
    'heb': 'Hebrew',
    'hun': 'Hungarian',
    'ind': 'Indonesian',
    'ita': 'Italian',
    'jpn': 'Japanese',
    'kor': 'Korean',
    'lit': 'Lithuanian',
    'mkd': 'Macedonian',
    'msa': 'Malay',
    'nor': 'Norwegian',
    'pol': 'Polish',
    'ron': 'Romanian',
    'rus': 'Russian',
    'srp': 'Serbian',
    'slv': 'Slovenian',
    'spa': 'Spanish',
    'swe': 'Swedish',
    'tha': 'Thai',
    'tur': 'Turkish',
    'urd': 'Urdu',
    'vie': 'Vietnamese'
}
#########################################
       
def get_subs(video_data, all_lang_override=False):

    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    
    global global_var
    log.warning('DEBUG | [SubSource] | Searching SubSource')

    media_type = video_data.get('media_type', '')
    season = video_data.get('season', '')
    episode = video_data.get('episode', '')
    imdb_id = video_data.get('imdb', '')
    
    if not imdb_id or not imdb_id.startswith('tt'):
        log.warning(f'DEBUG | [SubSource] |  IMDb ID missing. exiting...')
        return []
    
    
    selected_lang = []
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
            selected_lang.append(str(items))
    if Addon.getSetting("all_lang")=='true' or all_lang_override==True:
        selected_lang = ['ALL']
    else:
        selected_lang = [all_lang_codes[code] for code in selected_lang if code in all_lang_codes]
        
    data = {
        'query': imdb_id
    }

    try:
        response = requests.post(SUBSOURCE_SEARCH_API_URL, json=data, headers=headers, timeout=DEFAULT_REQUEST_TIMEOUT)
        response.raise_for_status()
        log.warning(f"DEBUG | [SubSource] | SubSource SearchSubtitles | URL: {response.url} | POST data: {data} | Status Code: {response.status_code}")
        response = response.json()
        
        if response['success'] and response['found']:
            linkName = response['found'][0]['linkName']

            data = {
                "movieName": linkName
                # "langs": [<langs>] Works in web, but API not honoring this param.
            }
            
            # TV Show - Specify season number
            if media_type == 'tv':
                 data['season'] = f"season-{season}"
            
            response = requests.post(SUBSOURCE_LIST_SUBS_API_URL, json=data, headers=headers, timeout=DEFAULT_REQUEST_TIMEOUT)
            response.raise_for_status()
            log.warning(f"DEBUG | [SubSource] | SubSource SearchSubtitles | URL: {response.url} | POST data: {data} | Status Code: {response.status_code}")
            response_subtitles_list = response.json()
            
            if not (response_subtitles_list['success'] and response_subtitles_list['subs']):
                return []
            
            response_subtitles_list = response_subtitles_list['subs']
            
            # Filter subtitles based on selected languages before entering the for loop
            if selected_lang != ['ALL']:
                response_subtitles_list = [
                    response_subtitle for response_subtitle in response_subtitles_list
                    if 'lang' in response_subtitle and (
                        xbmc.convertLanguage(response_subtitle['lang'], xbmc.ENGLISH_NAME) in selected_lang or
                        response_subtitle['lang'] in selected_lang
                    )
                ]
                
            # TV Shows - Filter out non matching season-episode subtitles combination
            if media_type == 'tv':
                season_number = season.zfill(2)
                episode_number = episode.zfill(2)

                response_subtitles_list = [
                    subtitle for subtitle in response_subtitles_list
                    if extract_season_episode_numbers(subtitle['releaseName']) == (season_number, episode_number)
                ]
                
            subsource_subtitle_list = []
            for response_subtitle in response_subtitles_list:
            
                # Check if 'lang' key exists
                if 'lang' not in response_subtitle:
                    continue  # Skip this subtitle if 'lang' key is missing
                
                FullLanguageName = response_subtitle['lang']
                # Attempt language conversion; if it fails, assign the original FullLanguageName
                FullLanguageName = xbmc.convertLanguage(FullLanguageName, xbmc.ENGLISH_NAME) or FullLanguageName
        
                SubRating = response_subtitle.get("rating", '0')
                hearing_impaired = "true" if response_subtitle.get("hi", 0) == 1 else "false"
                subId = response_subtitle['subId']
                
                # Attempt language conversion; Two letter code as defined in ISO 639-1
                thumbnailImageLanguageName = xbmc.convertLanguage(FullLanguageName, xbmc.ISO_639_1)
                
                SubFileName = response_subtitle['releaseName']

                # Define characters that might break the filename (It caused writing problem to MyTmp dir)
                characters_to_remove = '\\/:*?"<>|\''
                # Remove characters that might cause issues in the filename
                SubFileName = ''.join(c for c in SubFileName if c not in characters_to_remove)
            
                download_data={}
                download_data['filename'] = SubFileName
                download_data['subId'] = subId
                download_data['media_type'] = media_type
                download_data['season'] = season
                download_data['episode'] = episode
                download_data['format'] = "zip"
                # Send Hearing Impaired (HI) flag to determine if to clean HI tags or not.
                download_data['hearing_imp'] = hearing_impaired
                
                url = "plugin://%s/?action=download&filename=%s&language=%s&download_data=%s&source=subsource" % (MyScriptID,
                                                                                                    que(SubFileName),
                                                                                                    FullLanguageName,
                                                                                                    que(json.dumps(download_data))
                                                                                                    )

                json_data={'url':url,
                        'label':FullLanguageName,
                        'label2':site_id+' '+SubFileName,
                        'iconImage':str(int(round(float(SubRating)/2))),
                        'thumbnailImage':thumbnailImageLanguageName,
                        'hearing_imp':hearing_impaired,
                        'site_id':site_id,
                        'sub_color':sub_color,
                        'filename':SubFileName,
                        'sync': "false"}

                
                subsource_subtitle_list.append(json_data)
                    
            global_var=subsource_subtitle_list
        else:
            log.warning(f"DEBUG | [SubSource] | SubSource SearchSubtitles | No subs found. response={response}")
            
        
    except Exception as e:
        log.warning(f"DEBUG | [SubSource] | SubSource SearchSubtitles | type: {type(e)} | Exception: {repr(e)}")
        return []


def download(download_data,MySubFolder):
    
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)
    
    subId = download_data['subId']
    format = download_data['format']
    filename = download_data['filename']
    media_type = download_data['media_type']
    season = download_data['season']
    episode = download_data['episode']
    
    subFile = os.path.join(MyTmp, "%s.%s" %(str(filename), format))
    log.warning(f'DEBUG | [SubSource] | Desired subId: {subId} | subFile: {subFile}')

    data = {
        "id": str(subId)
    }
    
    try:
        sub_download_response = requests.post(SUBSOURCE_DOWNLOAD_API_URL, headers=headers, json=data, timeout=DEFAULT_REQUEST_TIMEOUT)
        log.warning(f"DEBUG | [SubSource] | DownloadSubtitles sub_download_response: {sub_download_response.status_code}")
        sub_download_response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)

        with open(subFile, 'wb') as temp_subFile:
            temp_subFile.write(sub_download_response.content)
        sub_file=extract(subFile,MySubFolder)
        return sub_file
        
        # TODO: Season pack support with PTN / GuessIt
        # episode_pattern = None
        # if media_type == 'tv':
            # episode_pattern = re.compile(get_episode_pattern(season, episode), re.IGNORECASE)
            
        # exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass",".idx",".sup"]   
        # for dir in xbmcvfs.listdir(MyTmp)[0]:
            # for file in xbmcvfs.listdir(os.path.join(MyTmp, dir))[1]:
                # if os.path.splitext(file)[1] in exts:

                    # if episode_pattern and not episode_pattern.search(file):
                        # continue
                   
                    # sub_file=(os.path.join(MyTmp, dir, file))

        # for file in xbmcvfs.listdir(MyTmp)[1]:
            # if os.path.splitext(file)[1] in exts:
               
                # if episode_pattern and not episode_pattern.search(file):
                    # continue
                
                # sub_file=(os.path.join(MyTmp, file))
                
    except Exception as e:
        log.warning(f'DEBUG | [SubSource] | DownloadSubtitles | type: {type(e)} | Exception: {repr(e)}')