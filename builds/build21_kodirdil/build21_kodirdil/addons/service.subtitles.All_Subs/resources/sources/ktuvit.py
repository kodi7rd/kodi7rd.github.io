# Import necessary libraries
import xbmcaddon,xbmcvfs,os,xbmc
global global_var,site_id,sub_color#global
global_var=[]
from resources.modules import log
import requests,json,re,shutil
from resources.modules import cache
from resources.modules.extract_sub import extract
import urllib.parse
from resources.modules.general import DEFAULT_REQUEST_TIMEOUT
#########################################


Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
que=urllib.parse.quote_plus
xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_ktuvit'))

########### Constants ###################
KTUVIT_URL = "https://www.ktuvit.me"
LOGIN_URL = f"{KTUVIT_URL}/Services/MembershipService.svc/Login"
SEARCH_URL = f"{KTUVIT_URL}/Services/ContentProvider.svc/SearchPage_search"
MOVIE_INFO_URL = f"{KTUVIT_URL}/MovieInfo.aspx"
EPISODE_INFO_URL = f"{KTUVIT_URL}/Services/GetModuleAjax.ashx?"
REQUEST_DOWNLOAD_IDENTIFIER_URL = f"{KTUVIT_URL}/Services/ContentProvider.svc/RequestSubtitleDownload"
DOWNLOAD_SUB_URL = f"{KTUVIT_URL}/Services/DownloadFile.ashx"
site_id='[Ktuvit]'
sub_color='springgreen'
#########################################
    
    
def get_subs(video_data):

    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    
    global global_var
    log.warning('DEBUG | [KTUVIT] | Searching Ktuvit')
        
    media_type = video_data["media_type"]
    title = video_data["OriginalTitle"]
    season = video_data["season"]
    episode = video_data["episode"]
    imdb_id = video_data["imdb"]
        
    ################ KTUVIT TITLE MISMATCH MAPPING ##############################
    title = get_matching_ktuvit_name(title)
    log.warning(f"DEBUG | [KTUVIT] | get_matching_ktuvit_name | title after mapping: {title}")
    #############################################################################
    
    
    #############################################################################
    # STEP 1: Search for movie/show in Ktuvit search page
    ktuvit_search_page_results = search_title_in_ktuvit(title, media_type)
    
    if not ktuvit_search_page_results:
    
        # IF NO RESULTS FOR TV SHOW's OriginalTitle - RE-SEARCH BY TVShowTitle
        if media_type == 'tv' and video_data.get("TVShowTitle") and title != video_data.get("TVShowTitle"):
            title = video_data["TVShowTitle"]
            log.warning(f"DEBUG | [KTUVIT] | Re-searching TV Show title | title={title}")
            ktuvit_search_page_results = search_title_in_ktuvit(title, media_type)
            
        # IF NO RESULTS FOR MOVIE's OriginalTitle - RE-SEARCH BY title
        elif media_type == 'movie' and video_data.get("title") and title != video_data.get("title"):
            title = video_data["title"]
            log.warning(f"DEBUG | [KTUVIT] | Re-searching Movie title | title={title}")
            ktuvit_search_page_results = search_title_in_ktuvit(title, media_type)

        else:
            log.warning(f"DEBUG | [KTUVIT] | ktuvit_search_page_results is empty | Skipping re-search.")

    else:
        log.warning(f"DEBUG | [KTUVIT] | ktuvit_search_page_results is not empty | Skipping re-search.")
    #############################################################################
    
    
    #############################################################################
    # STEP 2: Get matching Ktuvit ID from search results
    Ktuvit_Page_ID = get_Ktuvit_Page_ID(ktuvit_search_page_results, imdb_id, title)
    log.warning(f"DEBUG | [KTUVIT] | Ktuvit_Page_ID: {Ktuvit_Page_ID}")
        
    # Return empty subtitles list if no Ktuvit ID found.
    if Ktuvit_Page_ID == '':
        return []
    #############################################################################


    #############################################################################
    # STEP 3: Get login cookie from Ktuvit
    ktuvit_login_cookie = cache.get(login_to_ktuvit,1, table='subs')
    #############################################################################


    #############################################################################
    # STEP 4: Search for subtitles using Ktuvit ID and video_data params
    ktuvit_subtitles_search_response = search_subtitles_in_ktuvit(ktuvit_login_cookie, media_type, Ktuvit_Page_ID, season, episode)
    #############################################################################


    #############################################################################
    # STEP 5: Extract subtitles list from search response and build subtitles list
    ktuvit_subtitles_list = extract_subtitles_list_and_build_subtitles_list(ktuvit_subtitles_search_response, Ktuvit_Page_ID)
    #############################################################################
        
    global_var = ktuvit_subtitles_list


