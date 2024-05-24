# Import necessary libraries
import xbmc, xbmcaddon
import random
import requests
import json
from modules import kodi_utils
#########################################

########### Settings ####################
search_hebrew_subtitles_in_opensubtitles = kodi_utils.get_setting('search_hebrew_subtitles_in_opensubtitles', 'true') == 'true'

########### Constants ###################
AddonName = xbmcaddon.Addon().getAddonInfo('name')
AddonVersion = xbmcaddon.Addon().getAddonInfo('version')
USER_AGENT = f'{AddonName} v{str(AddonVersion)}'

OPS_API_BASE_URL = u"https://api.opensubtitles.com/api/v1"
OPS_API_SEARCH_URL = f"{OPS_API_BASE_URL}/subtitles"
SEARCH_API_KEYS = {
    "kodi7rdisrael-api_key_1": "HNUEpidhxT8ebYNFl6CYJZvuRQltv8Dp",
    "kodi7rdisrael-api_key_2": "P1Z0LLSXKCKYs4VoLyrYcjyKYmoS7mBP",
    "kodi7rdisrael-api_key_3": "eFfHuQ3GfBkYBvPzAsmf6SCHTfK0ekly"
}

DEFAULT_SEASON = 0
DEFAULT_EPISODE = 0
DEFAULT_TITLE = ""
DEFAULT_YEAR = 0
###### Requests Params ##############
REQUEST_TIMEOUT_IN_SECONDS = 5
REQUEST_MAX_RETRIES_NUMBER = 8
#########################################
            
def search_for_subtitles(media_metadata, language='Hebrew'):

    '''Search for Hebrew subtitles for a given media using the OpenSubtitles server.

       New OpenSubtitles.com API Search docs:
       https://opensubtitles.stoplight.io/docs/opensubtitles-api/a172317bd5ccc-search-for-subtitles
    
    Args:
        media_metadata (dict): A dictionary containing metadata for the media to search for.

    Returns:
        list: A list of file names for Hebrew subtitles found on the OpenSubtitles server.
        An empty list is returned if no subtitles were found.
    '''

    # if search_hebrew_subtitles_in_opensubtitles setting is disabled - Cancel search and return empty subtitles list
    if not search_hebrew_subtitles_in_opensubtitles:
        kodi_utils.logger("KODI-RD-IL", f"SETTING search_hebrew_subtitles_in_opensubtitles is: {search_hebrew_subtitles_in_opensubtitles}. Skipping [OPENSUBTITLES] website...")
        return []

    querystring = create_querystring_to_opensubtitles_api(media_metadata, language)
    
    # Perform the subtitles search
    opensubtitles_subtitles_list = search_subtitles(querystring)
    
    if opensubtitles_subtitles_list is None:
        return []
        
    opensubtitles_subtitles_names_list = create_subtitles_names_list(opensubtitles_subtitles_list)
    
    return opensubtitles_subtitles_names_list
    
