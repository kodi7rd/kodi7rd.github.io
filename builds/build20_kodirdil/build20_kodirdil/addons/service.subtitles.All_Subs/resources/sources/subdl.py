# Import necessary libraries
import random
import shutil
import xbmcaddon,os,xbmc
global global_var,site_id,sub_color#global
global_var=[]
from resources.modules import log
import requests,json
import urllib
from resources.modules.extract_sub import extract
from resources.modules.general import notify
from resources.modules import cache
import xbmcvfs
import struct
#########################################

que=urllib.parse.quote_plus
Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
MyAddonName = Addon.getAddonInfo('name')
MyAddonVersion    = Addon.getAddonInfo('version') # Module version
USER_AGENT = '%s v%s' %(MyAddonName, MyAddonVersion)
xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_subdl'))

########### Settings ####################
# Retrieve SUBDL_USER_API_KEY_VALUE from settings
SUBDL_USER_API_KEY_VALUE = Addon.getSetting("SUBDL_USER_API_KEY_VALUE")
# Check if SUBDL_USER_API_KEY_VALUE is not empty
USE_SUBDL_USER_API_KEY = bool(SUBDL_USER_API_KEY_VALUE)
#########################################

########### Constants ###################
SUBDL_API_SEARCH_URL = "https://api.subdl.com/api/v1/subtitles"
SUBDL_API_DOWNLOAD_URL = "https://dl.subdl.com"
site_id='[SubDL]'
sub_color='plum'
#########################################

###### Requests Params ##############
REQUEST_TIMEOUT_IN_SECONDS = 5
#########################################

def search_subtitles(item):

    # SubDL API Search docs:
    # https://subdl.com/api-doc

    title = item.get('OriginalTitle', '')
    media_type = item.get('media_type', '')
    season = item.get('season', '')
    episode = item.get('episode', '')
    year = item.get('year', '')
    imdb_id = item.get('imdb', '')
    
    #############################################################################
    from resources.modules.general import remove_year_from_title
    title = remove_year_from_title(title)
    #############################################################################
    
    #####################################################################################################################################
    # API is in beta version. due to limitations - for start - search only for Hebrew + English languages (In the future - all languages)
    #####################################################################################################################################
    lang=[]
    # Language codes from: https://subdl.com/api-files/language_list.json
    if Addon.getSetting("language_hebrew")=='true':
        lang.append('he')
    if Addon.getSetting("language_english")=='true':
        lang.append('en')
    # if Addon.getSetting("language_russian")=='true':
        # lang.append('ru')
    # if Addon.getSetting("language_arab")=='true':
        # lang.append('ar')
    # if len(Addon.getSetting("other_lang"))>0:
        # all_lang=Addon.getSetting("other_lang").split(",")
        # for items in all_lang:
            # lang.append(str(items))
    # If 'all_lang' is enabled - override lang to 'ALL' only (required 'ALL' only in new API)
    if Addon.getSetting("all_lang")=='true':
        lang = ['he','en']
        # lang = ['ALL']
       
    # lang_string = ','.join(lang)

    querystring = {}
    
    # Determine which API key to use for Search
    if USE_SUBDL_USER_API_KEY:
        SUBDL_API_KEY_NAME = "User_Setting_API_Key"
        SUBDL_API_KEY_VALUE = SUBDL_USER_API_KEY_VALUE  # Use SUBDL_USER_API_KEY_VALUE from settings
    else:
        SUBDL_API_KEY_NAME, SUBDL_API_KEY_VALUE = get_random_key()
        
    querystring['api_key'] = SUBDL_API_KEY_VALUE
    log.warning(f"DEBUG | SubDL | SubDL SearchSubtitles SUBDL_API_KEY_NAME={SUBDL_API_KEY_NAME} | SUBDL_API_KEY_VALUE={SUBDL_API_KEY_VALUE}")
    
    # FROM API DOCS: `subs_per_page` (optional): limit of subtitles will see in the results default is 10, (max can be 30)
    querystring['subs_per_page'] = 30
    
    querystring['type'] = media_type # 'movie' or 'tv'
    
    # querystring['languages'] = lang_string

    # Build querystring WITH imdb_id
    if imdb_id.startswith('tt'):
    
        if media_type == 'tv':
            #################################################
            # Option 1 - TV Shows - by imdb id + season + episode
            #################################################
            querystring['imdb_id'] = imdb_id
            querystring['season_number'] = season
            querystring['episode_number'] = episode
            
        else:
            #################################################
            # Option 2 - Movies - by imdb id
            #################################################
            querystring['imdb_id'] = imdb_id

    # Build querystring WITHOUT imdb_id
    else:
        querystring['film_name'] = title
        
        if media_type == 'tv':
            #################################################
            # Option 3 - TV Shows - by title + season + episode
            #################################################
            querystring['season_number'] = season
            querystring['episode_number'] = episode
            
        else:
            #################################################
            # Option 4 - Movies - by title + year
            #################################################
            querystring['year'] = year
    
    log.warning(f"DEBUG | SubDL | SubDL SearchSubtitles final querystring: {str(querystring)}")
    response_subtitles_list = []
    for language in lang:
        try:
            querystring['languages'] = language
            response = requests.get(SUBDL_API_SEARCH_URL, params=querystring, timeout=REQUEST_TIMEOUT_IN_SECONDS)
            response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)
            response_json = response.json()
            log.warning(f"DEBUG | SubDL | SubDL SearchSubtitles | Status Code: {response.status_code} | response_json={response_json}")
            
            response_text_status = response_json.get('status', False)
            log.warning(f"DEBUG | SubDL | SubDL SearchSubtitles | response_text_status={response_text_status}")
            if not response_text_status:
                continue
        
            subtitles_count = len(response_json['subtitles'])
            log.warning(f"DEBUG | SubDL | SubDL SearchSubtitles | searching language '{language}' | Count found: {subtitles_count}")
            
            response_subtitles_list.extend(response_json['subtitles'])
            xbmc.sleep(300)
        except Exception as e:
            log.warning(f'DEBUG | SubDL | SubDL SearchSubtitles | type: {type(e)} | Exception: {repr(e)}')
    return response_subtitles_list
       
