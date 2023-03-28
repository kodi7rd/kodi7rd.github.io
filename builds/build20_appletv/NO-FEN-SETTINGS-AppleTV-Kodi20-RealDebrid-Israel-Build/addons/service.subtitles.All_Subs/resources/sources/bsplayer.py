import xbmcaddon,xbmcvfs,os,re,xbmc
global global_var,stop_all,site_id,sub_color#global
global_var=[]
from resources.modules import log
import requests,json,re,shutil
from resources.modules import cache
Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
from resources.modules.extract_sub import extract,g_extract
import urllib.parse
import struct

Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
que=urllib.parse.quote_plus
xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_bs'))

site_id='[Bs]'
sub_color='lightblue'

__soap_format = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" '
                       'xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" '
                       'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                       'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
                       'xmlns:ns1="{url}">'
        '<SOAP-ENV:Body SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            '<ns1:{action}>{params}</ns1:{action}>'
        '</SOAP-ENV:Body>'
    '</SOAP-ENV:Envelope>'
)

__headers = {
    'User-Agent': 'BSPlayer/2.x (1022.12362)',
    'Content-Type': 'text/xml; charset=utf-8',
    'Connection': 'close',
}

__subdomains = [1, 2, 3, 4, 5, 6, 7, 8, 101, 102, 103, 104, 105, 106, 107, 108, 109]

__64k = 65536
__longlong_format_char = 'q'
__byte_size = struct.calcsize(__longlong_format_char)
from xml.dom import minidom

def parse_element(element):
    dict_data = dict()
    if element.nodeType == element.TEXT_NODE:
        dict_data['data'] = element.data
    if element.nodeType not in [element.TEXT_NODE, element.DOCUMENT_NODE, 
                                element.DOCUMENT_TYPE_NODE]:
        for item in element.attributes.items():
            dict_data[item[0]] = item[1]
    if element.nodeType not in [element.TEXT_NODE, element.DOCUMENT_TYPE_NODE]:
        for child in element.childNodes:
            child_name, child_dict = parse_element(child)
            if child_name in dict_data:
                try:
                    dict_data[child_name].append(child_dict)
                except AttributeError:
                    dict_data[child_name] = [dict_data[child_name], child_dict]
            else:
                dict_data[child_name] = child_dict 
    return element.nodeName, dict_data

def __sum_64k_bytes(file, result):
    range_value = __64k / __byte_size
    
    range_value = round(range_value)

    for _ in range(range_value):
        try: chunk = file.readBytes(__byte_size)
        except: chunk = file.read(__byte_size)
        (value,) = struct.unpack(__longlong_format_char, chunk)
        result.filehash += value
        result.filehash &= 0xFFFFFFFFFFFFFFFF
def hashFile(): 
      
                 
                longlongformat = '<q'  # little-endian long long
                bytesize = int(struct.calcsize(longlongformat) )
                    
                f = xbmcvfs.File( xbmc.Player().getPlayingFile())
                    
                filesize = f.size()
                hash = filesize 
                    
                if filesize < 65536 * 2: 
                       return "SizeError" 
                 
                for x in range(int(65536/bytesize)): 
                        #buffer = f.read(bytesize)
                        try: buffer = f.readBytes(bytesize)
                        except: buffer = f.read(bytesize)
        
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                         
    
                f.seek(max(0,filesize-65536),0) 
                for x in range(int(65536/bytesize)): 
                        try: buffer = f.readBytes(bytesize)
                        except: buffer = f.read(bytesize)
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
                f.close() 
                returnedhash =  "%016x" % hash 
                return returnedhash ,filesize
def __set_size_and_hash():
    

    f = xbmcvfs.File( xbmc.Player().getPlayingFile())

    try:
        filesize = f.size()

        # used for mocking
        try:
            filehash = f.hash()
            return
        except: pass

        if filesize < __64k * 2:
            return

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
def __get_url():
    from datetime import datetime
    time_seconds = datetime.now().second
    subdomain = __subdomains[time_seconds % len(__subdomains)]

    return "http://s%s.api.bsplayer-subtitles.com/v1.php" % subdomain

def __get_request( action, params):
    
    
    url = __get_url( )
    headers = __headers.copy()
    headers['SOAPAction'] = '"%s#%s"' % (url, action)
    request = {
        'method': 'POST',
        'url': url,
        'data': __soap_format.format(url=url, action=action, params=params),
        'headers': headers,
        'timeout':5,
        
    }
    
    return request
def __parse_response( response):
    dom=minidom.parseString(response.strip())
    x=json.dumps(parse_element(dom), sort_keys=True, indent=4)
    x=json.loads(x)
    return x[1]['SOAP-ENV:Envelope']['SOAP-ENV:Body']
    '''
    try:
        tree = ElementTree.fromstring(response.strip())
        return tree.find('.//return')
    except Exception as exc:
        log.warning('%s - %s' % ("Bs", exc))
        return None
    '''
def get_subs(item,file_name=""):
    log.warning('Searching Bsplayer')
    global global_var
    if not xbmc.Player().isPlaying():
        return []
    filehash,filesize=__set_size_and_hash()
    log.warning(filehash)
    log.warning(filesize)
    headers={
        'User-Agent': 'BSPlayer 3.0/10394',
        'Accept': '*/*', 
        'Accept-Encoding': '*', 

        'Content-Type': 'application/x-www-form-urlencoded'
        }
    data={'AppID':'BASPlayer v3'}
    x=requests.post('http://r4.api.subs.bplayer.org/subs-rest/login',headers=headers,data=data).json()
    log.warning(x)
    token=x['data']
    
    data={'handle':token,
          'movieHash':str(filehash),
          #'movieSize':filesize,
          'languageId':'heb'
          }
    
    x=requests.post('http://r4.api.subs.bplayer.org/subs-rest/searchSubtitles',headers=headers,data=data).json()
    results_list=[]
    for items in x['data']:
        name = items['subName']
        lang_id = items['subLang']
 
        
        download_data={}
        download_data['url']=items['subDownloadLink']
        download_data['file_name']=name
        if file_name==name:
            return items['subDownloadLink']
        name=name.replace('srt','')
        url = "plugin://%s/?action=download&download_data=%s&filename=%s&language=%s&source=bsplayer" % (MyScriptID,
                                                                que(json.dumps(download_data)),
                                                                que(name),
                                                                "Hebrew")
        json_data={'url':url,
                                 'label':"Hebrew",
                                 'label2':site_id+name,
                                 'iconImage':"0",
                                 'thumbnailImage':"he",
                                 'hearing_imp':'false',
                                 'site_id':site_id,
                                 'sub_color':sub_color,
                                 'filename':name,
                                 'sync': 'true'}
        results_list.append(json_data)
    


    global_var=results_list
def download(download_data,MySubFolder):
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)
    log.warning(download_data)
    
        
    url=download_data['url']
    file_name=download_data['file_name']
    url=get_subs("",file_name)
    log.warning('New Url:'+str(url))
    response = requests.get(url, headers=__headers)
    

    

    archive_file = os.path.join(MyTmp, 'bs_Sub.xx')
    # Throw an error for bad status codes
    response.raise_for_status()
   
    with open(archive_file, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)
   
    dest=os.path.join(MySubFolder,file_name)
    g_extract(archive_file,dest,MySubFolder)
    return dest