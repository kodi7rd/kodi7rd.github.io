########### Imports ##################### 
import xbmc
import requests,re
import ssl,urllib3
from kodirdil.websites.modules import cloudscraper
from modules import kodi_utils
#########################################

########### Settings ####################
search_hebrew_subtitles_in_subscene = kodi_utils.get_setting('search_hebrew_subtitles_in_subscene', 'true') == 'true'
#########################################

########### Constants ###################
SUBSCENE_URL = "https://subscene.com"
DEFAULT_SEASON = 0
DEFAULT_EPISODE = 0
DEFAULT_TITLE = 0
DEFAULT_YEAR = 0

seasons = ["Specials", "First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth", "Tenth",
           "Eleventh", "Twelfth", "Thirteenth", "Fourteenth", "Fifteenth", "Sixteenth", "Seventeenth",
           "Eighteenth", "Nineteenth", "Twentieth",
           "Twenty-first", "Twenty-second", "Twenty-third", "Twenty-fourth", "Twenty-fifth", "Twenty-sixth",
           "Twenty-seventh", "Twenty-eighth", "Twenty-ninth"]
           
SUBTITLE_SEARCH_LANGUAGE = ['hebrew']
#########################################

def search_hebrew_subtitles(media_metadata):

    """
    Searches for Hebrew subtitles on the Subscene website.

    Args:
    - media_metadata: A dictionary containing metadata about the media to be searched for subtitles.

    Returns:
    - A list of filenames of the found subtitles.
    """
    
    # if search_hebrew_subtitles_in_subscene setting is disabled - Cancel search and return empty subtitles list
    if not search_hebrew_subtitles_in_subscene:
        kodi_utils.logger("KODI-RD-IL", f"SETTING search_hebrew_subtitles_in_subscene is: {search_hebrew_subtitles_in_subscene}. Skipping [SUBSCENE] website...")
        return []
    
    # Set up variables
    subscene_subtitles_list = []

    # Get metadata values from the media_metadata dictionary
    media_type = media_metadata.get("media_type")
    title = media_metadata.get("title", DEFAULT_TITLE)
    season = str(media_metadata.get("season", DEFAULT_SEASON))
    episode = str(media_metadata.get("episode", DEFAULT_EPISODE))
    year = media_metadata.get("year", DEFAULT_YEAR)
    kodi_utils.logger("KODI-RD-IL", f"Searching in [SUBSCENE]: media_type: {media_type} Title: {title}: Season: {season} Episode: {episode} Year: {year}")
    
    try:
        if media_type == "tv":
            episode = season + ":" + episode
            padded_episode_number = episode.zfill(2)
            padded_season_number = season.zfill(2)
            
            
        headers, data = setup_search_request(title)
        
        # Extract the title without the year from the title
        title_without_year = re.compile("([ .\w']+?)(\W\d{4}\W?.*)").findall(title)
        title_for_search = title_without_year[0][0] if title_without_year else title
        

        # Set up scraper and send HTTP requests
        scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        scraper.mount('https://', TLSAdapter())
        
        search_results = search_subtitles_by_title(scraper, title_for_search, headers, data)
        
        regex = '<div class="title">.+?<a href="(.+?)">(.+?)<'
        matching_titles = re.compile(regex,re.DOTALL).findall(search_results)
        
        for link, subtitle_name in matching_titles:
            is_matching_subtitle = False
            
            if media_type == 'movie':
                movie_title_without_year = subtitle_name.split('(')[0].strip()
         
                if title.lower() == movie_title_without_year.lower() and str(year) in subtitle_name:
                    is_matching_subtitle = True
            else:
                tv_season_name = '%s - %s Season'%(title, seasons[int(season)])
               
                if tv_season_name.lower() == subtitle_name.lower():
                    is_matching_subtitle = True
            
            
            if is_matching_subtitle:  
                response = 'Please do not hammer on Subscene'
                counter = 0
                while 'Please do not hammer on Subscene'  in response:
                    # Send a GET request to retrieve the subtitle page
                    response = scraper.get(f'{SUBSCENE_URL}/' + link, headers=headers)
                    
                    if response.status_code in [503, 429, 403]:
                        if response.status_code == 503:
                            xbmc.sleep(2000)
                        if response.status_code == 429:
                            xbmc.sleep(3000)
                    else:
                        response = response.content.decode('utf-8')
                        
                    xbmc.sleep(100)
                    counter += 1
                    if counter > 10:
                        break
                subtitle_page_html = response
               
                regex = '<tr>(.+?)</tr'
                subtitle_links = re.compile(regex,re.DOTALL).findall(subtitle_page_html)
                
                for subtitle_link_html in subtitle_links:
                
                    regex = '<a href="(.+?)">.+?<span class=".+?">(.+?)</span>.+?<span>(.+?)</span>'
                    subtitle_info = re.compile(regex,re.DOTALL).findall(subtitle_link_html)
                    
                    if len(subtitle_info) == 0:
                        continue
                        
                    subtitle_link, subtitle_language, subtitle_filename = subtitle_info[0]
                    
                    subtitle_language = subtitle_language.replace('\t','').replace('\r','').replace('\n','').strip()
                    
                    subtitle_filename = subtitle_filename.replace('\t','').replace('\r','').replace('\n','').strip()
                    
                    if media_type == 'tv':
                        if ('S%sE%s.'%(padded_season_number, padded_episode_number)).lower() not in subtitle_filename.lower() and ('S%sE%s '%(padded_season_number, padded_episode_number)).lower() not in subtitle_filename.lower() and ('S%s.'%(padded_season_number)).lower() not in subtitle_filename.lower():
                            continue
                            
                    if subtitle_language.lower() not in SUBTITLE_SEARCH_LANGUAGE:
                        continue
                    
                    subscene_subtitles_list.append(subtitle_filename)
                        
        return subscene_subtitles_list
        
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"An error occurred while searching for subtitles on [SUBSCENE]: {str(e)}")
        return []
    
    