def login_to_ktuvit():
    
    # Set the request headers  
    headers = {
    'authority': 'www.ktuvit.me',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'content-type': 'application/json',
    'origin': KTUVIT_URL,
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9',
    }

    # Set email and password
    email = 'darksubsil1@gmail.com'
    password = 'ZkCyMZfsIHt9HQK4eL8bbfaxXoNBjmFO9w39kt/gA14='

    # Set login request data
    data = f'{{"request":{{"Email":"{email}","Password":"{password}"}}}}'

    # Send login request and get cookies
    ktuvit_api_response = requests.post(LOGIN_URL, headers=headers, data=data, timeout=DEFAULT_REQUEST_TIMEOUT).cookies

    # Create dictionary of cookies with names as keys and values as values
    ktuvit_login_cookies_dict = {}
    for cookie in ktuvit_api_response:
        ktuvit_login_cookies_dict[cookie.name] = cookie.value
        
    return ktuvit_login_cookies_dict


def search_title_in_ktuvit(title, media_type):
    
    headers = {
        'authority': 'www.ktuvit.me',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'content-type': 'application/json',
        'origin': KTUVIT_URL,
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'{KTUVIT_URL}/Search.aspx',
        'accept-language': 'en-US,en;q=0.9',
        
    }
    
    SearchTypeParam = '0' if media_type == 'movie' else '1'
    WithSubsOnlyParam = True if media_type == 'movie' else False

    data = {
        "request": {
            "FilmName": title,
            "Actors": [],
            "Studios": None,
            "Directors": [],
            "Genres": [],
            "Countries": [],
            "Languages": [],
            "Year": "",
            "Rating": [],
            "Page": 1,
            "SearchType": SearchTypeParam,
            "WithSubsOnly": WithSubsOnlyParam
        }
    }

    try:
        ktuvit_search_response = requests.post(SEARCH_URL, headers=headers, json=data, timeout=DEFAULT_REQUEST_TIMEOUT).json()
        ktuvit_search_page_results = json.loads(ktuvit_search_response['d'])['Films']
        return ktuvit_search_page_results
    except Exception as e:
        log.warning(f"DEBUG | [KTUVIT] | search_title_in_ktuvit | Exception: {str(e)}")
        return []

def extract_imdb_id_from_result(result):

    # Extract the IMDb ID from the IMDb link, Remove trailing slash if it exists
    imdb_link_from_ktuvit = str(result.get('IMDB_Link', '')).rstrip("/")
    # Split the URL by "/", Get the last part of the URL, which should be the IMDb ID (tt123456)
    imdb_parts = imdb_link_from_ktuvit.split("/")
    imdb_id_from_ktuvit = imdb_parts[-1] if imdb_parts else ''
            
    # FALLBACK - Check if imdb_id_from_ktuvit doesn't start with "tt"
    if not imdb_id_from_ktuvit.startswith("tt"):
        imdb_id_from_ktuvit = str(result.get('ImdbID', ''))
        log.warning(f"DEBUG | [KTUVIT] | FALLBACK | KTUVIT IMDB ID (fallback): {imdb_id_from_ktuvit}")
        
    return imdb_id_from_ktuvit

def get_Ktuvit_Page_ID(ktuvit_search_page_results, imdb_id, title):

    Ktuvit_Page_ID = ''

    if imdb_id.startswith("tt"):
        for result in ktuvit_search_page_results:
            imdb_id_from_ktuvit = extract_imdb_id_from_result(result)
            if imdb_id_from_ktuvit in imdb_id:
                log.warning(f"DEBUG | [KTUVIT] | MATCH | video_data imdb_id: {imdb_id} | Ktuvit imdb_id: {imdb_id_from_ktuvit}")
                Ktuvit_Page_ID = result['ID']
                break

    # if Ktuvit_Page_ID still empty (wrong imdb on ktuvit page) - search for match by title eng/heb names
    # if Ktuvit_Page_ID == '':
        # regex_helper = re.compile('\W+', re.UNICODE)
        # title = regex_helper.sub('', title).lower()
        
        # for result in ktuvit_search_page_results:
            # eng_name = regex_helper.sub('', regex_helper.sub(' ', result['EngName'])).lower()
            # heb_name = regex_helper.sub('', result['HebName'])
            # if (title.startswith(eng_name) or eng_name.startswith(title) or
                    # title.startswith(heb_name) or heb_name.startswith(title)):
                # log.warning(f"DEBUG | [KTUVIT] | REGEX MATCH | title: {title}: | eng_name: {eng_name} | heb_name: {heb_name}")
                # Ktuvit_Page_ID = result["ID"]
                # break
    
    return Ktuvit_Page_ID