def search_subtitles(querystring):
        
    OS_SEARCH_API_KEY_NAME, OS_SEARCH_API_KEY_VALUE = random.choice(list(SEARCH_API_KEYS.items()))
    
    kodi_utils.logger("KODI-RD-IL", f"Opensubtitles SearchSubtitles OS_SEARCH_API_KEY_NAME={OS_SEARCH_API_KEY_NAME} | OS_SEARCH_API_KEY_VALUE={OS_SEARCH_API_KEY_VALUE}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Api-Key": OS_SEARCH_API_KEY_VALUE
    }

    kodi_utils.logger("KODI-RD-IL", "Opensubtitles SearchSubtitles querystring: " + repr(querystring))
    
    for attempt_number in range(REQUEST_MAX_RETRIES_NUMBER):
        try:
            response = requests.get(OPS_API_SEARCH_URL, headers=headers, params=querystring, timeout=REQUEST_TIMEOUT_IN_SECONDS)
            response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)
            response_json = response.json()

            # Total subtitles found count.
            total_subs_count = response_json.get('total_count', 0)
            # Calculate total_pages through total_subs_count (OpenSubtitles API splits the results as 50 per page - not 60 as written in "per_page" JSON response!)
            total_pages = (total_subs_count // 50) + (1 if total_subs_count % 50 > 0 else 0)
            kodi_utils.logger("KODI-RD-IL", f"Opensubtitles SearchSubtitles search result: Total subs count: {repr(total_subs_count)} |  Number of pages - {repr(total_pages)}")
            
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
            kodi_utils.logger("KODI-RD-IL", "OpenSubtitles SearchSubtitles connection error: " + repr(ce))
            if attempt_number < REQUEST_MAX_RETRIES_NUMBER - 1:  # Retry if attempts are left
                kodi_utils.logger("KODI-RD-IL", f"OpenSubtitles SearchSubtitles | Retrying... Attempt {attempt_number + 2} of {REQUEST_MAX_RETRIES_NUMBER}")
                continue
            else:
                return [] # Exit the loop if all retries failed
        except Exception as e:
            kodi_utils.logger("KODI-RD-IL", "OpenSubtitles SearchSubtitles error: " + repr(e))
            return []


def create_querystring_to_opensubtitles_api(media_metadata, language):

    '''given: media_metadata dictionary
    return: List of dictionaries of search criteria for opensubtitles server search'''

    media_type = media_metadata.get("media_type")
    title = media_metadata.get("title", DEFAULT_TITLE).lower()
    season = media_metadata.get("season", DEFAULT_SEASON)
    episode = media_metadata.get("episode", DEFAULT_EPISODE)
    year = media_metadata.get("year", DEFAULT_YEAR)
    imdb_id = media_metadata.get("imdb_id", "")
    kodi_utils.logger("KODI-RD-IL", f"Searching in [OPENSUBTITLES] in {language} language: media_type: '{media_type}' title: {title} year: {year} season: {season} episode: {episode} imdb_id: {imdb_id}")

    # Define the querystring
    querystring = {}
    language = "he" if language == "Hebrew" else "en"
    querystring['languages'] = language

    # Build querystring WITH imdb_id
    if imdb_id.startswith('tt'):
    
        if media_type == 'tv':
            #################################################
            # Option 1 - TV Shows - by imdb id + season + episode
            #################################################
            querystring['parent_imdb_id'] = imdb_id
            querystring['season_number'] = season
            querystring['episode_number'] = episode
            kodi_utils.logger("KODI-RD-IL", f"Searching in [OPENSUBTITLES] based on media_type 'tv' parameters: imdb_id, season, episode.")
            
        else:
            #################################################
            # Option 2 - Movies - by imdb id
            #################################################
            querystring['imdb_id'] = imdb_id
            kodi_utils.logger("KODI-RD-IL", f"Searching in [OPENSUBTITLES] based on media_type 'movie' parameters: imdb_id.")

    # Build querystring WITHOUT imdb_id
    else:
        querystring['query'] = title
        
        if media_type == 'tv':
            #################################################
            # Option 3 - TV Shows - by title + season + episode
            #################################################
            querystring['season_number'] = season
            querystring['episode_number'] = episode
            kodi_utils.logger("KODI-RD-IL", f"Searching in [OPENSUBTITLES] based on media_type 'tv' parameters: title, season, episode. (IMDb ID not found)")
            
        else:
            #################################################
            # Option 4 - Movies - by title + year
            #################################################
            querystring['year'] = year
            kodi_utils.logger("KODI-RD-IL", f"Searching in [OPENSUBTITLES] based on media_type 'movie' parameters: title, year. (IMDb ID not found)")


    #################################################
    # Overwritten API default value:
    querystring['hearing_impaired'] = "include"
    # Default API values:
    querystring['ai_translated'] = "include" 
    querystring['foreign_parts_only'] = "include"
    querystring['machine_translated'] = "exclude"
    #################################################

    return querystring   
    

def create_subtitles_names_list(opensubtitles_subtitles_list):

    # Initialize an empty list to store file names
    opensubtitles_subtitles_names_list = []
    
    for search_item in opensubtitles_subtitles_list:

        attributes = search_item.get('attributes', {})
        LanguageName = attributes.get("language")
        if LanguageName is None:
            # Skip this iteration of the loop if LanguageName is None
            continue
        
        try:
            if attributes['files']:
                # Attempt to access 'file_name' if 'files' exist and have elements
                SubFileName = attributes['release'] or attributes['files'][0]['file_name']  # Get 'file_name'
            else:
                # If 'files' or its elements are missing or empty, proceed to the next search_item
                continue
        
        except:
            # Handle cases where 'file_name' is missing or incorrectly structured
            # Go to the next search_item
            continue

        # Define characters that might break the filename
        characters_to_remove = '\\/:*?"<>|\''
        # Remove characters that might cause issues in the filename
        SubFileName = ''.join(c for c in SubFileName if c not in characters_to_remove)
        
        # Remove "תרגום אולפנים"
        SubFileName = SubFileName.replace("תרגום אולפנים", "").replace("אולפנים", "").strip()
        
        opensubtitles_subtitles_names_list.append(SubFileName)
        
    return opensubtitles_subtitles_names_list
