# Import necessary libraries
import shutil
import xbmcaddon,os,xbmc
global global_var,site_id,sub_color#global
global_var=[]
from resources.modules import log
import requests,json
import urllib
from resources.modules.extract_sub import extract
from resources.modules.general import DEFAULT_REQUEST_TIMEOUT
import xbmcvfs
import re
#########################################

que=urllib.parse.quote_plus
Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
MyAddonName = Addon.getAddonInfo('name')
MyAddonVersion    = Addon.getAddonInfo('version') # Module version
USER_AGENT = '%s v%s' %(MyAddonName, MyAddonVersion)
xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_yify'))

########### Constants ###################
site_id='[YIFY]'
sub_color='chocolate'
YIFY_BASE_URL = "https://yifysubtitles.ch"
YIFY_SEARCH_URL = f"{YIFY_BASE_URL}/movie-imdb"
YIFY_DOWNLOAD_URL = f"{YIFY_BASE_URL}/subtitle/%s.zip"

all_lang_codes = {
    'sqi': 'Albanian',
    'ara': 'Arabic',
    'ben': 'Bengali',
    'por': 'Brazilian Portuguese',
    'bul': 'Bulgarian',
    'zho': 'Chinese',
    'hrv': 'Croatian',
    'ces': 'Czech',
    'dan': 'Danish',
    'nld': 'Dutch',
    'eng': 'English',
    'fas': 'Farsi/Persian',
    'fin': 'Finnish',
    'fre': 'French',
    'deu': 'German',
    'ell': 'Greek',
    'heb': 'Hebrew',
    'hun': 'Hungarian',
    'ind': 'Indonesian',
    'ita': 'Italian',
    'jpn': 'Japanese',
    'kor': 'Korean',
    'lit': 'Lithuanian',
    'mkd': 'Macedonian',
    'msa': 'Malay',
    'nor': 'Norwegian',
    'pol': 'Polish',
    'ron': 'Romanian',
    'rus': 'Russian',
    'srp': 'Serbian',
    'slv': 'Slovenian',
    'spa': 'Spanish',
    'swe': 'Swedish',
    'tha': 'Thai',
    'tur': 'Turkish',
    'urd': 'Urdu',
    'vie': 'Vietnamese'
}
#########################################

def _parse_row(row):
    # Extracting rating
    rating_match = re.search(r'<td class="rating-cell">.*?<span class="label(?:.*?)?">(\d+)</span>', row)
    SubRating = int(rating_match.group(1)) if rating_match else 0
    
    # Extracting language
    lang_match = re.search(r'sub-lang">(.*?)</span>', row)
    FullLanguageName = lang_match.group(1) if lang_match else None
    
    # Extracting release
    release_match = re.search(r'span class="text-muted">subtitle</span>\s+(.*?)<', row)
    SubFileName = release_match.group(1).strip() if release_match else None
    
    # Extracting page link
    link_match = re.search(r'<a href="(.*?)">', row)
    SubPageLink = link_match.group(1) if link_match else None
    
    # Checking for hearing impairment
    hi_match = re.search(r'hi-subtitle"', row)
    hearing_impaired = "true" if hi_match else "false"
    
    return SubRating, FullLanguageName, SubFileName, SubPageLink, hearing_impaired
       