def search_subtitles_in_ktuvit(ktuvit_login_cookie, media_type, Ktuvit_Page_ID, season, episode):
        
    KTUVIT_REFERER_URL = f"{MOVIE_INFO_URL}?ID={Ktuvit_Page_ID}"

    params = {}
    
    if media_type == 'movie':
        headers = {
            'authority': 'www.ktuvit.me',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': KTUVIT_REFERER_URL,
            'accept-language': 'en-US,en;q=0.9',
        }
        
    else:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': KTUVIT_REFERER_URL,
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers',
        }
        
        params['moduleName'] = 'SubtitlesList'
        params['SeriesID'] = Ktuvit_Page_ID
        params['Season'] = season.zfill(2)
        params['Episode'] = episode.zfill(2)

    # Search subtitles in Ktuvit and fetch response
    ktuvit_search_subtitles_request_url = f"{MOVIE_INFO_URL}?ID={Ktuvit_Page_ID}" if media_type == 'movie' else EPISODE_INFO_URL
    ktuvit_subtitles_search_response = requests.get(ktuvit_search_subtitles_request_url, headers=headers, params=params, cookies=ktuvit_login_cookie, timeout=DEFAULT_REQUEST_TIMEOUT).content
    log.warning(f"DEBUG | [KTUVIT] | ktuvit_search_subtitles_request_url={ktuvit_search_subtitles_request_url} | params={params}")
    
    return ktuvit_subtitles_search_response
        
    
def extract_subtitles_list_and_build_subtitles_list(ktuvit_subtitles_search_response, Ktuvit_Page_ID):
   
    # Intialize empty ktuvit_subtitles_list
    ktuvit_subtitles_list = []

    # Extract table rows from HTML response
    table_row_regex = '<tr>(.+?)</tr>'
    table_rows = re.compile(table_row_regex, re.DOTALL).findall(ktuvit_subtitles_search_response.decode('utf-8'))
    
    # Extract title and subtitle from each table row
    for table_row in table_rows:
        subtitle_row_regex = '<div style="float.+?>(.+?)<br />.+?data-subtitle-id="(.+?)"'
        extracted_subtitle_row = re.compile(subtitle_row_regex,re.DOTALL).findall(table_row)
        
        # Skip if extracted_subtitle_row is empty
        if len(extracted_subtitle_row) == 0:
            continue
    
        # Extract subtitle name and ID
        extracted_subtitle_name = extracted_subtitle_row[0][0]
        extracted_subtitle_ID = extracted_subtitle_row[0][1]
            
        # burekas fix for KT titles
        if ('i class' in extracted_subtitle_name):
            burekas_title_regex = 'כתובית מתוקנת\'></i>(.+?)$'
            burekas_title = re.compile(burekas_title_regex,re.DOTALL).findall(extracted_subtitle_name)
            extracted_subtitle_name = burekas_title[0]

        extracted_subtitle_name = extracted_subtitle_name.strip().replace('\n','').replace('\r','').replace('\t','').replace(' ','.')

        # Define characters that might break the filename (It caused writing problem to MyTmp dir)
        characters_to_remove = '\\/:*?"<>|\''
        # Remove characters that might cause issues in the filename
        extracted_subtitle_name = ''.join(c for c in extracted_subtitle_name if c not in characters_to_remove)
        
        download_data={}
        download_data['Ktuvit_Page_ID'] = Ktuvit_Page_ID
        download_data['subtitle_download_data'] = '{{"request":{{"FilmID":"{}","SubtitleID":"{}","FontSize":0,"FontColor":"","PredefinedLayout":-1}}}}'.format(Ktuvit_Page_ID, extracted_subtitle_ID)

        
        url = "plugin://%s/?action=download&filename=%s&download_data=%s&source=ktuvit&language=Hebrew" % (MyScriptID,que(extracted_subtitle_name),que(json.dumps(download_data)))
 
        json_data={'url':url,
                         'label':"Hebrew",
                         'label2':site_id+' '+extracted_subtitle_name,
                         'iconImage':"0",
                         'thumbnailImage':"he",
                         'hearing_imp':'false',
                         'site_id':site_id,
                         'sub_color':sub_color,
                         'filename':extracted_subtitle_name,
                         'sync': 'false'}
  

        ktuvit_subtitles_list.append(json_data)
        
    return ktuvit_subtitles_list


