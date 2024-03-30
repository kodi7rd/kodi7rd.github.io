########### Imports ##################### 
import xbmc
import requests,re
import ssl,urllib3,json
from kodirdil.websites.modules import cloudscraper
from kodirdil.websites.modules import num2ordinal
from modules import kodi_utils
from urllib.parse import quote_plus as que
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

all_lang_codes = {
    'English': {'id': 13, '3let': 'eng', '2let': 'en', 'name': 'English'},
    'Hebrew': {'id': 22, '3let': 'heb', '2let': 'he', 'name': 'Hebrew'}
}

# global subscene title_href:
title_href = ''
#########################################

################### CLOUDFLARE REQUESTS FUNCTIONS ###################################
class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = urllib3.poolmanager.PoolManager(num_pools=connections,
                                                           maxsize=maxsize,
                                                           block=block,
                                                           ssl_version=ssl.PROTOCOL_TLSv1_2,
                                                           ssl_context=ctx)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def __retry(request, response, next, cfscrape, retry=0):
    if retry > 6:
        return None

    if response.status_code in [503, 429, 409, 403]:
        if response.status_code == 403:
            xbmc.sleep(100)
        if response.status_code == 503:
            xbmc.sleep(2000)
            retry = 6
        if response.status_code == 429:
            xbmc.sleep(3000)
        if response.status_code == 409:
            xbmc.sleep(3000)

        retry += 1
        request['validate'] = lambda response: __retry(request, response, next, cfscrape, retry)
        request['next'] = next
        request['cfscrape'] = cfscrape
        return request

def execute_request(request, session=None):

    default_timeout = 10
    request.setdefault('timeout', default_timeout)

    next = request.pop('next', None)

    cfscrape = 'cfscrape' in request
    request.pop('cfscrape', None)

    validate = request.pop('validate', None)
    if not validate:
        validate = lambda response: __retry(request, response, next, cfscrape)

    if next:
        request.pop('stream', None)

    # kodi_utils.logger("KODI-RD-IL", 'Subscene | execute_request params | %s ^ - %s, %s' % (request['method'], request['url'], json.dumps(request.get('params', {}))))
    try:
        if cfscrape:
            request.pop('cfscrape', None)
            if not session:
                session = cloudscraper.create_scraper(interpreter='native')
            response = session.request(**request)
        else:
            session = requests.session()
            session.mount('https://', TLSAdapter())
            response = session.request(**request)
        exc = ''
    except:
        try:
            if cfscrape:
                if not session:
                    session = cloudscraper.create_scraper(interpreter='native')
                response = session.request(verify=False, **request)
            else:
                response = requests.request(verify=False, **request)
            exc = ''
        except:
            exc = traceback.format_exc()
            response = lambda: None
            response.text = ''
            response.content = ''
            response.status_code = 500
    kodi_utils.logger("KODI-RD-IL", 'Subscene | execute_request result | %s $ - %s - %s, %s' % (request['method'], request['url'], response.status_code, exc))

    alt_request = validate(response)
    if alt_request:
        return execute_request(alt_request)

    if next and response.status_code == 200:
        next_request = next(response)
        if next_request:
            return execute_request(next_request, session)
        else:
            return None

    return response
#####################################################################################


############## SUBSCENE SUBTTILES SEARCH FUNCTIONS ##################################
    
    
def __match_title(title, year, response):
    title_with_year = '%s (%s)' % (title, year)
    href_regex = r'<a href="(.*?)">' + re.escape(title_with_year) + r'</a>'
    return re.search(href_regex, response.text, re.IGNORECASE)

def __find_title_result(title, year, response, subscene_lang_ids):

    # Try match with the previous year
    previous_year = int(year) - 1
    # Try match with the next year
    next_year = int(year) + 1
    result = __match_title(title, year, response) or __match_title(title, previous_year, response) or __match_title(title, next_year, response) or None

    if not result:
        return None

    global title_href
    title_href = result.group(1)

    request = {
        'cfscrape': True,
        'method': 'GET',
        'url': SUBSCENE_URL + title_href
    }

    # Add LanguageFilter parameter as a cookie (from subscene_lang_ids)
    if subscene_lang_ids: # If empty - will search in all languages
        languages_ids_filter = f"LanguageFilter={','.join(map(str, subscene_lang_ids))}"
        request['headers'] = {}
        request['headers']['Cookie'] = languages_ids_filter

    return request

