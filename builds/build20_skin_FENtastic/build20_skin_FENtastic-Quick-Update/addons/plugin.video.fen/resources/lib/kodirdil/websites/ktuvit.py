########### Imports ##################### 
from modules import kodi_utils
import json
import re,requests
#########################################

########### Settings ####################
search_hebrew_subtitles_in_ktuvit = kodi_utils.get_setting('search_hebrew_subtitles_in_ktuvit', 'true') == 'true'
#########################################

########### Constants ###################
KTUVIT_URL = "https://www.ktuvit.me"
DEFAULT_SEASON = 0
DEFAULT_EPISODE = 0
DEFAULT_TITLE = 0
#########################################


def search_hebrew_subtitles(media_metadata):

    """
    Given media_metadata dict with information about the media file,
    returns a list of Hebrew subtitles available on ktuvit.me.

    Args:
    - media_metadata (dict): A dictionary containing metadata of the media file.
        - media_type (str): A string indicating the type of the media file ('movie' or 'tv').
        - title (str): A string representing the title of the media file.
        - season (int): An integer representing the season number of the TV series. Default value is 0.
        - episode (int): An integer representing the episode number of the TV series. Default value is 0.
        - imdb_id (str): A string representing the imdb_id of the media file. Default value is an empty string.
    
    Returns:
    - ktuvit_subtitles_list (list): A list of strings containing the available Hebrew subtitles on ktuvit.me for the media file.
    """

    # if search_hebrew_subtitles_in_ktuvit setting is disabled - Cancel search and return empty subtitles list
    if not search_hebrew_subtitles_in_ktuvit:
        kodi_utils.logger("KODI-RD-IL", f"SETTING search_hebrew_subtitles_in_ktuvit is: {search_hebrew_subtitles_in_ktuvit}. Skipping [KTUVIT] website...")
        return []
        
    media_type = media_metadata.get("media_type")
    title = media_metadata.get("title", DEFAULT_TITLE)
    season = media_metadata.get("season", DEFAULT_SEASON)
    episode = media_metadata.get("episode", DEFAULT_EPISODE)
    imdb_id = media_metadata.get("imdb_id", "")
    kodi_utils.logger("KODI-RD-IL", f"Searching in [KTUVIT]: media_type: {media_type} Title: {title}: Season: {season} Episode: {episode} imdb_id: {imdb_id}")
    
    try:
        # Search for movie/show in Ktuvit search page
        ktuvit_search_response = ktuvit_search_request(title, media_type)
        
        # Get IMDb ID from Ktuvit
        imdb_id_from_ktuvit = get_imdb_id_from_ktuvit(ktuvit_search_response, imdb_id, title)
        
        # Return empty subtitles list if no IMDb ID from Ktuvit found.    
        if imdb_id_from_ktuvit == '':
            return []
        
        ktuvit_referer_url = f"{KTUVIT_URL}/MovieInfo.aspx?ID={imdb_id_from_ktuvit}"

        # Set different API parameters based on media_type (movie / tv)
        ktuvit_search_subtitles_api_url, headers, params = create_headers_params(media_type, ktuvit_referer_url, imdb_id_from_ktuvit, season, episode)
            
        # Get login cookie from Ktuvit
        ktuvit_login_cookie = login_to_ktuvit()

        # Search subtitles in Ktuvit and fetch response
        ktuvit_subtitles_search_response = requests.get(ktuvit_search_subtitles_api_url, headers=headers, params=params, cookies=ktuvit_login_cookie, timeout=5).content
        
        # Extract subtitles list from search response
        ktuvit_subtitles_list = extract_subtitles_list(ktuvit_subtitles_search_response)
        
        return ktuvit_subtitles_list
        
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"An error occurred while searching for subtitles on [KTUVIT]: {str(e)}")
        return []
    
    
def login_to_ktuvit():

    """
    Logs in to ktuvit.me and returns a dictionary of login cookies.

    Returns:
    - ktuvit_login_cookies_dict (dict): A dictionary containing login cookies.
    """
    
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
    email = 'hatzel6969@gmail.com'
    password = 'Jw1n9nPOZRAHw9aVdarvjMph2L85pKGx79oAAFTCsaE='

    # Set login request data
    data = f'{{"request":{{"Email":"{email}","Password":"{password}"}}}}'

    # Send login request and get cookies
    ktuvit_api_response = requests.post(f"{KTUVIT_URL}/Services/MembershipService.svc/Login", headers=headers, data=data, timeout=5).cookies

    # Create dictionary of cookies with names as keys and values as values
    ktuvit_login_cookies_dict = {}
    for cookie in ktuvit_api_response:
        ktuvit_login_cookies_dict[cookie.name] = cookie.value
        
    return ktuvit_login_cookies_dict
    
    