def get_subs(item):
    global global_var
    log.warning('DEBUG | SubDL | Searching SubDL')
    subtitle_list = []
    response_subtitles_list = search_subtitles(item)
    
    if response_subtitles_list is not None:

        url_list=[]
        for response_subtitle in response_subtitles_list:
        
            SubRating = '0'
            hearing_impaired = "false"
            
            SubFileName = response_subtitle['release_name']
            file_id = response_subtitle['url']
            
            FullLanguageName = response_subtitle['lang'].capitalize()
            # Attempt language conversion; if it fails, assign the original FullLanguageName
            FullLanguageName = xbmc.convertLanguage(FullLanguageName, xbmc.ENGLISH_NAME) or FullLanguageName
            
            # Attempt language conversion; Two letter code as defined in ISO 639-1
            thumbnailImageLanguageName = xbmc.convertLanguage(FullLanguageName, xbmc.ISO_639_1)

            # Define characters that might break the filename (It caused writing problem to MyTmp dir)
            characters_to_remove = '\\/:*?"<>|'
            # Remove characters that might cause issues in the filename
            SubFileName = ''.join(c for c in SubFileName if c not in characters_to_remove)
            
            download_data={}
            download_data['filename']=SubFileName
            download_data['id']=file_id
            download_data['format']="zip"
            
            url = "plugin://%s/?action=download&filename=%s&language=%s&download_data=%s&source=subdl" % (MyScriptID,
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

            
            if url not in url_list:
               
                url_list.append(url)
                subtitle_list.append(json_data)
    global_var=subtitle_list


def download(download_data,MySubFolder):
    
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)
    file_id=download_data['id']
    format=download_data['format']
    filename=download_data['filename']
    
    subFile = os.path.join(MyTmp, "%s.%s" %(str(filename), format))
    log.warning(f'DEBUG | SubDL | Desired sub file_id: {file_id} | subFile: {subFile}')
    
    # Example: https://dl.subdl.com/subtitle/3197651-3213944.zip
    subtitle_download_url = f"{SUBDL_API_DOWNLOAD_URL}{file_id}"
        
    try:
        sub_download_response = requests.get(subtitle_download_url)
        log.warning(f"DEBUG | SubDL | SubDL DownloadSubtitles sub_download_response: {sub_download_response.status_code}")
        sub_download_response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)

        with open(subFile, 'wb') as temp_subFile:
            temp_subFile.write(sub_download_response.content)
        sub_file=extract(subFile,MySubFolder)
        return sub_file
    except Exception as e:
        log.warning(f'DEBUG | SubDL | SubDL DownloadSubtitles | type: {type(e)} | Exception: {repr(e)}')

def c_get_subdl_api_keys():    
    SUBDL_API_KEYS = requests.get('https://kodi7rd.github.io/repository/other/DarkSubs_SubDL/darksubs_subdl_api.json').json()
    return SUBDL_API_KEYS
    
def get_random_key():
    SUBDL_API_KEYS=cache.get(c_get_subdl_api_keys, 24,table='subs')
    random_key_index = random.randint(0, len(SUBDL_API_KEYS) - 1)
    SUBDL_API_KEY_NAME, SUBDL_API_KEY_VALUE =  SUBDL_API_KEYS[random_key_index]['SUBDL_API_KEY_NAME'],SUBDL_API_KEYS[random_key_index]['SUBDL_API_KEY_VALUE']
    return SUBDL_API_KEY_NAME, SUBDL_API_KEY_VALUE