def get_subs(video_data):

    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    
    global global_var
    log.warning('DEBUG | [YIFY] | Searching YIFY Subtitles')

    media_type = video_data.get('media_type', '')
    imdb_id = video_data.get('imdb', '')
    
    if media_type != 'movie' or not imdb_id.startswith('tt'):
        log.warning(f'DEBUG | [YIFY] | media_type is not Movie or IMDb ID missing. exiting...')
        return []
    
    
    selected_lang = []
    if Addon.getSetting("language_hebrew")=='true':
        selected_lang.append('heb')
    if Addon.getSetting("language_english")=='true':
        selected_lang.append('eng')
    if Addon.getSetting("language_russian")=='true':
        selected_lang.append('rus')
    if Addon.getSetting("language_arab")=='true':
        selected_lang.append('ara')
    if len(Addon.getSetting("other_lang"))>0:
        all_lang=Addon.getSetting("other_lang").split(",")
        for items in all_lang:
            selected_lang.append(str(items))
    if Addon.getSetting("all_lang")=='true':
        selected_lang = ['ALL']
    else:
        selected_lang = [all_lang_codes[code] for code in selected_lang if code in all_lang_codes]
    
    try:
        # Example: https://yifysubtitles.ch/movie-imdb/tt15239678
        response = requests.get(f"{YIFY_SEARCH_URL}/{imdb_id}", timeout=DEFAULT_REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)
        # Get the HTML content
        html_content = response.text
        log.warning(f"DEBUG | [YIFY] | YIFY Subtitles SearchSubtitles | URL: {response.url} | Status Code: {response.status_code}")
    except Exception as e:
        log.warning(f"DEBUG | [YIFY] | YIFY Subtitles SearchSubtitles | type: {type(e)} | Exception: {repr(e)}")
        return []
    
    # Regular expression pattern to find rows with data-id attribute
    rows = re.findall(r'<tr data-id="\d+">(.*?)</tr>', html_content, re.DOTALL)
    
    subtitle_list = []
    for row in rows:
        SubRating, FullLanguageName, SubFileName, SubPageLink, hearing_impaired = _parse_row(row)
        if any(value is None or value == '' for value in (SubRating, FullLanguageName, SubFileName, SubPageLink, hearing_impaired)):
            continue
        
        # Skip if sub language not in language settings.
        if selected_lang != ['ALL'] and FullLanguageName not in selected_lang:
            continue
            
        # Attempt language conversion; if it fails, assign the original FullLanguageName
        FullLanguageName = xbmc.convertLanguage(FullLanguageName, xbmc.ENGLISH_NAME) or FullLanguageName
            
        # Attempt language conversion; Two letter code as defined in ISO 639-1
        thumbnailImageLanguageName = xbmc.convertLanguage(FullLanguageName, xbmc.ISO_639_1)

        # Define characters that might break the filename (It caused writing problem to MyTmp dir)
        characters_to_remove = '\\/:*?"<>|\''
        # Remove characters that might cause issues in the filename
        SubFileName = ''.join(c for c in SubFileName if c not in characters_to_remove)
            
        download_data={}
        download_data['filename'] = SubFileName
        download_data['SubPageLink'] = SubPageLink
        download_data['format'] = "zip"
        # Send Hearing Impaired (HI) flag to determine if to clean HI tags or not.
        download_data['hearing_imp'] = hearing_impaired
        
        url = "plugin://%s/?action=download&filename=%s&language=%s&download_data=%s&source=yify" % (MyScriptID,
                                                                                            que(SubFileName),
                                                                                            FullLanguageName,
                                                                                            que(json.dumps(download_data))
                                                                                            )

        json_data={'url':url,
                'label':FullLanguageName,
                'label2':site_id+' '+SubFileName,
                'iconImage':str(int(round(float(SubRating)/2))),
                'thumbnailImage':thumbnailImageLanguageName,
                'hearing_imp':hearing_impaired,
                'site_id':site_id,
                'sub_color':sub_color,
                'filename':SubFileName,
                'sync': "false"}

        
        subtitle_list.append(json_data)
            
    global_var=subtitle_list


def download(download_data,MySubFolder):
    
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)
    
    SubPageLink = download_data['SubPageLink'].replace("/subtitles/", "")  # Remove the "/subtitles/" prefix
    format = download_data['format']
    filename = download_data['filename']
    
    subFile = os.path.join(MyTmp, "%s.%s" %(str(filename), format))
    log.warning(f'DEBUG | [YIFY] | Desired sub SubPageLink: {SubPageLink} | subFile: {subFile}')
    
    # Example: https://yifysubtitles.ch/subtitles/dune-part-two-2024-hebrew-yify-618077
    subtitle_download_url = YIFY_DOWNLOAD_URL % SubPageLink
        
    try:
        sub_download_response = requests.get(subtitle_download_url, timeout=DEFAULT_REQUEST_TIMEOUT)
        log.warning(f"DEBUG | [YIFY] | DownloadSubtitles sub_download_response: {sub_download_response.status_code}")
        sub_download_response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)

        with open(subFile, 'wb') as temp_subFile:
            temp_subFile.write(sub_download_response.content)
        sub_file=extract(subFile,MySubFolder)
        return sub_file
    except Exception as e:
        log.warning(f'DEBUG | [YIFY] | DownloadSubtitles | type: {type(e)} | Exception: {repr(e)}')