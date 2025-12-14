# Import necessary libraries
import xbmcaddon,xbmcvfs,os,xbmc
global global_var,site_id,sub_color#global
global_var=[]
from resources.modules import log
import requests,json,shutil
from resources.modules.extract_sub import g_extract
import urllib.parse
import struct
from resources.modules.general import DEFAULT_REQUEST_TIMEOUT
#########################################

Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
que=urllib.parse.quote_plus
xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_bsplayer'))

########### Constants ###################
site_id = '[BSPlayer]'
sub_color = 'lightblue'
BSPLAYER_API_LOGIN_URL = "http://r4.api.subs.bplayer.org/subs-rest/login"
BSPLAYER_API_SEARCH_URL = "http://r4.api.subs.bplayer.org/subs-rest/searchSubtitles"

__64k = 65536
__longlong_format_char = 'q'
__byte_size = struct.calcsize(__longlong_format_char)
#########################################

def __sum_64k_bytes(file, result):
    range_value = __64k / __byte_size
    
    range_value = round(range_value)

    for _ in range(range_value):
        try: chunk = file.readBytes(__byte_size)
        except: chunk = file.read(__byte_size)
        (value,) = struct.unpack(__longlong_format_char, chunk)
        result.filehash += value
        result.filehash &= 0xFFFFFFFFFFFFFFFF
def __set_size_and_hash():
    

    f = xbmcvfs.File( xbmc.Player().getPlayingFile())
    filehash=0
    filesize=0
    try:
        filesize = f.size()

        # used for mocking
        try:
            filehash = f.hash()
            return 0,0
        except: pass

        if filesize < __64k * 2:
            return 0,0

        # ref: https://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
        # filehash = filesize + 64bit sum of the first and last 64k of the file
        result = lambda: None
        result.filehash = filesize

        __sum_64k_bytes(f, result)
        f.seek(filesize - __64k, os.SEEK_SET)
        __sum_64k_bytes(f, result)

        filehash = "%016x" % result.filehash
    finally:
        f.close()

    return filehash,filesize
def get_subs(video_data):

    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    
    log.warning('DEBUG | [BSPlayer] | Searching Bsplayer')
    global global_var
    if not xbmc.Player().isPlaying():
        return []
        
    filehash,filesize=__set_size_and_hash()
    log.warning(f'DEBUG | [BSPlayer] | filehash={filehash}')
    
    headers={
        'User-Agent': 'BSPlayer 3.0/10394',
        'Accept': '*/*', 
        'Accept-Encoding': '*', 

        'Content-Type': 'application/x-www-form-urlencoded'
        }
        
    data={'AppID':'BASPlayer v3'}
    
    try:
        response = requests.post(BSPLAYER_API_LOGIN_URL, headers=headers, data=data, timeout=DEFAULT_REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)
        bsplayer_login_response_json = response.json()
        log.warning(f"DEBUG | [BSPlayer] | BSPlayer SearchSubtitles | URL: {response.url} | Status Code: {response.status_code} | bsplayer_login_response_json={bsplayer_login_response_json}")
    except Exception as e:
        log.warning(f'DEBUG | [BSPlayer] | BSPlayer SearchSubtitles | type: {type(e)} | Exception: {repr(e)}')
        return []
    
    token = bsplayer_login_response_json['data']
    data = {'handle':token,
          'movieHash':str(filehash),
          'languageId':'heb'
           }
    
    try:
        response = requests.post(BSPLAYER_API_SEARCH_URL, headers=headers, data=data, timeout=DEFAULT_REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise HTTPError for bad status codes (4xx, 5xx)
        bsplayer_search_response_json = response.json()
        log.warning(f"DEBUG | [BSPlayer] | BSPlayer SearchSubtitles | URL: {response.url} | Status Code: {response.status_code} | bsplayer_search_response_json={bsplayer_search_response_json}")
    except Exception as e:
        log.warning(f'DEBUG | [BSPlayer] | BSPlayer SearchSubtitles | type: {type(e)} | Exception: {repr(e)}')
        return []
    
    bsplayer_subtitles_list = []
    
    for items in bsplayer_search_response_json['data']:
    
        if 'subName' not in items:
            continue
            
        SubFileName = items['subName'].replace('.srt', '')

        # Define characters that might break the filename (It caused writing problem to MyTmp dir)
        characters_to_remove = '\\/:*?"<>|\''
        # Remove characters that might cause issues in the filename
        SubFileName = ''.join(c for c in SubFileName if c not in characters_to_remove)
        
        download_data={}
        download_data['url']=items['subDownloadLink']
        download_data['file_name']=SubFileName
        url = "plugin://%s/?action=download&download_data=%s&filename=%s&language=%s&source=bsplayer" % (MyScriptID,
                                                                que(json.dumps(download_data)),
                                                                que(SubFileName),
                                                                "Hebrew")
        json_data = {'url':url,
                     'label':"Hebrew",
                     'label2':site_id+' '+SubFileName,
                     'iconImage':"0",
                     'thumbnailImage':"he",
                     'hearing_imp':'false',
                     'site_id':site_id,
                     'sub_color':sub_color,
                     'filename':SubFileName,
                     'sync': 'true'}
                                 
        bsplayer_subtitles_list.append(json_data)
    

    global_var = bsplayer_subtitles_list
    
def download(download_data,MySubFolder):

    try:
        shutil.rmtree(MyTmp)
    except: pass
    
    xbmcvfs.mkdirs(MyTmp)
    log.warning(f'DEBUG | [BSPlayer] | BSPlayer download | download_data={download_data}')
    
        
    url = download_data['url']
    file_name = download_data['file_name']

    headers = {
        'User-Agent': 'BSPlayer/2.x (1022.12362)',
        'Content-Type': 'text/xml; charset=utf-8',
        'Connection': 'close',
    }
    
    response = requests.get(url, headers=headers, timeout=DEFAULT_REQUEST_TIMEOUT)
    

    archive_file = os.path.join(MyTmp, 'bs_Sub.xx')
    # Throw an error for bad status codes
    response.raise_for_status()
   
    with open(archive_file, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)
   
    dest=os.path.join(MySubFolder,file_name)
    g_extract(archive_file,dest,MySubFolder)
    return dest