def search_subtitles_by_title(scraper, title_for_search, headers, data):

    """
    Searches for subtitles on Subscene by title.

    Args:
    - scraper: The CloudScraper instance to use for sending HTTP requests.
    - title_for_search: The title of the media to search for subtitles.
    - headers: The headers to use for HTTP requests.
    - data: The data to use for HTTP requests.

    Returns:
    - The HTTP response as a string.
    """
    
    response = 'Please do not hammer on Subscene'
    
    num_tries = 0    
    while 'Please do not hammer on Subscene'  in response:
        # Send a POST request to search for subtitles by title
        response = scraper.post(f"{SUBSCENE_URL}/subtitles/searchbytitle?query={title_for_search}", headers=headers, data=data)
        if response.status_code in [503, 429, 403]:
            if response.status_code == 503:
                xbmc.sleep(2000)
            if response.status_code == 429:
                xbmc.sleep(3000)
        else:
            response = response.content.decode('utf-8')
        xbmc.sleep(100)
        num_tries += 1
        if num_tries > 10:
            break
            
    return response
     
def setup_search_request(title):

    """
    Sets up headers and data for HTTP requests to Subscene to search for subtitles by title.

    Args:
    - title: The title of the media to search for subtitles.

    Returns:
    - A dictionary containing headers and data for HTTP requests.
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Origin': f'{SUBSCENE_URL}',
        'Connection': 'keep-alive',
        'Referer': f'{SUBSCENE_URL}/subtitles/searchbytitle',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    data = {
      'query': title,
      'l': ''
    }
    
    return headers, data
    
    
class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        ctx.check_hostname = False
        self.poolmanager = urllib3.poolmanager.PoolManager(num_pools=connections,
                                                           maxsize=maxsize,
                                                           block=block,
                                                           ssl_version=ssl.PROTOCOL_TLSv1_2,
                                                           ssl_context=ctx)
                                                           