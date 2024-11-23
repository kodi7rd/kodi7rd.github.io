########### Imports ##################### 
from modules import kodi_utils
import requests
import base64
#########################################

########### Constants ###################
MOVIES_TAGLINES_FILE_URL = "https://darksubshebsubs.github.io/DarkSubsHebSubs/movies_taglines.txt"
TV_SHOWS_TAGLINES_FILE_URL = "https://darksubshebsubs.github.io/DarkSubsHebSubs/tvshows_taglines.txt"
DEFAULT_REQUEST_TIMEOUT = 10
#########################################


def get_hebrew_embedded_taglines(media_type):
    
    try:
        if not media_type:
            return None
            
        HEBREW_EMBEDDED_TAGLINES_URL = MOVIES_TAGLINES_FILE_URL if media_type == "movie" else TV_SHOWS_TAGLINES_FILE_URL
        response = requests.get(HEBREW_EMBEDDED_TAGLINES_URL, timeout=DEFAULT_REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            hebrew_embedded_taglines = [line.strip() for line in response.text.split("\n")]
            return hebrew_embedded_taglines
            
        else:
            # Handle non-200 status code here
            kodi_utils.logger("KODI-RD-IL", f"EMBEDDED | hebrew_embedded_taglines request returned status code: {response.status_code}")
            return None
        
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"EMBEDDED | An error occurred while searching for subtitles on [LOC]: {str(e)}")
        return None


def check_match(original_twilight_video_tagline,hebrew_embedded_taglines):

    for hebrew_embedded_tagline in hebrew_embedded_taglines:
        if original_twilight_video_tagline == hebrew_embedded_tagline:
            return True
    return False
    