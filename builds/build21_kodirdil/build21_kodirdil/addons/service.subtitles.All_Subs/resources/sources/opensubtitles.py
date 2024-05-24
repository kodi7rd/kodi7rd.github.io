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
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_open'))

########### Settings ####################
# Retrieve OS_USER_API_KEY_VALUE from settings
OS_USER_API_KEY_VALUE = Addon.getSetting("OS_USER_API_KEY_VALUE")
# Check if OS_USER_API_KEY_VALUE is not empty
USE_OS_USER_API_KEY = bool(OS_USER_API_KEY_VALUE)
#########################################

########### Constants ###################
OPS_API_BASE_URL = u"https://api.opensubtitles.com/api/v1"
# OPS_API_LOGIN_URL = f"{OPS_API_BASE_URL}/login"
OPS_API_SEARCH_URL = f"{OPS_API_BASE_URL}/subtitles"
OPS_API_DOWNLOAD_URL = f"{OPS_API_BASE_URL}/download"
site_id='[OpenSubtitles]'
sub_color='orange'
#########################################

###### Requests Params ##############
REQUEST_TIMEOUT_IN_SECONDS = 5
REQUEST_MAX_RETRIES_NUMBER = 8
REQUEST_RETRY_DELAY_IN_MS = 500
#########################################