def download(download_data,MySubFolder):
    
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)

    log.warning(f"DEBUG | [KTUVIT] | download_data={download_data}")
    
    # Get login cookie from Ktuvit
    ktuvit_login_cookie = cache.get(login_to_ktuvit,1, table='subs')
    
    # Set up params from download_data
    Ktuvit_Page_ID = download_data['Ktuvit_Page_ID']
    data = download_data['subtitle_download_data']
    
    subtitle_download_result = "הבקשה לא נמצאה, נא לנסות להוריד את הקובץ בשנית"

    # Attempt subtitle download
    count = 0
    KTUVIT_REFERER_URL = f"{MOVIE_INFO_URL}?ID={Ktuvit_Page_ID}"
    while ("הבקשה לא נמצאה, נא לנסות להוריד את הקובץ בשנית" in subtitle_download_result):
    
        count += 1
        log.warning(f"DEBUG | [KTUVIT] | Number of try: {count} | Sending RequestSubtitleDownload request...")
        
        # Set headers for subtitle download request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': KTUVIT_URL,
            'Connection': 'keep-alive',
            'Referer': KTUVIT_REFERER_URL,
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers',
            }
        
        # Send subtitle download request
        post_response = requests.post(REQUEST_DOWNLOAD_IDENTIFIER_URL, headers=headers, data=data, cookies=ktuvit_login_cookie, timeout=DEFAULT_REQUEST_TIMEOUT).json()
        
        # Extract DownloadIdentifier from response
        DownloadIdentifier = json.loads(post_response['d'])['DownloadIdentifier']
        log.warning(f"DEBUG | [KTUVIT] | Number of try: {count} | RequestSubtitleDownload DownloadIdentifier: {DownloadIdentifier}")
        
        # Set headers for file download
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Referer': KTUVIT_REFERER_URL,
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers',
            }
            
        # Set parameters for file download
        params = {'DownloadIdentifier': str(DownloadIdentifier)}

        # Send file download request
    
        log.warning(f"DEBUG | [KTUVIT] | Number of try: {count} | Sending DownloadFile request...")
        response = requests.get(DOWNLOAD_SUB_URL, headers=headers, params=params, cookies=ktuvit_login_cookie, timeout=DEFAULT_REQUEST_TIMEOUT)
        # Throw an error for bad status codes
        response.raise_for_status()
       
        xbmc.sleep(100)
        subtitle_download_result = response.text

        # Break the loop if the maximum number of tries is reached
        if (count > 10):
            log.warning(f"DEBUG | [KTUVIT] | Number of try: {count} | Reached max tries count. breaking...")
            break
            
    log.warning(f"DEBUG | [KTUVIT] | Number of try: {count} | While loop finished.")
    
    # Extract subtitle file name from download response headers
    subtitle_file_name = response.headers['Content-Disposition'].split("filename=")[1]
    log.warning(f"DEBUG | [KTUVIT] | Number of try: {count} | filename: {subtitle_file_name}")

    # Construct path for the archive file
    archive_file = os.path.join(MyTmp, subtitle_file_name)
   
    with open(archive_file, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)
            
    log.warning(archive_file)
    
    sub_file = extract(archive_file,MySubFolder)
    log.warning(sub_file)
    
    return sub_file


################ KTUVIT TITLE MISMATCH MAPPING ##############################
def c_get_ktuvit_original_title_mapping():
    ktuvit_original_title_mapping = requests.get('https://kodi7rd.github.io/repository/other/DarkSubs_Ktuvit_Title_Mapping/darksubs_ktuvit_title_mapping.json', timeout=DEFAULT_REQUEST_TIMEOUT).json()
    return ktuvit_original_title_mapping

def get_matching_ktuvit_name(video_data_original_title):
    try:
        ktuvit_original_title_mapping = cache.get(c_get_ktuvit_original_title_mapping, 24,table='subs')
        return ktuvit_original_title_mapping.get(video_data_original_title, video_data_original_title).lower()
    except Exception as e:
        log.warning(f"DEBUG | [KTUVIT] | get_matching_ktuvit_name | Exception: {str(e)}")
        return video_data_original_title
        pass
#############################################################################