def ktuvit_search_request(title, media_type):

    """
    Sends a request to the Ktuvit search page and returns the search results.

    Args:
    - title (str): A string representing the title of the media file.
    - media_type (str): A string indicating the type of the media file ('movie' or 'tv').
    
    Returns:
    - ktuvit_search_response (dict): A dictionary containing the search results.
    """
    
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
            "SearchType": '0' if media_type == 'movie' else '1',
            "WithSubsOnly": False
        }
    }
    
    return requests.post(f"{KTUVIT_URL}/Services/ContentProvider.svc/SearchPage_search", headers=headers, json=data, timeout=5).json()


def get_imdb_id_from_ktuvit(ktuvit_search_response, imdb_id, title):

    """
    Parses the Ktuvit search results and returns the IMDb ID of the media file.

    Args:
    - ktuvit_search_response (dict): A dictionary containing the search results.
    - imdb_id (str): A string representing the IMDb ID of the media file.
    - title (str): A string representing the title of the media file.

    Returns:
    - imdb_id_from_ktuvit (str): A string representing the IMDb ID of the media file as found on Ktuvit.
    """

    ktuvit_search_page_results = json.loads(ktuvit_search_response['d'])['Films']
    imdb_id_from_ktuvit = ''

    if imdb_id:
        for result in ktuvit_search_page_results:
            if imdb_id == result['ImdbID']:
                imdb_id_from_ktuvit = result['ID']
                break

    if imdb_id_from_ktuvit == '':
        regex_helper = re.compile('\W+', re.UNICODE)
        title = regex_helper.sub('', title).lower()
        for result in ktuvit_search_page_results:
        
            eng_name = regex_helper.sub('', regex_helper.sub(' ', result['EngName'])).lower()
            heb_name = regex_helper.sub('', result['HebName'])
            
            if (title.startswith(eng_name) or eng_name.startswith(title) or
                    title.startswith(heb_name) or heb_name.startswith(title)):
                imdb_id_from_ktuvit = result["ID"]
    
    return imdb_id_from_ktuvit


def create_headers_params(media_type, ktuvit_referer_url, imdb_id_from_ktuvit, season, episode):

    """
    Creates the headers and parameters for the API request to search for subtitles.

    Args:
    - media_type (str): A string indicating the type of the media file ('movie' or 'tv').
    - ktuvit_referer_url (str): A string representing the referer URL for the API request.
    - imdb_id_from_ktuvit (str): A string representing the IMDb ID of the media file as found on Ktuvit.
    - season (int): An integer representing the season number of the media file.
    - episode (int): An integer representing the episode number of the media file.

    Returns:
    - ktuvit_search_subtitles_api_url (str): A string representing the API endpoint for searching for subtitles.
    - headers (dict): A dictionary containing the headers for the API request.
    - params (tuple): A tuple containing the parameters for the API request.
    """

    if media_type == 'movie':
    
        ktuvit_search_subtitles_api_url = f"{KTUVIT_URL}/MovieInfo.aspx"
        
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
            'referer': ktuvit_referer_url,
            'accept-language': 'en-US,en;q=0.9',
        }

        params = (
            ('ID', imdb_id_from_ktuvit),
        )
        
    else:
    
        ktuvit_search_subtitles_api_url = f"{KTUVIT_URL}/Services/GetModuleAjax.ashx"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': ktuvit_referer_url,
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers',
        }

        params = (
            ('moduleName', 'SubtitlesList'),
            ('SeriesID', imdb_id_from_ktuvit),
            ('Season', season),
            ('Episode', episode),
        )
    
    return ktuvit_search_subtitles_api_url, headers, params


def extract_subtitles_list(ktuvit_subtitles_search_response):

    """
    Extracts the subtitles list from the Ktuvit API response.

    Args:
    - ktuvit_subtitles_search_response (bytes): A bytes object representing the API response.

    Returns:
    - ktuvit_subtitles_list (list): A list of strings representing the available subtitles for the media file.
    """
        
    # Extract table rows from HTML response
    table_row_regex = '<tr>(.+?)</tr>'
    table_rows = re.compile(table_row_regex, re.DOTALL).findall(ktuvit_subtitles_search_response.decode('utf-8'))
   
    # Intialize empty ktuvit_subtitles_list
    ktuvit_subtitles_list = []
    
    # Extract title and subtitle from each table row
    for table_row in table_rows:
        title_subtitle_regex = '<div style="float.+?>(.+?)<br />.+?data-subtitle-id="(.+?)"'
        title_subtitle = re.compile(title_subtitle_regex,re.DOTALL).findall(table_row)
        
        # Skip if title and subtitle not found
        if len(title_subtitle)==0:
            continue
    
        # Extract title from title and subtitle
        title_subtitle = title_subtitle[0][0]
            
        # burekas fix for KT titles
        if ('i class' in title_subtitle):
            burekas_title_regex = 'כתובית מתוקנת\'></i>(.+?)$'
            burekas_title = re.compile(burekas_title_regex, re.DOTALL).findall(title_subtitle)
            title_subtitle = burekas_title[0].replace('\n','').replace('\r','').replace('\t','').replace(' ','')
        else:
            title_subtitle = title_subtitle.replace('\n','').replace('\r','').replace('\t','').replace(' ','')
            
        ktuvit_subtitles_list.append(title_subtitle)
    
    return ktuvit_subtitles_list