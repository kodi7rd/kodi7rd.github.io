########### Imports ##################### 
from modules import kodi_utils
import json
import requests
import re
import xbmc
#########################################

########### Settings ####################
search_hebrew_subtitles_in_yify = kodi_utils.get_setting('search_hebrew_subtitles_in_yify', 'true') == 'true'
#########################################

########### Constants ###################
YIFY_BASE_URL = "https://yifysubtitles.ch"
YIFY_SEARCH_URL = f"{YIFY_BASE_URL}/movie-imdb"
DEFAULT_REQUEST_TIMEOUT = 10
#########################################

# language = Hebrew / English
def search_for_subtitles(media_metadata, language='Hebrew'):

    # if search_hebrew_subtitles_in_yify setting is disabled - Cancel search and return empty subtitles list
    if not search_hebrew_subtitles_in_yify:
        kodi_utils.logger("KODI-RD-IL", f"SETTING search_hebrew_subtitles_in_yify is: {search_hebrew_subtitles_in_yify}. Skipping [YIFY] website...")
        return []
    
    media_type = media_metadata.get("media_type")
    imdb_id = media_metadata.get("imdb_id", "")
    
    if media_type != 'movie' or not imdb_id.startswith('tt'):
        kodi_utils.logger("KODI-RD-IL", '[YIFY] | media_type is not Movie or IMDb ID missing. exiting...')
        return []
    
    # Log the search parameters
    kodi_utils.logger("KODI-RD-IL", f"Searching in [YIFY]: media_type: {media_type} imdb_id: {imdb_id} language: {language}")
    
    try:
        # Example: https://yifysubtitles.ch/movie-imdb/tt15239678
        response = requests.get(f"{YIFY_SEARCH_URL}/{imdb_id}", timeout=DEFAULT_REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)
        # Get the HTML content
        html_content = response.text
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"Error in sending API request to [YIFY]: {str(e)}")
        return []
    
    # Regular expression pattern to find rows with data-id attribute
    rows = re.findall(r'<tr data-id="\d+">(.*?)</tr>', html_content, re.DOTALL)
    
    yify_subtitles_list = []
        
    # Define characters that might break the filename (It caused writing problem to MyTmp dir)
    characters_to_remove = '\\/:*?"<>|\''
    
    for row in rows:
        FullLanguageName, SubFileName = _parse_row(row)
        if any(value is None or value == '' for value in (FullLanguageName, SubFileName)):
            continue
        
        # Skip if sub language is not current search language.
        if FullLanguageName == language:
            # Remove characters that might cause issues in the filename
            SubFileName = ''.join(c for c in SubFileName if c not in characters_to_remove)
          
            yify_subtitles_list.append(SubFileName)
        
    return yify_subtitles_list

def _parse_row(row):    
    # Extracting language
    lang_match = re.search(r'sub-lang">(.*?)</span>', row)
    FullLanguageName = lang_match.group(1) if lang_match else None
    
    # Extracting release
    release_match = re.search(r'span class="text-muted">subtitle</span>\s+(.*?)<', row)
    SubFileName = release_match.group(1).strip() if release_match else None
    
    return FullLanguageName, SubFileName
    