########### Imports ##################### 
from modules import kodi_utils
import json
import requests
from unicodedata import normalize
#########################################

########### Settings ####################
search_hebrew_subtitles_in_wizdom = kodi_utils.get_setting('search_hebrew_subtitles_in_wizdom', 'true') == 'true'
#########################################

########### Constants ###################
WIZDOM_API_BASE_URL = "https://wizdom.xyz/api"
WIZDOM_API_SEARCH_URL = f"{WIZDOM_API_BASE_URL}/search?action=by_id"
DEFAULT_SEASON = 0
DEFAULT_EPISODE = 0
DEFAULT_TITLE = 0
DEFAULT_REQUEST_TIMEOUT = 10
#########################################


def search_for_subtitles(media_metadata):

    """
    Given metadata for a media file, fetches a list of available Hebrew subtitles
    from Wizdom.xyz API.

    Args:
        media_metadata: A dictionary containing metadata for a media file, including
            the media type, title, season number, episode number, and IMDb ID.

    Returns:
        A list of strings representing available Hebrew subtitle versions for the
        given media file.
    """

    # if search_hebrew_subtitles_in_wizdom setting is disabled - Cancel search and return empty subtitles list
    if not search_hebrew_subtitles_in_wizdom:
        kodi_utils.logger("KODI-RD-IL", f"SETTING search_hebrew_subtitles_in_wizdom is: {search_hebrew_subtitles_in_wizdom}. Skipping [WIZDOM] website...")
        return []
    
    media_type = media_metadata.get("media_type")
    title = media_metadata.get("title", DEFAULT_TITLE)
    season = media_metadata.get("season", DEFAULT_SEASON)
    episode = media_metadata.get("episode", DEFAULT_EPISODE)
    imdb_id = media_metadata.get("imdb_id", "")
    
    # Log the search parameters
    kodi_utils.logger("KODI-RD-IL", f"Searching in [WIZDOM]: media_type: {media_type} title: {title}: season: {season} episode: {episode} imdb_id: {imdb_id}")

    querystring = {}
    querystring['imdb'] = imdb_id
    
    if media_type == 'tv':
        #################################################
        # TV Shows - by imdb id + season + episode
        #################################################
        querystring['season'] = str(season).zfill(2)
        querystring['episode'] = str(episode).zfill(2)

    try:
        # Send the API request and parse the response
        response = requests.get(WIZDOM_API_SEARCH_URL, params=querystring, timeout=DEFAULT_REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)
        wizdom_response_json = response.json()
    except Exception as e:
        # Handle any errors that occur during the API request
        kodi_utils.logger("KODI-RD-IL", f"Error in sending API request to [WIZDOM]: {str(e)}")
        return []
      
    wizdom_subtitles_list = []
    
    if wizdom_response_json:
        # Extract the subtitle versions from the API response
        for wizdom_subtitle in wizdom_response_json:
            wizdom_subtitles_list.append(wizdom_subtitle["versioname"])
            
    return wizdom_subtitles_list
    