def build_search_requests(media_type, title, year, season, subscene_lang_ids):

    if media_type == 'tv':
        ordinal_season = num2ordinal.convert(season).strip()
        title = '%s - %s Season' % (title, ordinal_season)

    request = {
        'cfscrape': True,
        'method': 'GET',
        'url': SUBSCENE_URL + ('/subtitles/searchbytitle?query=' + que(title)),
        'next': lambda response: __find_title_result(title, year, response, subscene_lang_ids),
    }

    return request

def parse_search_response(media_type, season, episode, search_response):
    global title_href
    any_regex = r'.*?'

    results_regex = (
            r'<a href="' + re.escape(title_href) + r'(.*?)">' +
                any_regex + r'</span>' + any_regex +
                r'<span>(.*?)</span>' + any_regex +
            r'</a>' + any_regex +
            r'(<td class="a41">)?' + any_regex +
        r'</tr>'
    )

    results = re.findall(results_regex, search_response.text, re.DOTALL)
    if not results:
        return []

    if media_type == 'tv':
        season_number = season.zfill(2)
        episode_number = episode.zfill(2)
        episodeid = 's%se%s' % (season_number, episode_number)
        # Regex Options: .S01. | S01E01 | 01x01
        identifier = r'(\.s%s\.|%s|\b%sx%s\b)' % (season_number, episodeid, season_number, episode_number)
        results = list(filter(lambda x: re.search(identifier, x[1], re.IGNORECASE), results))

    def map_result(result):
        subtitle_file_name = result[1].strip()
        return subtitle_file_name

    return list(map(map_result, results))
#####################################################################################

def search_for_subtitles(media_metadata, language='Hebrew'):

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

    # Get metadata values from the media_metadata dictionary
    media_type = media_metadata.get("media_type")
    title = media_metadata.get("title", DEFAULT_TITLE).lower()
    season = str(media_metadata.get("season", DEFAULT_SEASON))
    episode = str(media_metadata.get("episode", DEFAULT_EPISODE))
    year = media_metadata.get("year", DEFAULT_YEAR)
    kodi_utils.logger("KODI-RD-IL", f"Searching in [SUBSCENE] in {language} language: media_type: {media_type} Title: {title}: Season: {season} Episode: {episode} Year: {year}")
    
    
    ######################### LANGUAGE FILTER ####################################
    selected_lang=[]
    if language=='Hebrew':
        selected_lang=['heb']
    if language=='English':
        selected_lang=['eng']


    subscene_lang_ids = []
    for lang in selected_lang:
        for lang_name, lang_info in all_lang_codes.items():
            if lang == lang_info['3let']:
                subscene_lang_ids.append(lang_info['id'])
    # kodi_utils.logger("KODI-RD-IL", f"Subscene | LanguageFilter is: {str(selected_lang)} | {str(subscene_lang_ids)}")
    ################################################################################
    
    subscene_subtitles_list = []
            
    try:
        search_request = build_search_requests(media_type, title, year, season, subscene_lang_ids)
        search_response = execute_request(search_request)
            
        if search_response:
            kodi_utils.logger("KODI-RD-IL", f"Subscene | search_for_subtitles | search_response.status_code={search_response.status_code}")

            if search_response.status_code == 200 and search_response.text:
                subscene_subtitles_list = parse_search_response(media_type, season, episode, search_response)
            else:
                kodi_utils.logger("KODI-RD-IL", f"Subscene | search_for_subtitles | no results.")
                return []
        else:
            kodi_utils.logger("KODI-RD-IL", f"Subscene | search_for_subtitles | search_response is None.")
            return []
            
        return subscene_subtitles_list
        
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"An error occurred while searching for subtitles on [SUBSCENE]: {str(e)}")
        return []