def searchsubtitles(video_data):

    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()

    # New OpenSubtitles.com API Search docs:
    # https://opensubtitles.stoplight.io/docs/opensubtitles-api/a172317bd5ccc-search-for-subtitles
    

    title = video_data.get('OriginalTitle', '')
    season = video_data.get('season', '')
    episode = video_data.get('episode', '')
    year = video_data.get('year', '')
    imdb_id = video_data.get('imdb', '')
    media_type = video_data.get('media_type', '')
    
    lang=[]

    # Language codes from: https://opensubtitles.stoplight.io/docs/opensubtitles-api/1de776d20e873-languages
    if Addon.getSetting("language_hebrew")=='true':
        lang.append('he')
    if Addon.getSetting("language_english")=='true':
        lang.append('en')
    if Addon.getSetting("language_russian")=='true':
        lang.append('ru')
    if Addon.getSetting("language_arab")=='true':
        lang.append('ar')
    if len(Addon.getSetting("other_lang"))>0:
        all_lang=Addon.getSetting("other_lang").split(",")
        for items in all_lang:
            lang.append(str(items))
    # If 'all_lang' is enabled - override lang to 'ALL' only (required 'ALL' only in new API)
    if Addon.getSetting("all_lang")=='true':
        lang = ['ALL']
       
    lang_string = ','.join(lang)

    querystring = {}
    querystring['languages'] = lang_string


    # Build querystring WITH imdb_id
    if imdb_id.startswith('tt'):
    
        if media_type == 'tv':
            #################################################
            # Option 1 - TV Shows - by imdb id + season + episode
            #################################################
            querystring['parent_imdb_id'] = imdb_id
            querystring['season_number'] = season
            querystring['episode_number'] = episode
            
        else:
            #################################################
            # Option 2 - Movies - by imdb id
            #################################################
            querystring['imdb_id'] = imdb_id

    # Build querystring WITHOUT imdb_id
    else:
        querystring['query'] = title
        
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


    #################################################
    # Overwritten API default value:
    querystring['hearing_impaired'] = "include"
    # Default API values:
    querystring['ai_translated'] = "include" 
    querystring['foreign_parts_only'] = "include"
    querystring['machine_translated'] = "exclude"
    #################################################
    
    # Determine which API key to use for Search
    if USE_OS_USER_API_KEY:
        OS_API_KEY_NAME = "User_Setting_API_Key"
        OS_API_KEY_VALUE = OS_USER_API_KEY_VALUE  # Use OS_USER_API_KEY_VALUE from settings
    else:
        OS_API_KEY_NAME,OS_API_KEY_VALUE = get_random_key()
        
    log.warning(f"DEBUG | [OpenSubtitles] | Opensubtitles SearchSubtitles OS_API_KEY_NAME={OS_API_KEY_NAME} | OS_API_KEY_VALUE={OS_API_KEY_VALUE}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Api-Key": OS_API_KEY_VALUE
    }


    # Send the first request ONLY to get total_pages count.
    log.warning("DEBUG | [OpenSubtitles] | Opensubtitles SearchSubtitles querystring: " + repr(querystring))
    
    
    for attempt_number in range(REQUEST_MAX_RETRIES_NUMBER):
        try:
            response = requests.get(OPS_API_SEARCH_URL, headers=headers, params=querystring, timeout=REQUEST_TIMEOUT_IN_SECONDS)
            response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)
            response_json = response.json()


            # Total subtitles found count.
            total_subs_count = response_json.get('total_count', 0)
            # Calculate total_pages through total_subs_count (OpenSubtitles API splits the results as 50 per page - not 60 as written in "per_page" JSON response!)
            total_pages = (total_subs_count // 50) + (1 if total_subs_count % 50 > 0 else 0)
            log.warning(f"DEBUG | [OpenSubtitles] | Opensubtitles SearchSubtitles search result: Total subs count: {repr(total_subs_count)} |  Number of pages - {repr(total_pages)}")
            
            # Initialize search_data with the data from page 1 (which might be empty)
            search_data = response_json.get('data', [])

            # Check if there are additional pages to fetch
            if total_pages > 1:
                # Loop through the pages and save all results in search_data
                for _page in range(2, total_pages + 1):
                    querystring['page'] = _page
                    response = requests.get(OPS_API_SEARCH_URL, headers=headers, params=querystring, timeout=REQUEST_TIMEOUT_IN_SECONDS)
                    response_json = response.json()
                    search_data.extend(response_json.get('data', []))
                    xbmc.sleep(100)

            return search_data

        except requests.exceptions.ConnectionError as ce:
            log.warning('DEBUG | [OpenSubtitles] | OpenSubtitles SearchSubtitles connection error: ' + repr(ce))
            if attempt_number < REQUEST_MAX_RETRIES_NUMBER - 1:  # Retry if attempts are left
                log.warning(f"DEBUG | [OpenSubtitles] | OpenSubtitles SearchSubtitles | Retrying... Attempt {attempt_number + 2} of {REQUEST_MAX_RETRIES_NUMBER}")
                continue
            else:
                return [] # Exit the loop if all retries failed
        except Exception as e:
            log.warning('DEBUG | [OpenSubtitles] | OpenSubtitles SearchSubtitles error: ' + repr(e))
            return []
       
       
def get_subs(video_data):
    global global_var
    log.warning('DEBUG | [OpenSubtitles] | Searching Opensubtitles')
    subtitle_list = []
    
    search_data = searchsubtitles(video_data)
    
    if search_data is not None:

        for search_item in search_data:
        
            attributes = search_item.get('attributes', {})
            SubRating = attributes.get("ratings", '0')
            hearing_impaired = "true" if attributes.get("hearing_impaired", False) else "false"
            
            thumbnailImageLanguageName = attributes.get("language")
            if thumbnailImageLanguageName is None:
                # Skip this iteration of the loop if thumbnailImageLanguageName is None
                continue

            # Attempt language conversion; if it fails, assign the original thumbnailImageLanguageName
            FullLanguageName = xbmc.convertLanguage(thumbnailImageLanguageName, xbmc.ENGLISH_NAME) or thumbnailImageLanguageName
            
            try:
                if attributes['files']:
                    # Attempt to access 'file_name' and 'file_id' if 'files' exist and have elements
                    SubFileName = attributes['release'] or attributes['files'][0]['file_name']  # Get 'file_name'
                    file_id = str(attributes['files'][0]['file_id'])  # Get 'file_id' and convert to string
                else:
                    # If 'files' or its elements are missing or empty, proceed to the next search_item
                    continue
            
            except:
                # Handle cases where 'file_name' or 'file_id' are missing or incorrectly structured
                # Go to the next search_item
                continue

            # Define characters that might break the filename (It caused writing problem to MyTmp dir)
            characters_to_remove = '\\/:*?"<>|\''
            # Remove characters that might cause issues in the filename
            SubFileName = ''.join(c for c in SubFileName if c not in characters_to_remove)
        
            # Remove "תרגום אולפנים"
            SubFileName = SubFileName.replace("תרגום אולפנים", "").replace("אולפנים", "").strip()
            
            download_data={}
            download_data['filename']=SubFileName
            download_data['id']=file_id
            download_data['format']="srt"
            
            url = "plugin://%s/?action=download&filename=%s&language=%s&download_data=%s&source=opensubtitles" % (MyScriptID,
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

            
               
            subtitle_list.append(json_data)
            
        global_var=subtitle_list


def download(download_data,MySubFolder):

    # New OpenSubtitles.com API Download docs:
    # https://opensubtitles.stoplight.io/docs/opensubtitles-api/6be7f6ae2d918-download
    
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)
    file_id=download_data['id']
    format=download_data['format']
    filename=download_data['filename']
    
    subFile = os.path.join(MyTmp, "%s.%s" %(str(filename), format))
    log.warning(f'DEBUG | [OpenSubtitles] | Desired sub file_id: {file_id} | subFile: {subFile}')
    
    # Subtitle File ID
    payload = {"file_id": int(file_id), "sub_format": "srt"}

    response = None
    success = False
    
    # Get subtitle download link
    for api_key_attempt_number in range(1, REQUEST_MAX_RETRIES_NUMBER + 1):
    
        # Determine which API key to use for Download
        if USE_OS_USER_API_KEY:
            OS_API_KEY_NAME = "User_Setting_API_Key"
            OS_API_KEY_VALUE = OS_USER_API_KEY_VALUE  # Use OS_USER_API_KEY_VALUE from settings
        else:
            OS_API_KEY_NAME,OS_API_KEY_VALUE = get_random_key()
            
        log.warning(f"DEBUG | [OpenSubtitles] | Opensubtitles DownloadSubtitles | api_key_attempt_number={api_key_attempt_number} | OS_API_KEY_NAME={OS_API_KEY_NAME} | OS_API_KEY_VALUE={OS_API_KEY_VALUE}")

        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Api-Key": OS_API_KEY_VALUE
            # "Authorization": f"Bearer {osdb_token}" # Download works also only with API key, without username/password token authentication, although the API docs. Strange..
        }
        
        retry_number = 1
        while retry_number <= REQUEST_MAX_RETRIES_NUMBER:
            try:
                log.warning(f"DEBUG | [OpenSubtitles] | Opensubtitles DownloadSubtitles | Get sub URL download |  Starting retry_number {retry_number}.")
                log.warning(f"DEBUG | [OpenSubtitles] | Opensubtitles DownloadSubtitles payload: {repr(payload)}")
                response = requests.post(OPS_API_DOWNLOAD_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_IN_SECONDS)
                log.warning(f"DEBUG | [OpenSubtitles] | Opensubtitles DownloadSubtitles response.status_code: {repr(response.status_code)}")
                
                if response.status_code == 503 or response.status_code == 406:
                    break # 503 - Wrong API Key | 406 - max usage quota reached for the API key.
                response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)
                
                response_json = response.json()
                log.warning(f"DEBUG | [OpenSubtitles] | Opensubtitles DownloadSubtitles result: {repr(response_json)}")
                subtitle_download_url = response_json['link']
                success = True # Set flag to break both loops
                break

            except requests.RequestException as req_err:
                if isinstance(req_err, (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError)):
                    log.warning(f"DEBUG | [OpenSubtitles] | OpenSubtitles DownloadSubtitles RequestException error: {repr(req_err)}")
                    if response:
                        log.warning(f"DEBUG | [OpenSubtitles] | OpenSubtitles DownloadSubtitles response.status_code: {response.status_code}")
                    retry_number += 1
                    if retry_number > REQUEST_MAX_RETRIES_NUMBER:
                        raise RuntimeError("Reached maximum retry_number for ReadTimeout or ConnectionError error")
                    xbmc.sleep(REQUEST_RETRY_DELAY_IN_MS)
                else:
                    log.warning('DEBUG | [OpenSubtitles] | OpenSubtitles DownloadSubtitles error: ' + repr(req_err))
                    raise RuntimeError("OpenSubtitles DownloadSubtitles error")
                    
        if success:
            break  # Break the for loop if the flag is set

    if not success:
        log.warning("DEBUG | [OpenSubtitles] | OpenSubtitles DownloadSubtitles error | No success in getting sub URL download from any API key")
        raise RuntimeError(f"OpenSubtitles DownloadSubtitles error | Looped through {REQUEST_MAX_RETRIES_NUMBER} API keys unsucessfully.")
            
    # Download subtitle file
    for attempt_number in range(1, REQUEST_MAX_RETRIES_NUMBER + 1):
        log.warning(f"DEBUG | [OpenSubtitles] | Opensubtitles DownloadSubtitles | Download sub file | Starting attempt_number {attempt_number}.")
        try:
            sub_download_response = requests.get(subtitle_download_url, timeout=REQUEST_TIMEOUT_IN_SECONDS)
            log.warning(f"DEBUG | [OpenSubtitles] | Opensubtitles DownloadSubtitles sub_download_response: {sub_download_response.status_code}")
            sub_download_response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)

            with open(subFile, 'wb') as temp_subFile:
                temp_subFile.write(sub_download_response.content)
            sub_file=extract(subFile,MySubFolder)
            return sub_file

        except requests.HTTPError as http_err:
            if attempt_number < REQUEST_MAX_RETRIES_NUMBER:
                log.warning(f"DEBUG | [OpenSubtitles] | Opensubtitles DownloadSubtitles error: {repr(http_err)} on attempt_number {attempt_number}. Retrying in {REQUEST_RETRY_DELAY_IN_MS} seconds...")
                xbmc.sleep(REQUEST_RETRY_DELAY_IN_MS)
                continue  # Retry the request
            else:
                log.warning('DEBUG | [OpenSubtitles] | OpenSubtitles DownloadSubtitles error: ' + repr(http_err))
                raise RuntimeError("OpenSubtitles DownloadSubtitles HTTPError reached maximum tries.")

