# Import necessary libraries
from modules import kodi_utils
import xmlrpc.client as xmlrpclib
import socket
import http.client as httplib
#########################################

########### Settings ####################
search_hebrew_subtitles_in_opensubtitles = kodi_utils.get_setting('search_hebrew_subtitles_in_opensubtitles', 'true') == 'true'

# Default value for SUBTITLE_SEARCH_LANGUAGE
OPS_SUBTITLE_SEARCH_LANGUAGE = ['heb']

#########################################

########### Constants ###################
OPENSUBTITLES_URL_XMLRPC = u"https://api.opensubtitles.org/xml-rpc"
DEFAULT_SEASON = 0
DEFAULT_EPISODE = 0
DEFAULT_TITLE = 0
DEFAULT_YEAR = 0
#########################################

# Set default timeout value to 5 seconds for socket connections
socket.setdefaulttimeout(5)
#########################################

# Define the Transport class with timeout support
class TimeoutTransport(xmlrpclib.Transport):

    def __init__(self, use_datetime=0, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, secure=False):
        xmlrpclib.Transport.__init__(self, use_datetime)
        self.timeout = timeout
        self.secure = secure

    def make_connection(self, host):
        # Check if we already have a connection and return it
        if self._connection and host == self._connection[0]:
            return self._connection[1]
        # Otherwise, get the host info, set the connection parameters and return the connection
        chost, self._extra_headers, x509 = self.get_host_info(host)
        if self.secure:
            self._connection = host, httplib.HTTPSConnection(chost, None, timeout=self.timeout, **(x509 or {}))
        else:
            self._connection = host, httplib.HTTPConnection(chost, timeout=self.timeout)

        return self._connection[1]

# Define the OSDBServer class to handle subtitle search requests
class OSDBServer:

    def __init__(self):
        # Create an instance of the server and initialize the login token
        self.server = xmlrpclib.Server(OPENSUBTITLES_URL_XMLRPC, verbose=0, transport=TimeoutTransport())
        login = self.server.LogIn("", "", "en", "XBMC_Subtitles_Unofficial")
        self.osdb_token = login["token"]

    def search_subtitles(self, media_metadata, language):
        '''given: media_metadata dictionary
        return: List of subtitle file names based on search results from opensubtitles server'''
    
        searchlist = create_search_list_to_opensubtitles_api(media_metadata, language)
        
        # Perform the opensubtitles_search_results and return a list of subtitle file names
        opensubtitles_search_results = self.server.SearchSubtitles(self.osdb_token, searchlist)
        
        if opensubtitles_search_results["data"]:
            return [subtitle_name['SubFileName'] for subtitle_name in opensubtitles_search_results["data"]]
        else:
            return []
            
            
def search_for_subtitles(media_metadata, language='Hebrew'):

    '''Search for Hebrew subtitles for a given media using the OpenSubtitles server.

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
        
    global OPS_SUBTITLE_SEARCH_LANGUAGE  # Use the global variable

    if language == 'English':
    
        # Temporarily set the subtitle search language based on the 'language' parameter
        ORIGINAL_OPS_SUBTITLE_SEARCH_LANGUAGE = OPS_SUBTITLE_SEARCH_LANGUAGE
        OPS_SUBTITLE_SEARCH_LANGUAGE = ['eng']

    # Initialize the subtitle list and perform the opensubtitles_search_results
    opensubtitles_subtitles_list = []
    
    opensubtitles_subtitles_list = OSDBServer().search_subtitles(media_metadata, language)

    if language == 'English':
        # Reset the subtitle search language to the original value
        OPS_SUBTITLE_SEARCH_LANGUAGE = ORIGINAL_OPS_SUBTITLE_SEARCH_LANGUAGE
    
    if opensubtitles_subtitles_list is None:
        return []
    return opensubtitles_subtitles_list


def create_search_list_to_opensubtitles_api(media_metadata, language):

    '''given: media_metadata dictionary
    return: List of dictionaries of search criteria for opensubtitles server search'''

    media_type = media_metadata.get("media_type")
    title = media_metadata.get("title", DEFAULT_TITLE)
    season = media_metadata.get("season", DEFAULT_SEASON)
    episode = media_metadata.get("episode", DEFAULT_EPISODE)
    year = media_metadata.get("year", DEFAULT_YEAR)
    imdb_id = media_metadata.get("imdb_id", "")
    kodi_utils.logger("KODI-RD-IL", f"Searching in [OPENSUBTITLES] in {language} language: media_type: '{media_type}' title: {title} year: {year} season: {season} episode: {episode} imdb_id: {imdb_id}")

    # Define the search list
    searchlist = []

    # If the media_type is a TV show, create the search string based on the TV show title, season, and episode
    if media_type == 'tv':

        kodi_utils.logger("KODI-RD-IL", f"Searching in [OPENSUBTITLES] based on movie_type 'tv' parameters: title, season, episode.")
        OS_search_string = f"{title} S{season:02d}E{episode:02d}".replace(" ", "+")

        searchlist.append({
            'sublanguageid': ",".join(OPS_SUBTITLE_SEARCH_LANGUAGE),
            'query': OS_search_string,
            'season': season,
            'episode': episode
        })
    # Else - if the media_type is a Movie and has IMDb ID, create the search list based on the IMDb ID
    elif imdb_id:
        kodi_utils.logger("KODI-RD-IL", f"Searching in [OPENSUBTITLES] based on movie_type 'movie' parameters: imdb_id")
        searchlist.append({
            'sublanguageid': ",".join(OPS_SUBTITLE_SEARCH_LANGUAGE),
            'imdbid': imdb_id.replace('tt', '')
        })
        
    # Otherwise, the media_type is a Movie and no IMDb ID found - create the search list based on the title and year
    else:
        kodi_utils.logger("KODI-RD-IL", f"Searching in [OPENSUBTITLES] based on movie_type 'movie' parameters: title, year. (IMDb ID not found)")
        OS_search_string = title.replace(" ", "+")
        searchlist.append({
            'sublanguageid': ",".join(OPS_SUBTITLE_SEARCH_LANGUAGE),
            'query': OS_search_string,
            'year': year
        })

    return searchlist
        