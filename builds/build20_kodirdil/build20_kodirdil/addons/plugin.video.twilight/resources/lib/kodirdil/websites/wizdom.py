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
WIZDOM_URL = "http://wizdom.xyz"
DEFAULT_SEASON = 0
DEFAULT_EPISODE = 0
DEFAULT_TITLE = 0
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
    title = lowercase_with_underscores(media_metadata.get("title", DEFAULT_TITLE))
    season = media_metadata.get("season", DEFAULT_SEASON)
    episode = media_metadata.get("episode", DEFAULT_EPISODE)
    imdb_id = media_metadata.get("imdb_id", "")
    
    # Log the search parameters
    kodi_utils.logger("KODI-RD-IL", f"Searching in [WIZDOM]: media_type: {media_type} title: {title}: season: {season} episode: {episode} imdb_id: {imdb_id}")

    # Build the API URL
    wizdom_api_url = f"{WIZDOM_URL}/api/search?action=by_id&imdb={imdb_id}&season={season}&episode={episode}"

    try:
        # Send the API request and parse the response
        wizdom_api_response = requests.get(wizdom_api_url).json()
    except Exception as e:
        # Handle any errors that occur during the API request
        wizdom_api_response = {}
        kodi_utils.logger("KODI-RD-IL", f"Error in sending API request to [WIZDOM]: {str(e)}")
        return []
      
    wizdom_subtitles_list = []
    
     # Extract the subtitle versions from the API response
    for wizdom_subtitle in wizdom_api_response:
        if wizdom_subtitle["versioname"] not in wizdom_subtitles_list:
            wizdom_subtitles_list.append(wizdom_subtitle["versioname"])
            
    return wizdom_subtitles_list
      
      
def lowercase_with_underscores(string):

    """
    Converts a string to lowercase and replaces spaces with underscores.

    Args:
        string: A string to convert.

    Returns:
        A lowercase version of the input string with spaces replaced by underscores.
    """
    
    return normalize('NFKD', (string)).encode('utf-8', 'ignore')
    