def c_get_os_api_keys():    
    OS_API_KEYS = requests.get('https://kodi7rd.github.io/repository/other/DarkSubs_OpenSubtitles/darksubs_opensubtitles_api.json', timeout=REQUEST_TIMEOUT_IN_SECONDS).json()
    return OS_API_KEYS
    
def get_random_key():
    OS_API_KEYS=cache.get(c_get_os_api_keys, 24,table='subs')
    random_key = random.choice(OS_API_KEYS)
    OS_API_KEY_NAME, OS_API_KEY_VALUE = random_key["OS_API_KEY_NAME"], random_key["OS_API_KEY_VALUE"]
    return OS_API_KEY_NAME, OS_API_KEY_VALUE




####################################################################
####################################################################
######################### UNUSED ###################################


# Create an instance of OSDBServer
# osdb_server = OSDBServer()

# Retrieve the osdb_token value using the get_osdb_token() method
# osdb_token = osdb_server.get_osdb_token()
###########################################

# The class is currently UNUSED - was able to Search+Download with API keys authentication ONLY, without username/password authentication.
# class OSDBServer:
    # def __init__( self, *args, **kwargs ):
    
        # self.osdb_token = None
        # self.login_to_osdb()
        

    # def login_to_osdb(self):
        # try:
            # usernameSettings = Addon.getSetting("OSuser")
            # passSettings = Addon.getSetting("OSpass")
            # username = usernameSettings if len(usernameSettings) > 0 else DEFAULT_USERNAME
            # password = passSettings if len(passSettings) > 0 else DEFAULT_PASSWORD
            # username = DEFAULT_USERNAME
            # password = DEFAULT_PASSWORD

            # payload = {
                # "username": username,
                # "password": password
            # }

            # Determine which API key to use
            # if USE_OS_USER_API_KEY:
                # OS_API_KEY_NAME = "User_Setting_API_Key"
                # OS_API_KEY_VALUE = OS_USER_API_KEY_VALUE  # Use OS_USER_API_KEY_VALUE from settings
            # else:
                # OS_API_KEY_NAME,OS_API_KEY_VALUE = get_random_key()
            
            # headers = {
                # "Content-Type": "application/json",
                # "Accept": "application/json",
                # "User-Agent": USER_AGENT,
                # "Api-Key": OS_API_KEY_VALUE
            # }

            # response = requests.post(OPS_API_LOGIN_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_IN_SECONDS)
            # response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)

            # if response.status_code == 200:
                # response_json = response.json()

                # log.warning('DEBUG | [OpenSubtitles] | OpenSubtitles Login: Succeeded')
                # log.warning('DEBUG | [OpenSubtitles] | OpenSubtitles Login: response json - ' + repr(response_json))

                # self.osdb_token = response_json.get('token')
            # else:
                # log.warning('DEBUG | [OpenSubtitles] | OpenSubtitles Login: Failed - status code: ' + repr(response.status_code))
                # error_message = 'Failed with status code: ' + str(response.status_code)
                # notify_for_api_error(error_message, response_json)

        # except Exception as e:
            # log.warning('DEBUG | [OpenSubtitles] | OpenSubtitles Login error: ' + repr(e))

        
    # def get_osdb_token(self):
        # return self.osdb_token
