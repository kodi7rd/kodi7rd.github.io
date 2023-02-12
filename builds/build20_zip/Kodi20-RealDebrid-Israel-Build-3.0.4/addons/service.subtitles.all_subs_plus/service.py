# -*- coding: utf-8 -*-
import sys,logging,unicodedata,urllib,zlib,json,os,xbmcvfs,zipfile,re,xbmcgui,xbmcaddon,contextlib,xbmc,hashlib,shutil,threading

import linecache
import PTN,base64
try:
    import HTMLParser
    html_parser = HTMLParser.HTMLParser()
    from urllib import urlretrieve
    from urllib import  unquote_plus, unquote, urlopen, quote
except:
    import html
    from urllib.request import urlretrieve
    from urllib.parse import  unquote_plus, unquote, quote, quote_plus
from os import path

from json import loads, load

import time
from unicodedata import normalize


import cgi

from xbmcaddon import Addon
from xbmcplugin import endOfDirectory, addDirectoryItem
from xbmcgui import ListItem, Dialog
from srt2ass import srt2ass
from xbmcvfs import listdir, exists
from xbmc import  executebuiltin, getInfoLabel, executeJSONRPC, Player, sleep, log, getCondVisibility
from re import sub
from subscene import download_subscene
#from  Subscene import search_subscene,download_subscene
from opensubtitle import Search_opensubtitle,Download_opensubtitle
import cache
import socket,xbmc
from myLogger import myLogger
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
if KODI_VERSION<=18:
    xbmc_tranlate_path=xbmc.translatePath
else:
    import xbmcvfs
    xbmc_tranlate_path=xbmcvfs.translatePath
    
user_dataDir = xbmc_tranlate_path(xbmcaddon.Addon().getAddonInfo("profile"))
if not os.path.exists(user_dataDir):
     os.makedirs(user_dataDir)
'''
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmc_tranlate_path(addonInfo('profile')).decode('utf-8')
cacheFile = os.path.join(dataPath, 'subs_history.db')
xbmcvfs.mkdir(dataPath)
dbcon = database.connect(cacheFile)
dbcur = dbcon.cursor()


dbcur.execute("CREATE TABLE IF NOT EXISTS AllData ( ""title TEXT, ""episode TEXT, ""season TEXT, ""year TEXT, ""tvshow TEXT, ""file_original_path TEXT, ""full_path TEXT, ""subs TEXT);")
try:
    dbcur.execute("VACUUM 'AllData';")
    dbcur.execute("PRAGMA auto_vacuum;")
    dbcur.execute("PRAGMA JOURNAL_MODE=MEMORY ;")
    dbcur.execute("PRAGMA temp_store=MEMORY ;")
except:
 pass
dbcon.commit()
'''

__addon__ = xbmcaddon.Addon()

#reload(sys)  
#sys.setdefaultencoding('utf8')
from yify import search_yify
socket.setdefaulttimeout(10)
action=None
searchstring=None
myLogger('Subs On')
all_setting=[]
location=0
last_sub_download=''

regexHelper = re.compile('\W+', re.UNICODE)
running=0
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
if KODI_VERSION>18:
    
    class Thread (threading.Thread):
       def __init__(self, target, *args):
        super().__init__(target=target, args=args)
       def run(self, *args):
          
          self._target(*self._args)
else:
   
    class Thread(threading.Thread):
        def __init__(self, target, *args):
           
            self._target = target
            self._args = args
            
            
            threading.Thread.__init__(self)
            
        def run(self):
            
            self._target(*self._args)
global links_wizdom,links_subcenter,links_local,links_ktuvit,links_open,imdbid,sc_subtitle
imdbid=''
links_wizdom=[]
links_ktuvit=[]
links_open=[]
base_aa='aHR0cHM6Ly9yb2NrLnNlZWRob3N0LmV1L2tjYXQxMjMvSHViLw=='
links_subcenter=[]
links_local=[]
sc_subtitle=[]

prefix_wizdom='[Wiz]'
prefix_ktuvit='[Kt]'
prefix_open='[OpS]'
prefix_acat='[AC]' #AA_CAT
prefix_subscene='[SS]'
prefix_local='[Loc]'

MyAddon = Addon()
__profile__ = xbmc_tranlate_path(MyAddon.getAddonInfo('profile'))
MyScriptID = MyAddon.getAddonInfo('id')
MyVersion = MyAddon.getAddonInfo('version')
__scriptid__ = MyAddon.getAddonInfo('id')
__scriptname__ = MyAddon.getAddonInfo('name')
MyTmp_aa = xbmc_tranlate_path(os.path.join(__profile__, 'aa_buff'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_download'))
MySubFolder = xbmc_tranlate_path(path.join(MyTmp, 'subs'))
MyName = MyAddon.getAddonInfo('name')
MyLang = MyAddon.getLocalizedString
__settings__ = xbmcaddon.Addon(id=MyScriptID)
cache_list_folder=(xbmc_tranlate_path(os.path.join(__profile__, 'cache_list_folder')))
addon_font_path= MyAddon.getAddonInfo('path')+'\\fonts'
fonts_folder=xbmc_tranlate_path("special://home/")+'media\\fonts'

__language__ = MyAddon.getLocalizedString
__temp__ = (xbmc_tranlate_path(os.path.join(__profile__, 'temp_jsons')))
__last__ = (xbmc_tranlate_path(os.path.join(__profile__, 'last')))
__history__ = (xbmc_tranlate_path(os.path.join(__profile__, '__history__')))
BASE_URL = "http://www.cinemast.org/he/cinemast/api/"

try:
  if not path.exists(cache_list_folder):
    xbmcvfs.mkdirs(cache_list_folder)
except: pass
try:
  if not path.exists(fonts_folder):
    xbmcvfs.mkdirs(fonts_folder)
  src=addon_font_path
  dst=fonts_folder
  for item in os.listdir(src):

      if not path.exists(str(dst)+'\\'+str(item)):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        shutil.copy2(s, d)
except:
  pass


try:
  if not path.exists(__temp__):
    xbmcvfs.mkdirs(__temp__)
except: pass

id_all_collection=[]
'''
class popupBtns(xbmcgui.WindowDialog):
    def __init__(self, title='', btns=[], width=1):
        self.w = width
        self.selected = -1
        self.btns = btns
        self.btnCnts = [0]
        for i in range(len(btns)-1): # There has to be a better way to do this. zeros doesn't work...
            self.btnCnts.append(0)
  
#   def onInit(self):
        w = self.w      
        w = int(self.getWidth()*width)
        pad = self.getHeight()/100
        hCnt = 5*pad
        yo = pad
  
        h = len(self.btns) * (hCnt + 5) + yo
        mediaDir = os.path.join(os.getcwd().replace(";",""),'resources','skins','DefaultSkin','media')
        rw = self.getWidth()
        rh = self.getHeight()
        x = rw/2 - w/2
        y = rh/2 - h/2
  
        # Background
        self.imgBg = xbmcgui.ControlImage(0+x-4*pad,0+y-4*pad,w+8*pad,h+8*pad, os.path.join(mediaDir,'gs-bg-menu.png'))
        self.addControl(self.imgBg)
  
        i = 0
        while i < len(self.btns):
            self.btnCnts[i] = xbmcgui.ControlButton(pad+x, yo+y, w-2*pad, hCnt, str(self.btns[i]), os.path.join(mediaDir,'button_focus.png'), '', font='font12', textColor='0xFFFFFFFF', alignment=2)
            self.addControl(self.btnCnts[i])
            yo += hCnt + 5
            i += 1
  
        self.setFocus(self.btnCnts[0])
  
    def onControl(self, action):
        pass
  
    def onAction(self, action):
        if action == 10:
            self.close()    
        elif (action == 3) or (action == 4) or (action == 7) or (action == 9):
            try:    
                cnt = self.getFocus()
            except:
                self.setFocus(self.btnCnts[0])
                return None
  
            d = 0
            if action == 3: # Up
                d = -1
            elif action == 4: # Down
                d = 1
            l = len(self.btnCnts)
            for i in range(l):
                if self.btnCnts[i] == cnt:
                    if action == 7: # Select
                        self.selected = i
                        self.close()
                    elif action == 9: # Back
                        self.close()
                    elif i+d > l-1:
                        self.setFocus(self.btnCnts[0])
                    elif i+d < 0:
                        self.setFocus(self.btnCnts[l-1])
                    else:
                        self.setFocus(self.btnCnts[i+d])
  
'''
class subtitle_cache_next():
    
    def set(self, table,value):
        try:
            from sqlite3 import dbapi2 as database
        except:
            from pysqlite2 import dbapi2 as database
        cacheFile=os.path.join(user_dataDir,'database.db')
        dbcon = database.connect(cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s ( ""data TEXT);" % table)
        
        dbcur.execute("DELETE FROM %s"%table)
        code=(base64.b64encode(value.encode("utf-8"))).decode("utf-8")
        dbcur.execute("INSERT INTO %s Values ('%s')"%(table,code))
        dbcon.commit()
    
        dbcur.close()
        dbcon.close()
    def get(self, table):
        try:
            from sqlite3 import dbapi2 as database
        except:
            from pysqlite2 import dbapi2 as database
        cacheFile=os.path.join(user_dataDir,'database.db')
        dbcon = database.connect(cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s ( ""data TEXT);" % table)
        

        dbcur.execute("SELECT * FROM ('%s')"%(table))
        match = dbcur.fetchone()
        dbcur.close()
        dbcon.close()
        
        if match!=None:
            return base64.b64decode(match[0])
class subtitle_cache():
    
    def set(self, table,value):
        try:
            from sqlite3 import dbapi2 as database
        except:
            from pysqlite2 import dbapi2 as database
        cacheFile=os.path.join(user_dataDir,'database.db')
        dbcon = database.connect(cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s ( ""data TEXT);" % table)
        
        dbcur.execute("DELETE FROM %s"%table)
        code=(base64.b64encode(value.encode("utf-8"))).decode("utf-8")
        dbcur.execute("INSERT INTO %s Values ('%s')"%(table,code))
        dbcon.commit()
    
        dbcur.close()
        dbcon.close()
    def get(self, table):
        try:
            from sqlite3 import dbapi2 as database
        except:
            from pysqlite2 import dbapi2 as database
        cacheFile=os.path.join(user_dataDir,'database.db')
        dbcon = database.connect(cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s ( ""data TEXT);" % table)
        

        dbcur.execute("SELECT * FROM ('%s')"%(table))
        match = dbcur.fetchone()
        dbcur.close()
        dbcon.close()
        
        if match!=None:
            return base64.b64decode(match[0])
    def delete(self, table):
        try:
            from sqlite3 import dbapi2 as database
        except:
            from pysqlite2 import dbapi2 as database
        cacheFile=os.path.join(user_dataDir,'database.db')
        dbcon = database.connect(cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s ( ""data TEXT);" % table)
        

        dbcur.execute("DELETE FROM %s"%(table))
        
        dbcur.close()
        dbcon.close()
def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    try:
      myLogger('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj), logLevel=xbmc.LOGERROR)     
      return "Error"
    except:
      return "Error"



def notify(msg_id):
    xbmc.executebuiltin(u'Notification(%s,%s)' % (__scriptname__, __language__(msg_id)))
def notify2(msg_id,all_setting):
    if all_setting["popup"]=="true":
      xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, msg_id)))
def login( notify_success=True):
        
  
        email = all_setting["Email"]
        password = all_setting["Password"]
        if email=='' or password=='':
          __settings__.openSettings()
          email = all_setting["Email"]
          password = all_setting["Password"]
        post_data = {'username': email, 'password': password}
        content = urlHandler.request(BASE_URL + "login/", post_data)

        if content['result'] == 'success':
            if notify_success:
                notify(32010)

            del content["result"]
            return content
        else:
            notify(32009)
            return None
        
def get_user_token( force_update=False):
        if force_update:
            subtitle_cache().delete('credentials')

        results = subtitle_cache().get('credentials')
        if results:
            results = json.loads(results)
        else:
            results = login(False)
            if results:
                subtitle_cache().set('credentials', json.dumps(results))
        
        return results
        
def convert_to_utf(file):
    try:
        with codecs.open(file, "r", "cp1255") as f:
            srt_data = f.read()

        with codecs.open(file, 'w', 'utf-8') as output:
            output.write(srt_data)
    except: pass  

'''
def take_title_from_focused_item():
    labelType = xbmc.getInfoLabel("ListItem.DBTYPE")  # movie/tvshow/season/episode
    labelMovieTitle = xbmc.getInfoLabel("ListItem.OriginalTitle")
    labelYear = xbmc.getInfoLabel("ListItem.Year")
    labelTVShowTitle = xbmc.getInfoLabel("ListItem.TVShowTitle")
    labelSeason = xbmc.getInfoLabel("ListItem.Season")
    labelEpisode = xbmc.getInfoLabel("ListItem.Episode")
    isItMovie = xbmc.getCondVisibility("Container.Content(movies)") or labelType == 'movie'
    isItEpisode = xbmc.getCondVisibility("Container.Content(episodes)") or labelType == 'episode'

    title = 'SearchFor...'
    if isItMovie and labelMovieTitle and labelYear:
        title = labelMovieTitle + " " + labelYear
    elif isItEpisode and labelTVShowTitle and labelSeason and labelEpisode:
        title = ("%s S%.2dE%.2d" % (labelTVShowTitle, int(labelSeason), int(labelEpisode)))

    return title
'''

def getOriginalTitle(): ###### burekas

    if xbmc.getInfoLabel("VideoPlayer.TVshowtitle").isascii():
        return normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))  # Show

    #First, check if database has the original title.
    labelTVShowTitle = getTVshowOriginalTitleByJSONandDBid("playing")    ##using kodi database json
    #If not, try get the original title by using tmdb api
    if (labelTVShowTitle == "" or not labelTVShowTitle.isascii()):
        labelTVShowTitle = getTVshowOriginalTitleByTMDBapi("playing")  ##New way using tmdb api

    return labelTVShowTitle
    
def takeTitleFromFocusedItem(type="movie"): ###### burekas
    labelMovieTitle = xbmc.getInfoLabel("ListItem.OriginalTitle")
    labelYear = xbmc.getInfoLabel("ListItem.Year")
    labelTVShowTitle = xbmc.getInfoLabel("ListItem.TVShowTitle") #xbmc.getInfoLabel("ListItem.OriginalTitle")
    labelSeason = xbmc.getInfoLabel("ListItem.Season")
    labelEpisode = xbmc.getInfoLabel("ListItem.Episode")
    labelType = xbmc.getInfoLabel("ListItem.DBTYPE")  #movie/tvshow/season/episode	
    isItMovie = labelType == 'movie' or xbmc.getCondVisibility("Container.Content(movies)")
    isItEpisode = labelType == 'episode' or xbmc.getCondVisibility("Container.Content(episodes)")
    labelDBID = xbmc.getInfoLabel("ListItem.DBID")

    #If item is TVShow and in the library => When titles are not in english
    if isItEpisode and type == 'tvshow' and labelDBID != "":
        #First, check if database has the original title.
        labelTVShowTitle = getTVshowOriginalTitleByJSONandDBid()  ##using kodi database json
        #If not, try get the original title by using tmdb api
        if (labelTVShowTitle == "" or not labelTVShowTitle.isascii()):
            labelTVShowTitle = getTVshowOriginalTitleByTMDBapi()  ##New way using tmdb api

    title = 'SearchFor...'
    if isItMovie and labelMovieTitle and labelYear:
        title = ("%s %s" % (labelMovieTitle, labelYear)) if type == 'movie' else '' ###### burekas
    elif isItEpisode and labelTVShowTitle and labelSeason and labelEpisode:
        title = ("%s S%.2dE%.2d" % (labelTVShowTitle, int(labelSeason), int(labelEpisode))) if type == 'tvshow' else '' ###### burekas

    return title

def getTVshowOriginalTitleByJSONandDBid(source="notPlaying"): ###### burekas
    try:
        if (source=="notPlaying"):
            labelDBID = xbmc.getInfoLabel("ListItem.DBID")
        else:
            labelDBID = xbmc.getInfoLabel("VideoPlayer.DBID")        
        
        originalShowTitle = ''
        
        labelDBID = xbmc.getInfoLabel("ListItem.DBID")
        requestEpisodeDetails = {"jsonrpc": "2.0", "id": 1 , "method": "VideoLibrary.GetEpisodeDetails", "params": {"episodeid": int(labelDBID), "properties": ["tvshowid"]}}
        resultsEpisodeDetails = json.loads(xbmc.executeJSONRPC(json.dumps(requestEpisodeDetails)))
        
        tvshowDBID = resultsEpisodeDetails["result"]["episodedetails"]["tvshowid"]
        
        requestTVShowDetails = {"jsonrpc": "2.0", "id": 1 , "method": "VideoLibrary.GetTVShowDetails", "params": {"tvshowid": int(tvshowDBID), "properties": ["originaltitle"]}}
        resultsTVShowDetails = json.loads(xbmc.executeJSONRPC(json.dumps(requestTVShowDetails)))
               
        tvshowOriginalTitle = resultsTVShowDetails["result"]["tvshowdetails"]["originaltitle"]
        
        originalShowTitle = tvshowOriginalTitle

        return originalShowTitle

    except Exception as err:
        myLogger('Caught Exception: error getTVshowOriginalTitleByJSONandDBid: %s' % format(err), logLevel=xbmc.LOGERROR)
        originalShowTitle = ''			
        return originalShowTitle


def getTVshowOriginalTitleByTMDBapi(source="notPlaying"): ###### burekas
    try:
        if (source=="notPlaying"):
            labelTVShowTitle = xbmc.getInfoLabel("ListItem.TVShowTitle")
            labelYear = xbmc.getInfoLabel("ListItem.Year")
        else:
            labelTVShowTitle = xbmc.getInfoLabel("VideoPlayer.TVShowTitle")
            labelYear = xbmc.getInfoLabel("VideoPlayer.Year")

        originalTitle = ''

        tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'
        filename = 'subs.search.tmdb.%s.%s.%s.json' % ("tv",lowercase_with_underscores(labelTVShowTitle), labelYear)
        
        if int(labelYear) > 0:
            #url = "http://api.tmdb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=en" % ("tv",tmdbKey, labelTVShowTitle, labelYear)
            url = "http://api.themoviedb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=en" % ("tv",tmdbKey, labelTVShowTitle, labelYear)
        else:
            #url = "http://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en" % ("tv",tmdbKey, labelTVShowTitle)
            url = "http://api.themoviedb.org/3/search/%s?api_key=%s&query=%s&language=en" % ("tv",tmdbKey, labelTVShowTitle)
        
        myLogger("searchTMDB for original tv title: %s" % url)
        
        json_results = get_TMDB_data_popularity_and_votes_sorted(url,filename)
        
        '''
        json = caching_json(filename,url)

        resultsLen = len(json["results"])			
        itemIndex = -1
        voteCountMax = 0			
        popularityMax = 0						
        itemIndexMax = 0			
        for item in json['results']:
            itemIndex = itemIndex+1				
            if (item['vote_count'] > voteCountMax and item['popularity'] > popularityMax):
                voteCountMax = item['vote_count']
                popularityMax = item['popularity']						
                itemIndexMax = itemIndex
    
        if resultsLen > 0 :			
            #originalTitle = json["results"][itemIndexMax]["original_name"]
            originalTitle = json["results"][itemIndexMax]["name"]
		'''
        
        try:    originalTitle = json_results[0]["name"]
        except:
            myLogger( "[%s]" % (e,))
            return ''         
               
        return originalTitle
    
    except Exception as err:
        myLogger('Caught Exception: error searchTMDB: %s' % format(err), logLevel=xbmc.LOGERROR)
        originalTitle = ''		
        return originalTitle

def lowercase_with_underscores(_str):   ####### burekas
    return unicodedata.normalize('NFKD', _str).encode('utf-8','ignore').decode('utf-8')
    #return normalize('NFKD', (_str)).encode('utf-8', 'ignore')
    #return normalize('NFKD', str(str(str, 'utf-8'))).encode('utf-8', 'ignore')

def caching_json(filename, url):   ####### burekas
    from requests import get

    if (__addon__.getSetting( "json_cache" ) == "true"):
        json_file = path.join(__temp__, filename) 
        if not path.exists(json_file) or not path.getsize(json_file) > 20 or (time.time()-path.getmtime(json_file) > 30*60): 
            data = get(url, verify=False)
            open(json_file, 'wb').write(data.content)
        if path.exists(json_file) and path.getsize(json_file) > 20:
            with open(json_file,'r',encoding='utf-8') as json_data:
                json_object = load(json_data)
            return json_object
        else:
            return {}
            
    else:
        try:
          json_object = get(url).json()
        except:
          json_object = {}
          pass
        return json_object        
    
def Download_aa(url,mode_subtitle):
    import requests
    myLogger('Download aa')
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)
        
    subtitle_list=[]
    archive_file = path.join(MyTmp, 'aa_sub.srt')

    f_url=unquote_plus(url).strip()
    myLogger('f_url:'+f_url)
    headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Authorization': 'Basic YWFhOmFhYQ==',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'utf-8',
    'Accept-Language': 'en-US,en;q=0.9',
    }
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    #'Referer': 'http://185.165.240.137:8080/SUB/',
    'Upgrade-Insecure-Requests': '1',
    'Accept-Encoding': 'utf-8',
    }
    
    r=requests.get(f_url,headers=headers,stream=True)
    params = cgi.parse_header(r.headers.get('content-type'))[0]
    server_encoding = ('charset' in params) and params['charset'].strip("'\"") or None
    r.encoding = server_encoding or r.apparent_encoding
    text = r.text

    #file = open(archive_file, 'w')
    if KODI_VERSION>18:
        with open(archive_file, mode="w", encoding="utf8") as f:
             f.write(text)
    else:
        with open(archive_file, mode="w") as f:
             f.write(text)
    #file.write(text) 
    #file.close()
    #urlretrieve(z, archive_file)
    subtitle_list.append(archive_file)
    if mode_subtitle>1:
      return subtitle_list
    else:
     #xbmc.Player().setSubtitles(subtitle_list[0])

     if len (subtitle_list)>0:
       sub_result=subtitle_list[0]
     else:
       sub_result='0'
     return sub_result
     
def getDomainWizdom(): 
	from requests import get
	try:
		myDomain = str(get('https://pastebin.com/raw/1vbRPSGh').text)
		return myDomain
	except Exception as err:
		myLogger('Caught Exception: error in finding getDomain: %s' % format(err))
		return "wizdom.xyz" # "lolfw.com"

myWizdomDomain = getDomainWizdom() + "/api"
         
def download(id,language,key,filename,mode_subtitle):
    global all_setting
    try:
        from zfile_18 import ZipFile
    except:
        from zipfile import ZipFile

    
    import requests
    try:
     temp=[]

     if id=="LOCAL FILE":
       temp.append(filename)
    
       return temp," "

     
     if filename!='':
    
        subtitle_list = []
        exts = [".srt", ".sub"]
   
        zip_filename = os.path.join(__temp__, "subs.zip")

        
        try:
            shutil.rmtree(__temp__)
        except: pass
        xbmcvfs.mkdirs(__temp__)

        query = {"v": filename,"key": key,"sub_id": id}

        user_token = get_user_token()

        url = BASE_URL + "subtitle/download/" + language + "/?" + urllib.urlencode(query)

        f = urlHandler.request(url, user_token)

        if f==None:
          if mode_subtitle>1:
            return '',False
          else:
             return False,'NO'
        if len(f)<100:
            if mode_subtitle==3:
              xbmcgui.Dialog().ok("Subscenter",str(f))
            else:
              xbmcgui.Dialog().notification('Subcenter Download', str(f), xbmcgui.NOTIFICATION_INFO,1000 )
            return False,'NO'
        else:
            with open(zip_filename, "wb") as subFile:
                subFile.write(f)
            subFile.close()
            xbmc.sleep(500)
            try:
                with contextlib.closing(ZipFile(zip_filename , "r")) as z:
                    z.extractall(__temp__)
            except:
                with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                    zip_ref.extractall(__temp__)
            #with zipfile.ZipFile(zip_filename) as zf:
            #    zf.extractall(__temp__)
        file_list=(os.listdir(__temp__ ))
     
        for file in file_list:
            full_path = os.path.join(__temp__, file)

            if os.path.splitext(full_path)[1] in exts:
              subtitle_list.append(full_path)

        if mode_subtitle>1:
          return subtitle_list," "
        else:
         #xbmc.Player().setSubtitles(subtitle_list[0])

         if len (subtitle_list)>0:
           sub_result=subtitle_list[0]
         else:
           sub_result='0'
         return True,sub_result
     else:

        try:
            shutil.rmtree(MyTmp)
        except: pass
        xbmcvfs.mkdirs(MyTmp)
        try:
            shutil.rmtree(MySubFolder)
        except: pass
        xbmcvfs.mkdirs(MySubFolder)



        subtitle_list = []
        exts = [".srt", ".sub", ".str"]

        if 'yify$$$' in id:
            archive_file = path.join(MyTmp, 'yify.sub.'+id.replace('yify$$$','').replace('/subtitles/','')+'.zip')


            if not path.exists(archive_file):
                urlretrieve("https://www.yifysubtitles.org/subtitle/"+id.replace('yify$$$','').replace('/subtitles/','')+".zip", archive_file)
                
        elif 'FIRSTH$$$' in id:
           font_c="0"
           size=0
           
           o_id=id
           id=id.split("$$$")[1].split("$$$")[0]
           login_cook=cache.get(get_login_cook,1, table='subs')
          
           f_id=o_id.split("$$$")[2]
           headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.5',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.ktuvit.me',
                'Connection': 'keep-alive',
                'Referer': 'https://www.ktuvit.me/MovieInfo.aspx?ID='+f_id,
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'TE': 'Trailers',
            }

           data = id
           response = requests.post('https://www.ktuvit.me/Services/ContentProvider.svc/RequestSubtitleDownload', headers=headers, cookies=login_cook, data=data).json()
         
           
           headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Referer': 'https://www.ktuvit.me/MovieInfo.aspx?ID='+f_id,
                'Upgrade-Insecure-Requests': '1',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'TE': 'Trailers',
            }

           params = (
                ('DownloadIdentifier', json.loads(response['d'])['DownloadIdentifier']),
            )

           response = requests.get('https://www.ktuvit.me/Services/DownloadFile.ashx', headers=headers, params=params, cookies=login_cook)
           headers=(response.headers)
          
           file_name=headers['Content-Disposition'].split("filename=")[1]
          
           archive_file = path.join(MyTmp, file_name)
            # Throw an error for bad status codes
           response.raise_for_status()
           subtitle_list=[]
           with open(archive_file, 'wb') as handle:
                for block in response.iter_content(1024):
                    handle.write(block)
           subtitle_list.append(archive_file)
           if mode_subtitle==3:
             return subtitle_list,True
           else:
             return True,subtitle_list
        else:
            archive_file = path.join(MyTmp, 'wizdom.sub.'+id+'.zip')
 
            if not path.exists(archive_file):
                urlretrieve("http://%s/"%format(myWizdomDomain)+"/files/sub/"+id, archive_file)

        #executebuiltin(('XBMC.Extract("%s","%s")' % (archive_file, MySubFolder)).encode('utf-8'), True)
        try:
            with contextlib.closing(ZipFile(archive_file , "r")) as z:
                z.extractall(MySubFolder)
        except:
            with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                zip_ref.extractall(MySubFolder)
                    
        
        for file_ in listdir(MySubFolder)[1]:
            ufile = file_
            file_ = path.join(MySubFolder, ufile)
            if path.splitext(ufile)[1] in exts:
                convert_to_utf(file_)
                subtitle_list.append(file_)

        if mode_subtitle>1:
          return subtitle_list," "
        else:
         if len (subtitle_list)>0:
           sub_result=subtitle_list[0]
         else:
           sub_result='0'
         #xbmc.Player().setSubtitles(subtitle_list[0])
         return True,sub_result
    except Exception as e:
        import linecache
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        
        myLogger('ERROR IN Download:'+str(lineno)+',Error:'+str(e), logLevel=xbmc.LOGERROR)
        notify2('[COLOR red] Error: [\COLOR]'+str(lineno)+' E:'+str(e),all_setting)
    if mode_subtitle>1:
        return '',False
    else:
        return False,'NO'


def getParams(arg):
    param=[]
    paramstring=arg
    if len(paramstring)>=2:
        params=arg
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:    
                param[splitparams[0]]=splitparams[1]
                            
    return param

def getParam(name,params):
    try:
        return unquote_plus(params[name])
    except:    pass

def GetWizJson(imdb,mode_subtitle,season=0,episode=0,version=0):
    global links_wizdom
    filename = 'subs.search.wizdom.%s.%s.%s.json'%(imdb,season,episode)
    url = "http://%s/search?action=by_id&imdb=%s&season=%s&episode=%s&version=%s" % (myWizdomDomain, imdb, season, episode, version)

    myLogger("GetWizJson url: " + repr(url))
       
    json_object = caching_json(filename,url)

    subs_rate = []
    subtitle=' '
    x=1
    id_all_collection=[]
    subtitle_list=[]
    if json_object!=0:
        for item_data in json_object:
            try:
                listitem = ListItem(label= "Hebrew",label2= str(x)+'. '+prefix_wizdom+' '+item_data["versioname"],thumb="he",icon="%s"%("{:.0f}".format(item_data["score"]/2)))
            except:
                listitem = ListItem(label= "Hebrew",label2= str(x)+'. '+prefix_wizdom+' '+item_data["versioname"])
            if int(item_data["score"])>8:
                listitem.setProperty("sync", "true")
            url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, item_data["versioname"], item_data["id"])
          
            json_data={'url':url,
                             'label':"Hebrew",
                             'label2':str(x)+'. '+prefix_wizdom+' '+item_data["versioname"],
                             'iconImage':"%s"%("{:.0f}".format(item_data["score"]/2)),
                             'thumbnailImage':"he",
                             'hearing_imp':'false',
                             'sync': 'false'}
            if item_data["id"] not in id_all_collection:
                id_all_collection.append(item_data["id"])         
                
                subtitle_list.append(json_data)
                links_wizdom=subtitle_list
                x=x+1
    
    if (json_object)==0:
      return 0,' ',subtitle_list
    else:
 
      return len(json_object),subtitle,subtitle_list

'''
def ManualSearch(title,option,mode_subtitle,imdb_id,item):  #burekas - not in use, need to be tested
    title=title.replace("&"," and ")
    filename = 'subs.search.wizdom.%s.json'%(quote(title))

    #url = "http://api.wizdom.xyz/search.manual.php?filename=%s"%(lowercase_with_underscores(title))
    url = "http://%s/search?action=by_id&imdb=%s" % (myWizdomDomain, imdb_id)    

    subtitle_list=[]
    try:

        json = caching_json(filename,url)

        if "season" not in json:
          json['season']=0

        if "episode" not in json:
          json['episode']=0
        if json["type"]=="episode":
            json['year']=0

            #imdb_id = SearchMovie(str(json['title']),json['year'],item,mode_subtitle)
            imdb_id = searchForIMDBID(str(json['title'],item)
            if 'tt' not in imdb_id:
              imdb_id = urllib.request.urlopen("http://api.wizdom.xyz/search.tv.php?name="+quote(json['title'])).read()

            if imdb_id!='' and imdb_id!=0 and option==1:
                num_of_subs,subtitle,subtitle_list=GetWizJson(str(imdb_id),mode_subtitle,json['season'],json['episode'],lowercase_with_underscores(title))

        elif json["type"]=="movie":
            if "year" in json:
                #imdb_id = SearchMovie(str(json['title']),json['year'],item,mode_subtitle)
                imdb_id = searchForIMDBID(str(json['title'],item)
            else:
                json['year']=0
                item['year']=0000
                #imdb_id = SearchMovie(str(json['title']),0,item,mode_subtitle)
                imdb_id = searchForIMDBID(str(json['title'],item)
            if imdb_id and option==1:
      
                num_of_subs,subtitle,subtitle_list=GetWizJson(str(imdb_id),mode_subtitle,0,0,lowercase_with_underscores(title))

        return(json['title'],json['year'],imdb_id,json['season'],json['episode'],subtitle_list,num_of_subs,subtitle)
    except:    pass
'''

#///////////////////////////////////////Subcenter////////////////////////////////////////////////
def get_aa_server(url,it):
    import requests
    try:
        shutil.rmtree(MyTmp_aa)
    except: pass
    xbmcvfs.mkdirs(MyTmp_aa)
    
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
           
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
    x=requests.get(url,headers=headers).content

    if it == 'tv':
        fi_name='aa_tv.txt'
    else:
        fi_name='aa_movie.txt'
        
    output_file=os.path.join(MyTmp_aa,fi_name)
    
    file = open(output_file, 'w')
  
    file.write(str(x))
    file.close()
    return output_file

def aa_subs_old(item,mode_subtitle):
    global links_subcenter
    import requests
    headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Authorization': 'Basic YWFhOmFhYQ==',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'utf-8',
    'Accept-Language': 'en-US,en;q=0.9',
    }
    
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    #'Referer': 'http://185.165.240.137:8080/SUB/',
    'Upgrade-Insecure-Requests': '1',
    }
    results2=[]
    db=[]
    subtitle=' '


    item["season"]=str(item["season"])
    item["episode"]=str(item["episode"])
    if len(item["season"])==1:
        lseason='0'+item["season"]
    else:
        lseason=item["season"]
        
    if len(item["episode"])==1:
        lepisode='0'+item["episode"]
    else:
        lepisode=item["episode"]
    ep_str=('.s%se%s.'%(lseason,lepisode)).lower()
    ep_str2=('.%sx%s.'%(item["season"],item["episode"])).lower()
    ep_str3=('.%se%s.'%(item["season"],lepisode)).lower()
    if 'tvshow' in item and len(item['tvshow'])>0:
        base_addr='http://185.165.240.137:8080/SUB/Series/'
        
        title=item["tvshow"].replace(':',' ').replace("'",'').replace(",",' ').replace('  ',' ').lower()
        title2=item["tvshow"].replace(':',' ').replace("'",'').replace(",",' ').replace('  ',' ').replace(' ','.').lower()
        search_string=[title+ep_str,title+ep_str2,title+ep_str3]
        options=[ep_str,ep_str2,ep_str3]
        tv_mode=True
    else:
        base_addr='http://185.165.240.137:8080/SUB/Movies/'
        title=item["title"].replace(':',' ').replace("'",'').replace(",",' ').replace('  ',' ').lower()
        title2=item["title"].replace(':',' ').replace("'",'').replace(",",' ').replace('  ',' ').replace(' ','.').lower()
        tv_mode=False
    
 
    progress='requests key'
   

    req = urllib2.Request(base_addr+'?search='+title.replace(' ','%20'), None, headers)  
    resp = urllib2.urlopen(req)
    response=resp.read()
   
    regex="input type='checkbox' class='selector' name='selection' value=\".+?\".+?<a href=\"(.+?)\"><img src=\".+?\">(.+?)<"
    m=re.compile(regex,re.DOTALL).findall(response)
    count=1
    
    for lk,items2 in m:
      
        c_name=items2.replace(':',' ').replace("'",'').replace(",",' ').replace('_',' ').replace('  ',' ').lower()
        
        if title not in c_name and title2 not in c_name :
            continue
        
        '''
        regex='.*(\.[1-3][0-9]{3}\.)'
        year_pre=re.compile(regex).findall(items2['name'])
        if len(year_pre)>0:
            myLogger(items2['name'])
            myLogger(year_pre[0])
            myLogger(item['year'])
            if str(item['year'])!=str(year_pre[0]):
                continue
        '''
        ok=True
        if tv_mode:
            ok=False
            for items in options:
                if items.lower()  in items2.lower():
                    ok=True
                    break
        if ok:
        
            url_down=base_addr+lk
          
            #z=requests.get(url,headers=headers,stream=True).url
            #myLogger(z)
            url = "plugin://%s/?action=download&link=%s&id=%s&filename=%s&language=%s&source=%s" % (
                __scriptid__,urllib.quote_plus(url_down), items2, items2, 'he','aa_subs')
            
            if mode_subtitle>1:
                json_data={'url':url,
                             'label':'hebrew',
                             'label2':'[COLOR lightskyblue]'+str(count)+'. '+' [AA]' +items2+'[/COLOR]',
                             'iconImage':"0",
                             'thumbnailImage':"he",
                             'hearing_imp':'false',
                             'sync': 'false'}
                db.append(json_data)
                count+=1
                links_subcenter=db
    
    return results2,subtitle,db

def aa_subs(item,mode_subtitle):
    global links_subcenter
    
    if item["tvshow"] or is_local_file_tvshow(item):
        
        x_pre=cache.get(get_aa_server,100,base64.b64decode(base_aa).decode('utf-8')+'Series/','tv', table='subs_aa')
        
        file = open(x_pre, 'r')
   
        x=file.read()#.decode('utf-8','ignore')
        file.close()
      
        regex='<td><a href="(.+?)"'
        
        m=re.compile(regex).findall(x)
        ret = []
        item["season"]=str(item["season"])
        item["episode"]=str(item["episode"])
        if len(item["season"])==1:
            lseason='0'+item["season"]
        else:
            lseason=item["season"]
            
        if len(item["episode"])==1:
            lepisode='0'+item["episode"]
        else:
            lepisode=item["episode"]
        ep_str=('.s%se%s.'%(lseason,lepisode)).lower()
        ep_str2=('.%sx%s.'%(item["season"],item["episode"])).lower()
        ep_str3=('.%se%s.'%(item["season"],lepisode)).lower()
        
        x=1
        db=[]
        subtitle=" "
        results2=[]
      
        for items in m:
            f_item=items.lower().replace(' ','.')
           
            if (is_local_file_tvshow(item)):
                item["tvshow"] = item["title"]
                
            if item["tvshow"].replace(' ','.').lower() in f_item and ((ep_str in f_item) or (ep_str2 in f_item) or(ep_str3 in f_item)) :
               
                url = "plugin://%s/?action=download&link=%s&id=%s&filename=%s&language=%s&source=%s" % (
                    __scriptid__,base64.b64decode(base_aa).decode('utf-8')+'Series/'+ items, items, items, 'he','aa_subs')
                if mode_subtitle>1:
                    json_data={'url':url,
                                 'label':'he',
                                 'label2':'[COLOR lightskyblue]'+str(x)+'. '+prefix_acat+' ' +items+'[/COLOR]',
                                 'iconImage':"0",
                                 'thumbnailImage':"he",
                                 'hearing_imp':'false',
                                 'sync': 'false'}
                    db.append(json_data)
                    links_subcenter=db
                    x=x+1
            
    else:
        x_pre=cache.get(get_aa_server,100,base64.b64decode(base_aa).decode('utf-8')+'Movies/','movie', table='subs_aa')
       
        file = open(x_pre, 'r')
   
        x=file.read()#.decode('utf-8','ignore')
        file.close()
        
      
        regex='<td><a href="(.+?)"'
        
        m=re.compile(regex).findall(x)
        ret = []
        
       
        
        x=1
        db=[]
        subtitle=" "
        results2=[]
      
        for items in m:
            f_item=items.lower().replace(' ','.').lower()
            
            if item["title"].replace(' ','.').lower() in f_item.lower() and str(item['year']) in f_item :
                
           
                url = "plugin://%s/?action=download&link=%s&id=%s&filename=%s&language=%s&source=%s" % (
                    __scriptid__,base64.b64decode(base_aa).decode('utf-8')+'Movies/'+ items, items, items, 'he','aa_subs')
                if mode_subtitle>1:
                    json_data={'url':url,
                                 'label':'he',
                                 'label2':'[COLOR lightskyblue]'+str(x)+'. '+prefix_acat+' ' +items+'[/COLOR]',
                                 'iconImage':"0",
                                 'thumbnailImage':"he",
                                 'hearing_imp':'false',
                                 'sync': 'false'}
                    db.append(json_data)
                    links_subcenter=db
                    x=x+1

    return results2,subtitle,db

def subcenter_search_old(item,mode_subtitle):
        global links_subcenter
        results = []
        
        id_collection=[]
        search_string = re.split(r'\s\(\w+\)$', item["tvshow"])[0] if item["tvshow"] else item["title"]
        user_token =  get_user_token()

        if user_token:
            query = {"q": search_string.encode("utf-8").replace("%20"," "), "user": user_token["user"], "token": user_token["token"]}
            if item["tvshow"]:
                query["type"] = "series"
                query["season"] = item["season"]
                query["episode"] = item["episode"]
            else:
                query["type"] = "movies"
                if item["year"]:
                    query["year_start"] = int(item["year"]) 
                    query["year_end"] = int(item["year"])

            search_result =  urlHandler.request( BASE_URL + "search/", query)

            if search_result is not None and search_result["result"] == "failed":
                # Update cached token
                user_token =  get_user_token(True)
                query["token"] = user_token["token"]
                search_result =  urlHandler.request( BASE_URL + "search/", query)

            if search_result is not None and search_result["result"] == "failed":
                notify(32009)
                if mode_subtitle>1:
                   return results," "," "
                else:
                   return len(results)," "," "

            myLogger("Results: %s" % search_result)

            if search_result is None or search_result["result"] != "success" or search_result["count"] < 1:
                if mode_subtitle>1:
                   return results," "," "
                else:
                    return len(results)," "," "

            results = search_result# _filter_results(search_result["data"], search_string, item)
            
            
            myLogger("Filtered: %s" % results)

        else:
            notify(32009)
        ret = []
        ok=True
        lang=[]
        lang.append('he')
        if all_setting["English"]== 'true':
          lang.append('eng')
        for result in results['data']:
            total_downloads = 0
            counter = 0
            
            subs_list = result
     
            if subs_list is not None:
               

                for language in subs_list['subtitles']:
                        
                        
                       if language in lang:
                    #if xbmc.convertLanguage(language, xbmc.ISO_639_2) in item["3let_language"]:
                        for current in subs_list['subtitles'][language]:
                            

                            counter += 1
                            title = current["version"]
                            subtitle_rate = 0
                            total_downloads += int(current["downloads"])
                            ret.append(
                                {   'lang_index':'0',# item["3let_language"].index('heb'),
                                    'filename': title,
                                    'link': current["key"],
                                    'language_name': xbmc.convertLanguage(language, xbmc.ENGLISH_NAME),
                                    'language_flag': language,
                                    'id': current["id"],
                                    'rating': current["downloads"],
                                    'sync': subtitle_rate >= 3.8,
                                    'hearing_imp': False,
                                    'is_preferred':
                                        xbmc.convertLanguage(language, xbmc.ISO_639_2) == item[
                                            'preferredlanguage']
                                })
            # Fix the rating
            if total_downloads:
                for it in ret[-1 * counter:]:
                    it["rating"] = str(min(int(round(float(it["rating"]) / float(total_downloads), 1) * 8), 5))

        number_of_subs=0
        x=1
        saved_data=[]
        results2= sorted(ret, key=lambda x: (x['is_preferred'], x['lang_index'], x['sync'], x['rating']), reverse=True)
        subtitle=" "
        json_data=[]
        db=[]
        if results2:
         for it in results2:

            number_of_subs=number_of_subs+1
            listitem = ListItem(label=it["language_name"],
                                        label2='[COLOR lightskyblue]'+str(x)+'. '+' [SC]' +it["filename"]+'[/COLOR]',
                                        iconImage=it["rating"],
                                        thumbnailImage=it["language_flag"]
                                        )
            if it["sync"]:
                listitem.setProperty("sync", "true")
                sync='true'
            else:
                listitem.setProperty("sync", "false")
                sync='false'

            if it.get("hearing_imp", False):
                listitem.setProperty("hearing_imp", "true")
                hearing_imp='true'
            else:
                listitem.setProperty("hearing_imp", "false")
                hearing_imp="false"

            url = "plugin://%s/?action=download&link=%s&id=%s&filename=%s&language=%s" % (
                __scriptid__, it["link"], it["id"], it["filename"], it["language_flag"])
            if it["id"] not in id_collection:
              id_collection.append(it["id"])
              if mode_subtitle>1:
                json_data={'url':url,
                             'label':it["language_name"],
                             'label2':'[COLOR lightskyblue]'+str(x)+'. '+' [SC]' +it["filename"]+'[/COLOR]',
                             'iconImage':it["rating"],
                             'thumbnailImage':it["language_flag"],
                             'hearing_imp':hearing_imp,
                             'sync':sync}
                db.append(json_data)
                links_subcenter=db
                x=x+1
             

        
        return results2,subtitle,db
        
        
def wizdom_search(item,mode_subtitle,imdb_id):
 
      if str(imdb_id)[:2]=="tt":
                    num_of_subs,subtitle,subtitle_list=GetWizJson(imdb_id,mode_subtitle,0,0,item['file_original_path'])
  
      return num_of_subs,subtitle,subtitle_list,imdb_id

def clean_title(item):
    
    temp=re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", item["title"])


    temp=temp.replace("(","")
    temp=temp.replace(")","")
    temp=temp.replace("[","")
    temp=temp.replace("]","")
    temp=temp.replace("1080 HD","")
    temp=temp.replace("720 HD","")
   
 
    if "  - " in temp:
      temp=temp.split("  - ")[0]
    
    temp2=re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", item["tvshow"])
    temp2=temp2.replace("(","")
    temp2=temp2.replace(")","")
    temp2=temp2.replace("[","")
    temp2=temp2.replace("]","")
    if "  - " in temp2:
      temp2=temp2.split("  - ")[0]

    title = os.path.splitext(temp)
    tvshow = os.path.splitext(temp2)

    if len(title) > 1:
        if re.match(r'^\.[a-z]{2,4}$', title[1], re.IGNORECASE):
            item["title"] = title[0]
        else:
            item["title"] = ''.join(title)
    else:
        item["title"] = title[0]

    if len(tvshow) > 1:
        if re.match(r'^\.[a-z]{2,4}$', tvshow[1], re.IGNORECASE):
            item["tvshow"] = tvshow[0]
        else:
            item["tvshow"] = ''.join(tvshow)
    else:
        item["tvshow"] = tvshow[0]

    
    #item["title"] = str(item["title"]) #unicode(item["title"], "utf-8")		# burekas fix - offline hebrew titles
    #item["tvshow"] = str(item["tvshow"] #unicode(item["tvshow"], "utf-8")	    # burekas fix - offline hebrew titles

    # Removes country identifier at the end
    item["title"] = re.sub(r'\([^\)]+\)\W*$', '', item["title"]).strip()
    item["tvshow"] = re.sub(r'\([^\)]+\)\W*$', '', item["tvshow"]).strip()


def parse_rls_title(item):
    title = regexHelper.sub(' ', item["title"])
    tvshow = regexHelper.sub(' ', item["tvshow"])

    groups = re.findall(r"(.*?) (\d{4})? ?(?:s|season|)(\d{1,2})(?:e|episode|x|\n)(\d{1,2})", title, re.I)

    if len(groups) == 0:
        groups = re.findall(r"(.*?) (\d{4})? ?(?:s|season|)(\d{1,2})(?:e|episode|x|\n)(\d{1,2})", tvshow, re.I)

    if len(groups) > 0 and len(groups[0]) >= 3:
        title, year, season, episode = groups[0]
        item["year"] = str(int(year)) if len(year) == 4 else year

        item["tvshow"] = regexHelper.sub(' ', title).strip()
        item["season"] = str(int(season))
        item["episode"] = str(int(episode))
        myLogger("TV Parsed Item: %s" % (item,))

def get_more_data(now_play_data, titleBefore):
    myLogger("get_more_data - filename: " + repr(now_play_data['file']))
    myLogger("get_more_data - titleBefore: : " + repr(titleBefore))
    
    title, year = xbmc.getCleanMovieTitle(now_play_data['file'])
    myLogger("CleanMovieTitle: title - %s, year - %s " %(title, year)) 
    
    tvshow=' '
    season=0
    episode=0
    
    try:
        yearval = int(year)
    except ValueError:
        yearval = 0
        
    if title == "" or not title.isascii():
        title = titleBefore
        
    patterns = [
                '\WS(?P<season>\d\d)E(?P<episode>\d\d)',
                '\W(?P<season1>\d)x(?P<episode1>\d\d)'
                ]
                
    for pattern in patterns:
        pattern = r'%s' % pattern
        match = re.search(pattern, now_play_data['file'], flags=re.IGNORECASE)
        myLogger("regex match: " + repr(match)) 

        if match is None:
            continue
        else:
            title = title[:match.start('season') - 1].strip()
            season = match.group('season').lstrip('0')
            episode = match.group('episode').lstrip('0')
            myLogger("regex parse: title = %s , season = %s, episode = %s " %(title,season,episode))
            return title,yearval,season,episode
    
    return title,yearval,season,episode            

        
def normalizeString(str):
    if KODI_VERSION>18:
        return unicodedata.normalize(
            'NFKD', ((str))
        ).encode('utf-8', 'ignore').decode('utf-8')
    else:
        return unicodedata.normalize(
            u'NFKD', unicode((str))
        ).encode('utf-8', 'ignore').decode('utf-8')

def MyLog(msg):    
    myLogger(msg)             
    
def download_next(location,all_setting,last_sub_download,save_all_data,max_sub):

     x=0

     __last__ = (xbmc_tranlate_path(os.path.join(__profile__, 'last')))

     value_for_subs=location
    
     enable_count=0
     total_count=0
     break_now=0
     
          
     for save_data_value in save_all_data:
         if break_now>0:
           break
         lab1,lab2,icn,thu,url,pre=save_data_value


         params=getParams('?'+url.split('?')[1])
         
         id = getParam("id", params)
         try:
              language=params["language"]
         except:
              language=''
         try:
              key=params["link"]
         except:
              key=''
         try:
              filename=params["filename"]
         except:
              filename=''
         try:
              source=params["source"]
         except:
              source=''
         
    
         if x==value_for_subs :
               notify2('Downloading',all_setting)
               myLogger('source:'+source)
               myLogger('subs:')
               if source=='subscence':
               
                 if 'episode' in params:
                   subs = download_subscene(params["link"],1, params["episode"])
                 else:
                   subs = download_subscene(params["link"],1)
               elif source=='opensubtitle':
                   subs = Download_opensubtitle(params["ID"], params["link"],params["format"],1)
               elif source=='aa_subs':
                    myLogger('AA SUBS DOWNLOAD')
                    subs = Download_aa(params["link"],1)
               else:
                 temp,subs = download(id,language,key,filename,1)
                 try:
                    if len(subs[0])>0:
                        subs=subs[0]
                 except:
                    pass
                 myLogger(temp)
               
               myLogger(subs)
               
               try:
                 shutil.rmtree(__last__)
               except: pass
               xbmcvfs.mkdirs(__last__)
             
               last_sub_download=hashlib.sha256(str(json.dumps(params)).encode('utf-8','ignore')).hexdigest()
               
               subtitle_cache_next().set('last_sub', last_sub_download)
               if subs!='0' and subs!='NO':
                 sub=subs
                 if language!='Hebrew'  and all_setting["auto_translate"]=='true' and language!='' and (source=='opensubtitle' or source=='subscence'):
                  
                    translate_subs(sub,os.path.join(__last__, "trans.srt"),3)
                    sub=os.path.join(__last__, "trans.srt")
                       
                 dst=os.path.join(__last__, "last.srt")
                 xbmcvfs.copy(sub, dst)
                 if all_setting["enable_font"]=='true':
                   sub = srt2ass(sub,all_setting)
                 notify2('Setting sub [COLOR skyblue]'+str(total_count) +'/'+str(max_sub-1)+'[/COLOR]: ' +lab2,all_setting)

                 xbmc.Player().setSubtitles(sub)
                 break_now=1
                 break
               else:
                 notify2('[COLOR red]Cannot download [/COLOR][COLOR skyblue]'+str(total_count) +'/'+str(max_sub-1)+'[/COLOR]: ' +lab2,all_setting)
           

         x=x+1
         total_count=total_count+1
     return location
   

def refresh_setting():
   global __settings__,__addon__,MyAddon,MyScriptID,all_setting
   MyAddon = xbmcaddon.Addon()
   MyScriptID = MyAddon.getAddonInfo('id')
   __settings__ = xbmcaddon.Addon(id=MyScriptID)
   __addon__ = xbmcaddon.Addon()
   all_setting={}
   all_setting=({"Email":MyAddon.getSetting("Email"),
                "Password":MyAddon.getSetting("Password"),
                "action":MyAddon.getSetting("action"),
                "aa_subs":MyAddon.getSetting("aa_subs"),
                "OSuser":MyAddon.getSetting("OSuser"),
                "OSpass":MyAddon.getSetting("OSpass"),
                "wizset":MyAddon.getSetting("wizset"),
                "subscene":MyAddon.getSetting("subscene"),
                "opensubtitle":MyAddon.getSetting("opensubtitle"),
                "English":MyAddon.getSetting("English"),
                "autosub":MyAddon.getSetting("autosub"),
                "pause":MyAddon.getSetting("pause"),
                "ExcludeTime":MyAddon.getSetting("ExcludeTime"),
                "ExcludeAddosOption":MyAddon.getSetting("ExcludeAddosOption"),
                "ExcludeAddos":MyAddon.getSetting("ExcludeAddos"),
                "ExcludeAddosOption2":MyAddon.getSetting("ExcludeAddosOption2"),
                "ExcludeAddos2":MyAddon.getSetting("ExcludeAddos2"),
                "ExcludeAddosOption3":MyAddon.getSetting("ExcludeAddosOption3"),
                "ExcludeAddos3":MyAddon.getSetting("ExcludeAddos3"),
                "ExcludeAddosOption4":MyAddon.getSetting("ExcludeAddosOption4"),
                "ExcludeAddos4":MyAddon.getSetting("ExcludeAddos4"),
                "ExcludeAddosOption5":MyAddon.getSetting("ExcludeAddosOption5"),
                "ExcludeAddos5":MyAddon.getSetting("ExcludeAddos5"),
                "ExcludeAddosOption6":MyAddon.getSetting("ExcludeAddosOption6"),
                "ExcludeAddos6":MyAddon.getSetting("ExcludeAddos6"),
                "enable_font":MyAddon.getSetting("enable_font"),
                "background":MyAddon.getSetting("background"), 
                "bold":MyAddon.getSetting("bold"),
                "size":MyAddon.getSetting("size"),
                "color":MyAddon.getSetting("color"), 
                "background_level":MyAddon.getSetting("background_level"),
                "yify":MyAddon.getSetting("yify"),
                "force":MyAddon.getSetting("force"),
                "popup":MyAddon.getSetting("popup"),
                "storage":MyAddon.getSetting("storage"),
                "ktuvitset":MyAddon.getSetting("ktuvitset"),
                "ktcode":MyAddon.getSetting("ktcode"),
                "sort_subs":MyAddon.getSetting("sort_subs"),
                "auto_translate":MyAddon.getSetting("auto_translate"),
                "arab":MyAddon.getSetting("arab"),
                "spanish":MyAddon.getSetting("spanish"),
                "history_log":MyAddon.getSetting("history_log"),
                "other_lang":MyAddon.getSetting("other_lang"),
                "storage_en":MyAddon.getSetting("storage_en"),
                "all_lang":MyAddon.getSetting("all_lang"),
                "local_files":MyAddon.getSetting("local_files"),
                "Debug":MyAddon.getSetting("Debug")})
   temp=json.dumps(all_setting)
   return  json.loads(temp)
if not exists(MyTmp):
    xbmcvfs.mkdirs(MyTmp)


myLogger("sys.argv: %s" %repr(sys.argv))
myLogger("sys.argv len: %s" %str(len(sys.argv)))

if len(sys.argv) >= 2:   
    params = getParams(sys.argv[2])

    action = getParam("action", params)
    searchstring=getParam("searchstring", params)
else:
    params = {}
    params['action'] = 'autosub'
    params['searchstring'] = ''

MyLog("Version:%s"%MyVersion)
MyLog("Action:%s"%action)
try:
  language=params["language"]
except:
  language=''
try:
  key=params["link"]
except:
  key=''
try:
  filename=params["filename"]
except:
  filename=''
try:
  source=params["source"]
except:
  source=''
all_setting=refresh_setting()
def search_local(item,mode_subtitle,all_setting):
    global links_local
    from xbmcvfs import listdir
    
    mypath=all_setting["storage"]
    onlyfiles=[]
    _, files =listdir(mypath)
    for f in files:
   
      if ('.srt' in  f or '.sub' in f):
        
        onlyfiles.append(f)
    #onlyfiles = [f for f in listdir(mypath) if ('.srt' in  f or '.sub' in f)]


    count=0
    all_subs_local=[]
    first=' '
    for file1 in onlyfiles:
       split_file=file1.split(".")
       subfix=split_file[len(split_file)-1]
       
       if subfix=='ass' or subfix=='srt' or subfix=='sub':
          array_original=item['file_original_path'].strip().replace("_",".").replace(" ",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")
          original_name=item['file_original_path'].strip().replace("_",".").replace(" ",".").replace(".avi","").replace(".mp4","").replace(".mkv","")
          
          
          array_original=[line.strip().lower() for line in array_original]
          array_original=[str(x) for x in array_original if x != '']
          array_original2=xbmc.getInfoLabel("VideoPlayer.title").strip().replace("_",".").replace(" ",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")
          original_name2=xbmc.getInfoLabel("VideoPlayer.title").strip().replace("_",".").replace(" ",".").replace(".avi","").replace(".mp4","").replace(".mkv","")
          
          array_original2=[line.strip().lower() for line in array_original2]
          array_original2=[str(x) for x in array_original2 if x != '']
          info=(PTN.parse(file1))
          title_comapre=info['title'].strip().replace("_",".").replace(" ",".").replace(".avi","").replace(".mp4","").replace(".mkv","")
          precent=similar(file1.lower().replace("_",".").replace(" ",".").replace(".avi","").replace(".srt","").replace(".sub","").replace(".ass","").replace(".mp4","").replace(".mkv","").split("."),array_original)
          precent2=similar(file1.lower().replace("_",".").replace(" ",".").replace(".avi","").replace(".srt","").replace(".sub","").replace(".ass","").replace(".mp4","").replace(".mkv","").split("."),array_original2)

       

          if (precent>30 or precent2>30) and title_comapre in original_name and title_comapre in original_name2:
   
            if 'season' in info:
             if len(str(info['season']))>0:
                  
                  if (info['season']==int(item['season']) and info['episode']==int(item['episode'])) or (precent>90 or precent2>90) :
                    
                    url = "plugin://%s/?action=download&filename=%s&id=%s" % (MyScriptID, os.path.join(mypath,file1), 'LOCAL FILE')
                    
                    json_data={'url':url,
                         'label':"Hebrew",
                         'label2':str(count)+'. '+'[COLOR thistle]'+prefix_local+file1+'[/COLOR]',
                         'iconImage':"0",
                         'thumbnailImage':"he",
                         'hearing_imp':'false',
                         'sync': 'false'}
                    all_subs_local.append(json_data)
                    links_local=all_subs_local
                    if  count==0:
                      first=file1
                    count=count+1
                  
            else:
                
                url = "plugin://%s/?action=download&filename=%s&id=%s" % (MyScriptID, os.path.join(mypath,file1), 'LOCAL FILE')
                json_data={'url':url,
                     'label':"Hebrew",
                     'label2':str(count)+'. '+'[COLOR thistle]'+prefix_local+file1+'[/COLOR]',
                     'iconImage':"0",
                     'thumbnailImage':"he",
                     'hearing_imp':'false',
                     'sync': 'false'}
                all_subs_local.append(json_data)
                links_local=all_subs_local
                if  count==0:
                  first=file1
                count=count+1
  
    return len(all_subs_local),first,all_subs_local
def get_login_cook():
    import requests
    headers = {
    'authority': 'www.ktuvit.me',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://www.ktuvit.me',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    
    'accept-language': 'en-US,en;q=0.9',
    
    }

    ktEmail = __addon__.getSetting( "KT_email" )
    if (__addon__.getSetting( "KT_email" ) == ''):
        ktEmail = "hatzel6969@gmail.com"
    
    ktEncPass = __addon__.getSetting( "KT_enc_pass" )
    if (__addon__.getSetting( "KT_enc_pass" ) == ''):
        ktEncPass = "Jw1n9nPOZRAHw9aVdarvjMph2L85pKGx79oAAFTCsaE="

    data = '{"request":{"Email":"%s","Password":"%s"}}' %(ktEmail, ktEncPass)

    login_cook = requests.post('https://www.ktuvit.me/Services/MembershipService.svc/Login', headers=headers, data=data).cookies
    login_cook_fix={}
    for cookie in login_cook:

            login_cook_fix[cookie.name]=cookie.value
    return login_cook_fix

def Ktuvit_Search(item,mode_subtitle,imdb_id):
    global links_ktuvit
    import requests

    parse_rls_title(item)
    login_cook=cache.get(get_login_cook,1, table='subs')
  
    myLogger("Ktuvit_Search item:" + repr(item))
    if item["tvshow"]:
        s_type='1'
        s_title=item["tvshow"]
    elif is_local_file_tvshow(item):
        s_type='1'
        s_title=item["title"]        
    else:
        s_type='0'
        s_title=item["title"]
    
    if 1:
        headers = {
            'authority': 'www.ktuvit.me',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'content-type': 'application/json',
            'origin': 'https://www.ktuvit.me',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.ktuvit.me/Search.aspx',
            'accept-language': 'en-US,en;q=0.9',
            
        }

        data = '{"request":{"FilmName":"%s","Actors":[],"Studios":null,"Directors":[],"Genres":[],"Countries":[],"Languages":[],"Year":"","Rating":[],"Page":1,"SearchType":"%s","WithSubsOnly":false}}'%(s_title,s_type)
        
        response = requests.post('https://www.ktuvit.me/Services/ContentProvider.svc/SearchPage_search', headers=headers, data=data).json()
        
        j_data=json.loads(response['d'])['Films']
        f_id=''
        myLogger('Ktuvit')
        myLogger(data)   
        myLogger(response)        
        myLogger(j_data)

        #first filtered by imdb
        for itt in j_data:
            if imdb_id==itt['ImdbID']:              
                f_id=itt['ID']

        #if ids still empty (wrong imdb on ktuvit page) filtered by text                
        if f_id == '':
            s_title = regexHelper.sub('', s_title).lower()        
            for itt in j_data:
                eng_name = regexHelper.sub('', regexHelper.sub(' ', itt['EngName'])).lower()
                heb_name = regexHelper.sub('', itt['HebName'])

                if (s_title.startswith(eng_name) or eng_name.startswith(s_title) or
                        s_title.startswith(heb_name) or heb_name.startswith(s_title)):
                    f_id=itt["ID"]
                
        if f_id!='':
            url='https://www.ktuvit.me/MovieInfo.aspx?ID='+f_id


        if item["tvshow"] or is_local_file_tvshow(item):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
                'Accept': 'text/html, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.5',
                'X-Requested-With': 'XMLHttpRequest',
                'Connection': 'keep-alive',
                'Referer': url,
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'TE': 'Trailers',
            }

            params = (
                ('moduleName', 'SubtitlesList'),
                ('SeriesID', f_id),
                ('Season', item["season"]),
                ('Episode', item["episode"]),
            )

            response = requests.get('https://www.ktuvit.me/Services/GetModuleAjax.ashx', headers=headers, params=params, cookies=login_cook).content
        else:
            headers = {
                'authority': 'www.ktuvit.me',
                'cache-control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'referer': 'https://www.ktuvit.me/MovieInfo.aspx?ID='+f_id,
                'accept-language': 'en-US,en;q=0.9',
                
            }
            params = (
                ('ID', f_id),
            )
            
            response = requests.get('https://www.ktuvit.me/MovieInfo.aspx', headers=headers, params=params, cookies=login_cook).content
            
        
        regex='<tr>(.+?)</tr>'
        m_pre=re.compile(regex,re.DOTALL).findall(response.decode('utf-8'))
        z=1
        subtitle=' '
        subtitle_list=[]
        for itt in m_pre:
           
            regex='<div style="float.+?>(.+?)<br />.+?data-subtitle-id="(.+?)"'
            m=re.compile(regex,re.DOTALL).findall(itt)
            if len(m)==0:
                continue
                
            if ('i class' in m[0][0]):    #burekas fix for KT titles
                regex='כתובית מתוקנת\'></i>(.+?)$'
                n=re.compile(regex,re.DOTALL).findall(m[0][0])
                nm=n[0].replace('\n','').replace('\r','').replace('\t','').replace(' ','')
            else:
                nm=m[0][0].replace('\n','').replace('\r','').replace('\t','').replace(' ','')            
            
            data='{"request":{"FilmID":"%s","SubtitleID":"%s","FontSize":0,"FontColor":"","PredefinedLayout":-1}}'%(f_id,m[0][1])


            url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID,nm, "FIRSTH$$$"+data+'$$$'+f_id)
     
            json_data={'url':url,
                             'label':"Hebrew",
                             'label2':'[COLOR limegreen]'+str(z)+'. '+prefix_ktuvit+' '+nm+'[/COLOR]',
                             'iconImage':"0",
                             'thumbnailImage':"he",
                             'hearing_imp':'false',
                             'sync': 'false'}
           
            subtitle_list.append(json_data)
            links_ktuvit=subtitle_list            
            z=z+1

    return len(m_pre),subtitle,subtitle_list
def Ktuvit_Search_old(item,mode_subtitle,imdb_id):
   global links_ktuvit
   import requests
   

   if item["tvshow"]:
       if 'tt' in imdb_id:
         query={"request":
            {
                "SearchPhrase": imdb_id,
                "SearchType": "ImdbID",
                "Version":"1.0",
                "Season":item["season"],
                "Episode":item["episode"]
            }
            }
       else:
         query={"request":
            {
                "SearchPhrase": item["tvshow"],
                "SearchType": "FilmName",
                "Version":"1.0",
                "Season":item["season"],
                "Episode":item["episode"]
            }
            }
       url_n='http://api.ktuvit.me/FindSeries'
   else:
       if 'tt' in imdb_id:
         query={"request":
            {
                "SearchPhrase": imdb_id,
                "SearchType": "ImdbID",
                "Version":"1.0",
                "Season":item["season"],
                "Episode":item["episode"]
            }
            }
       else:
         query={"request":
            {
                "SearchPhrase": item["title"],
                "SearchType": "FilmName",
                "Version":"1.0",
                "year":int(item['year'])
            }
            }
            
       url_n='http://api.ktuvit.me/FindFilm'
 
   subtitle=' '
   subtitle_list=[]

   
   x=requests.post(url_n,json=query,timeout=15).json()
 
   z=0
   responce=json.loads(x)
   
   for item_data in responce['Results']:
       
       url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, item_data["SubtitleName"], "FIRSTH$$$"+item_data["Identifier"])
     
       json_data={'url':url,
                         'label':"Hebrew",
                         'label2':'[COLOR limegreen]'+str(z)+'. '+prefix_ktuvit+' '+item_data["SubtitleName"]+'[/COLOR]',
                         'iconImage':"0",
                         'thumbnailImage':"he",
                         'hearing_imp':'false',
                         'sync': 'false'}
  

      
       subtitle_list.append(json_data)
       links_ktuvit=subtitle_list
      
       z=z+1

   return len(responce['Results']),subtitle,subtitle_list
def similar(w1, w2):
    from difflib import SequenceMatcher
    
    s = SequenceMatcher(None, w1, w2)
    return int(round(s.ratio()*100))
def download_subs(link):

      params = getParams(link)
      id = getParam("id", params)
      try:
          language=params["language"]
      except:
          language=''
      try:
          key=params["link"]
      except:
          key=''
      try:
          filename=params["filename"]
      except:
          filename=''
      try:
          source=params["source"]
      except:
          source=''
      myLogger('source=='+source)
      if source=='subscence':
      
        if 'episode' in params:
          subs = download_subscene(params["link"],3, params["episode"])
        else:
          subs = download_subscene(params["link"],3)
      elif source=='opensubtitle':
        subs = Download_opensubtitle(params["ID"], params["link"],params["format"],3)
      elif source=='aa_subs':
            myLogger('AA SUBS DOWNLOAD')
            subs = Download_aa(params["link"],3)
      else:

        subs,temp = download(id,language,key,filename,3)
      try:
        shutil.rmtree(__last__)
        xbmc.sleep(100)
      except: pass
      xbmcvfs.mkdirs(__last__)
      xbmc.sleep(100)
      last_sub_download=hashlib.sha256(str(json.dumps(params)).encode('utf-8','ignore')).hexdigest()
     
      subtitle_cache_next().set('last_sub', last_sub_download)

      for sub in subs:
        
       
        return sub
def Search_opensubtitle_in(item,imdb_id,mode_subtitle,all_setting):
        global links_open
        subtitle,saved_data=Search_opensubtitle(item,imdb_id,mode_subtitle,all_setting,prefix_open)
        links_open=saved_data
        return links_open

def rtl(text):
    try:
        text=html_parser.unescape(text)
    except:
        import xml.sax.saxutils as saxutils
        text=saxutils.unescape(text.decode())
    test_t=text[-1:]
    if test_t=='.' or test_t=='?' or test_t=='!'or test_t==','or test_t=='(':
     
       
       text=test_t+text[:len(text)-1]+' '
     
    return text


def translate_subs(input_file,output_file,mode_subtitle):

    import requests,chardet
   
    sourcelang='eng'
    if mode_subtitle==3:
        dp = xbmcgui . DialogProgress ( )
        if KODI_VERSION>18:
            dp.create('אנא המתן'+'\n'+'מתרגם',)
            dp.update(0, 'אנא המתן'+'\n'+'מתרגם' )
        else:
            dp.create('אנא המתן','מתרגם',)
            dp.update(0, 'אנא המתן','מתרגם' )
    url = 'https://www.googleapis.com/language/translate/v2?key={0}&q={1}&source={2}&target={3}'
    targetlang='he'
    api_key='AIzaSyCk5TfD_K1tU1AB2salwn2Lb_yZbesSmY8'
    import chardet

    # Open the file as binary data
    with open(input_file, 'rb') as f:
        # Join binary lines for specified number of lines
        rawdata = f.read()

    encoding=chardet.detect(rawdata)['encoding']
    myLogger('encoding:'+encoding)
    
   
    text=rawdata
    
    
    if encoding=='ISO-8859-7':
      text=text.decode('cp1253','ignore')
    elif encoding=='MacCyrillic':
      text=text.decode('cp1256','ignore')
    else:
      text=text.decode(encoding,'ignore')
    
    from gtn.google_trans_new import google_translator  
  
    translator = google_translator()  
    
    
    all_text_p1=[]
    all_data=''
 
    counter=0
    

    split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
   
    ax2=split_string(text,3000)
    f_sub_pre=''
    xx=0
 
    for items in ax2:
         if mode_subtitle==3:
          if KODI_VERSION>18:
            dp.update(int(((xx* 100.0)/(len(ax2))) ), ' מתרגם ' + encoding+'\n'+str(int(((xx* 100.0)/(len(ax2))) ))+'%')
          else:
              dp.update(int(((xx* 100.0)/(len(ax2))) ), ' מתרגם ' + encoding,str(int(((xx* 100.0)/(len(ax2))) ))+'%')
         translation=translator.translate(items, lang_tgt='he')
         f_sub_pre=f_sub_pre+translation
         xx+=1
    
    all_text=f_sub_pre.replace(': ',':').replace('"# ','"#').split('\r\n')
    
   
    f_all=''
    for line in all_text:
       if '[' and ']' not in line:
        f_all=f_all+rtl(line.encode('utf-8'))+'\n'
       else:
        f_all=f_all+line.replace('] [','][')+'\n'
   
    if KODI_VERSION>18:
        with open(output_file, mode="w", encoding="utf8") as f:
             f.write(f_all)
    else:
        with open(output_file, mode="w") as f:
             f.write(f_all)
    
    if mode_subtitle==3:
      dp.close()
    return f_all
def search_subscene(item,mode_subtitle):
    global sc_subtitle
    import requests
    selected_lang=['heb']
    if MyAddon.getSetting("arab")== 'true':
        selected_lang.append('ara')
    if MyAddon.getSetting("spanish")== 'true':
        selected_lang.append('spa')
        

    if len(MyAddon.getSetting("other_lang"))>0:
         all_lang=MyAddon.getSetting("other_lang").split(",")
         
         for items in all_lang:
          
            selected_lang.append(items)
    all_lang_codes={

        'Albanian': {'id': 1, '3let': 'alb', '2let': 'sq', 'name': 'Albanian'},
        'Arabic': {'id': 2, '3let': 'ara', '2let': 'ar', 'name': 'Arabic'},
        'Big 5 code': {'id': 3, '3let': 'chi', '2let': 'zh', 'name': 'Chinese'},
        'Brazillian Portuguese': {'id': 4, '3let': 'por', '2let': 'pb', 'name': 'Brazilian Portuguese'},
        'Bulgarian': {'id': 5, '3let': 'bul', '2let': 'bg', 'name': 'Bulgarian'},
        'Chinese BG code': {'id': 7, '3let': 'chi', '2let': 'zh', 'name': 'Chinese'},
        'Croatian': {'id': 8, '3let': 'hrv', '2let': 'hr', 'name': 'Croatian'},
        'Czech': {'id': 9, '3let': 'cze', '2let': 'cs', 'name': 'Czech'},
        'Danish': {'id': 10, '3let': 'dan', '2let': 'da', 'name': 'Danish'},
        'Dutch': {'id': 11, '3let': 'dut', '2let': 'nl', 'name': 'Dutch'},
        'English': {'id': 13, '3let': 'eng', '2let': 'en', 'name': 'English'},
        'Estonian': {'id': 16, '3let': 'est', '2let': 'et', 'name': 'Estonian'},
        'Farsi/Persian': {'id': 46, '3let': 'per', '2let': 'fa', 'name': 'Persian'},
        'Finnish': {'id': 17, '3let': 'fin', '2let': 'fi', 'name': 'Finnish'},
        'French': {'id': 18, '3let': 'fre', '2let': 'fr', 'name': 'French'},
        'German': {'id': 19, '3let': 'ger', '2let': 'de', 'name': 'German'},
        'Greek': {'id': 21, '3let': 'gre', '2let': 'el', 'name': 'Greek'},
        'Hebrew': {'id': 22, '3let': 'heb', '2let': 'he', 'name': 'Hebrew'},
        'Hungarian': {'id': 23, '3let': 'hun', '2let': 'hu', 'name': 'Hungarian'},
        'Icelandic': {'id': 25, '3let': 'ice', '2let': 'is', 'name': 'Icelandic'},
        'Indonesian': {'id': 44, '3let': 'ind', '2let': 'id', 'name': 'Indonesian'},
        'Italian': {'id': 26, '3let': 'ita', '2let': 'it', 'name': 'Italian'},
        'Japanese': {'id': 27, '3let': 'jpn', '2let': 'ja', 'name': 'Japanese'},
        'Korean': {'id': 28, '3let': 'kor', '2let': 'ko', 'name': 'Korean'},
        'Lithuanian': {'id': 43, '3let': 'lit', '2let': 'lt', 'name': 'Lithuanian'},
        'Malay': {'id': 50, '3let': 'may', '2let': 'ms', 'name': 'Malay'},
        'Norwegian': {'id': 30, '3let': 'nor', '2let': 'no', 'name': 'Norwegian'},
        'Polish': {'id': 31, '3let': 'pol', '2let': 'pl', 'name': 'Polish'},
        'Portuguese': {'id': 32, '3let': 'por', '2let': 'pt', 'name': 'Portuguese'},
        'Romanian': {'id': 33, '3let': 'rum', '2let': 'ro', 'name': 'Romanian'},
        'Russian': {'id': 34, '3let': 'rus', '2let': 'ru', 'name': 'Russian'},
        'Serbian': {'id': 35, '3let': 'scc', '2let': 'sr', 'name': 'Serbian'},
        'Slovak': {'id': 36, '3let': 'slo', '2let': 'sk', 'name': 'Slovak'},
        'Slovenian': {'id': 37, '3let': 'slv', '2let': 'sl', 'name': 'Slovenian'},
        'Spanish': {'id': 38, '3let': 'spa', '2let': 'es', 'name': 'Spanish'},
        'Swedish': {'id': 39, '3let': 'swe', '2let': 'sv', 'name': 'Swedish'},
        'Thai': {'id': 40, '3let': 'tha', '2let': 'th', 'name': 'Thai'},
        'Turkish': {'id': 41, '3let': 'tur', '2let': 'tr', 'name': 'Turkish'},
        'Vietnamese': {'id': 45, '3let': 'vie', '2let': 'vi', 'name': 'Vietnamese'}
    }
    seasons = ["Specials", "First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth", "Tenth"]
    seasons = seasons + ["Eleventh", "Twelfth", "Thirteenth", "Fourteenth", "Fifteenth", "Sixteenth", "Seventeenth",
                         "Eighteenth", "Nineteenth", "Twentieth"]
    seasons = seasons + ["Twenty-first", "Twenty-second", "Twenty-third", "Twenty-fourth", "Twenty-fifth", "Twenty-sixth",
                         "Twenty-seventh", "Twenty-eighth", "Twenty-ninth"]
                         
    all_nam_lang={}
    ok_lang=[]
    if item['tvshow']:
        tv_movie='tv'
        name=item['tvshow']
        season=item['season']
        episode=item['episode']
        if len(episode)==1:
          episode_n="0"+episode
        else:
           episode_n=episode
        if len(season)==1:
          season_n="0"+season
        else:
          season_n=season
    else:
        tv_movie='movie'
        name=item['title']
        year=item['year']
    for items in all_lang_codes:
        all_nam_lang[items.lower()]=all_lang_codes[items]['2let']
        if all_lang_codes[items]['3let'] in selected_lang:
            ok_lang.append(items.lower())
        
        
        
   
    headers = {
        'authority': 'subscene.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'origin': 'https://subscene.com',
        'upgrade-insecure-requests': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'sec-fetch-user': '?1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        #'referer': 'https://subscene.com/subtitles/'+name+'-'+year,
        'accept-encoding': 'utf-8',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
       
    }

    data = {
      'query': name,
      'l': ''
    }

    xx=0
    response='Please do not hammer on Subscene'
    x=0
    while 'Please do not hammer on Subscene'  in response:
        response = requests.post('https://subscene.com/subtitles/searchbytitle', headers=headers, data=data).content.decode('utf-8')
        xbmc.sleep(100)
        x+=1
        if x>10:
            break
        
    
    if tv_movie=='tv':
        regex='<h2>TV-Series</h2>.+?<ul>(.+?)</ul'
    else:
        regex='<h2 class="exact">Exact</h2>.+?<ul>(.+?)</ul'
        
    m_pre=re.compile(regex,re.DOTALL).findall(response)
  
    regex='<div class="title">.+?<a href="(.+?)">(.+?)<'
    m=re.compile(regex,re.DOTALL).findall(m_pre[0])
    sc_subtitle=[]
    all_lk=[]

    
    for lk,nm in m:
        check=False
        if tv_movie=='movie':
            tname=nm.split('(')[0].strip()
         
            if name.lower() == tname.lower() and str(year) in nm:
                check=True
        else:
            tname='%s - %s Season'%(name,seasons[int(season)])
           
            if tname.lower()==nm.lower():
                check=True
                
        if check:
            
            x=requests.get('https://subscene.com/'+lk,headers=headers).content.decode('utf-8')
           
            regex='<tr>(.+?)</tr'
            mm_pre2=re.compile(regex,re.DOTALL).findall(x)
            for itm in mm_pre2:
                regex='<a href="(.+?)">.+?<span class=".+?">(.+?)</span>.+?<span>(.+?)</span>'
                mm=re.compile(regex,re.DOTALL).findall(itm)
                if len(mm)>0:
                    
                    lk2,lang,ver=mm[0]
                    lk2=lk2.replace('\t','').replace('\r','').replace('\n','').strip()
                    lang=lang.replace('\t','').replace('\r','').replace('\n','').strip()
                    ver=ver.replace('\t','').replace('\r','').replace('\n','').strip()
                    if tv_movie=='tv':
                        if ('S%sE%s.'%(season_n,episode_n)).lower() not in ver.lower() and ('S%sE%s '%(season_n,episode_n)).lower() not in ver.lower():
                            continue
                    if lk2  in all_lk:
                        continue
                    if lang.lower() not in ok_lang:
                        continue
                    all_lk.append(lk2)
                    xx+=1
                    
                    cd=''
                    hearing='false'
                    if 'td class="a41"' in itm:
                        hearing='true'
                    bad=''
                    if 'l r bad-icon' in itm:
                        bad='[COLOR red]-BAD SUBTITLE-[/COLOR]'
                    if lang.lower() in all_nam_lang:
                        cd=all_nam_lang[lang.lower()]
                    url = "plugin://%s/?action=download&link=%s&filename=%s&source=%s&language=%s" % (__scriptid__,
                                                                'https://subscene.com/'+lk2,
                                                                ver,
                                                                'subscence',
                                                                lang)
                    json_data={'url':url,
                                 'label':lang,
                                 'label2':str(xx)+'. '+prefix_subscene+bad+ver,
                                 'iconImage':"0",
                                 'thumbnailImage':cd,
                                 'hearing_imp':hearing,
                                 'sync': 'false'}
                    sc_subtitle.append(json_data)
    return sc_subtitle

def searchTMDB(type, query, year):
    import requests

    tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'
    
    if int(year) > 0:
        url = "http://api.tmdb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=en" % (
            type,tmdbKey, query, str(year))
    else:
        url = "http://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en" % (
            type,tmdbKey, query)

    json = requests.get(url).json()
    json_results = json["results"]
    myLogger("searchTMDB: json_results - " + repr(json_results))
    json_results.sort(key = lambda x:x["popularity"], reverse=True)
    myLogger("searchTMDB: json_results sorted - " + repr(json_results))
    try:
        tmdb_id = int(json_results[0]["id"])
    except Exception as err:
        return '0000'

 
    url = "http://api.tmdb.org/3/%s/%s/external_ids?api_key=%s&language=en" % (type,tmdb_id, tmdbKey)
    json = requests.get(url).json()
    
    try:
        imdb_id = json["imdb_id"]
    except Exception:
        return '000'
    myLogger('Searching TMDB Found:'+imdb_id)
    return imdb_id

def checkAndParseIfTitleIsTVshowEpisode(manualTitle):  ##### burekas
    try:
        manualTitle = manualTitle.replace("%20", " ")

        matchShow = re.search(r'(?i)^(.*?)\sS\d', manualTitle)
        if matchShow == None:
            return ["NotTVShowEpisode", "0", "0",'']
        else:
            tempShow = matchShow.group(1)
        
        matchSnum = re.search(r'(?i)%s(.*?)E' %(tempShow+" s"), manualTitle)
        if matchSnum == None:
            return ["NotTVShowEpisode", "0", "0",'']
        else:
            tempSnum = matchSnum.group(1)
        
        matchEnum = re.search(r'(?i)%s(.*?)$' %(tempShow+" s"+tempSnum+"e"), manualTitle)
        if matchEnum == None:
            return ["NotTVShowEpisode", "0", "0",'']
        else:
            tempEnum = matchEnum.group(1)

        return [tempShow, tempSnum, tempEnum, 'episode']

    except Exception as err:
        myLogger( "checkAndParseIfTitleIsTVshowEpisode error: '%s'" % err)                
        return ["NotTVShowEpisode", "0", "0",'']
    
def get_TMDB_data_popularity_and_votes_sorted(url,filename):    ##### burekas
    myLogger("searchTMDB: %s" % url)
    json = caching_json(filename,url)
    json_results = json["results"]
    myLogger("searchTMDB: json_results - " + repr(json_results))
    json_results.sort(key = lambda x:x["popularity"], reverse=True)
    json_results.sort(key = lambda x:x["vote_count"], reverse=True)
    myLogger("searchTMDB: json_results sorted - " + repr(json_results))

    return json_results
    
def get_TMDB_data_filtered(url,filename,query,type):    ##### burekas
    myLogger("searchTMDB: %s" % url)
    myLogger("query filtered: %s" % query)
    json = caching_json(filename,url)
    json_results = json["results"]
    myLogger("searchTMDB: json_results - " + repr(json_results))
    if type=='tv':
        json_results.sort(key = lambda x:x["name"]==query, reverse=True)
    else:
        json_results.sort(key = lambda x:x["title"]==query, reverse=True)
    myLogger("searchTMDB: json_results sorted - " + repr(json_results))

    return json_results      

def getIMDB(title):    ##### burekas
	myLogger("ManualSearch for title: %s" % title)

	item = {}
	item['tvshow'], item['season'], item['episode'], item['dbtype'] = checkAndParseIfTitleIsTVshowEpisode(title)
	myLogger("Parse item tvshow result: " + item['tvshow'])    
	myLogger("ManualSearch for item: %s" % repr(item))    

	if item['tvshow'] == 'NotTVShowEpisode':
		item['title'] = title
		item['tvshow'] = ''          
		_query = item['title'].rsplit(' ', 1)[0]    

		try:
			item['year'] = item['title'].rsplit(' ', 1)[1]
			item['title'] = _query            
			if item['year'].isdigit():
				if int(item['year']) > 1900:
					item['imdb_id'] = searchForIMDBID(_query, item)               
					myLogger("item imdb_id %s" % (item['imdb_id']))         
				else:
					#item['year'] is not present a year
					item['imdb_id'] = ''
			else:
				item['imdb_id'] = '' 
		except:  
			item['imdb_id'] = ''        

	else:  # TVShowEpisode
		item['year'] = '0000'
		_query = item['tvshow']    

		_season = item['season'].split("0")
		_episode = item['episode'].split("0")
		if _season[0] == '':
			item['season'] = _season[1]
		if _episode[0] == '':
			item['episode'] = _episode[1]

		item['imdb_id'] = searchForIMDBID(_query, item)                

	try:
		if item['imdb_id']:        
			return item['imdb_id']
		else:
			return 0

	except Exception as err:
		myLogger('Caught Exception: error in manual search: %s' % format(err))
		pass
        
def searchForIMDBID(query,item):  ##### burekas 
    import requests                       
    year=item["year"]
    info=(PTN.parse(query))
    tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'

    if item["tvshow"] and item['dbtype'] == 'episode':   
        type_search='tv'
        filename = 'subs.search.tmdb.%s.%s.%s.json'%(type_search,lowercase_with_underscores(item['tvshow']),year)            
        url="https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en&append_to_response=external_ids"%(type_search,tmdbKey,quote_plus(item['tvshow']))
          #url="https://api.tmdb.org/3/search/tv?api_key=%s&query=%s&year=%s&language=he&append_to_response=external_ids"%(tmdbKey,quote_plus(item['tvshow']),year)
          
          #url='https://www.omdbapi.com/?apikey=8e4dcdac&t=%s&year=%s'%(item["tvshow"],item["year"])

        #json_results = get_TMDB_data_popularity_and_votes_sorted(url,filename)
        json_results = get_TMDB_data_filtered(url,filename,item['tvshow'],type_search)

        try:
            tmdb_id = int(json_results[0]["id"])
        except:
            myLogger( "[%s]" % (e,))
            return 0        

        filename = 'subs.search.tmdb.fulldata.%s.%s.json'%(type_search,tmdb_id)
        url = "https://api.tmdb.org/3/%s/%s?api_key=%s&language=en&append_to_response=external_ids"%(type_search,tmdb_id,tmdbKey)
        myLogger("searchTMDB fulldata id: %s" % url)        
        json = caching_json(filename,url)
        
        try:    imdb_id = json['external_ids']["imdb_id"]
        except:    
            myLogger( "[%s]" % (e,))
            return 0        
                  
        return imdb_id
   
    elif info['title']: # and item['dbtype'] == 'movie':
        type_search='movie'
        filename = 'subs.search.tmdb.%s.%s.%s.json'%(type_search,lowercase_with_underscores(query),year)        
        if int(year) > 0:
            url = "https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=en"%(type_search,tmdbKey,quote(info['title']),year)
        else:
            url = "https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en"%(type_search,tmdbKey,quote(info['title']))

        #json_results = get_TMDB_data_popularity_and_votes_sorted(url,filename)
        json_results = get_TMDB_data_filtered(url,filename,item['title'],type_search)
        
        try:
            tmdb_id = int(json_results[0]["id"])
        except:
            myLogger( "[%s]" % (e,))
            return 0

        filename = 'subs.search.tmdb.fulldata.%s.%s.json'%(type_search,tmdb_id)
        url = "https://api.tmdb.org/3/%s/%s?api_key=%s&language=en&append_to_response=external_ids"%(type_search,tmdb_id,tmdbKey)
        myLogger("searchTMDB fulldata id: %s" % url)        
        json = caching_json(filename,url)
        
        try:    imdb_id = json['external_ids']["imdb_id"]
        except:
            myLogger( "[%s]" % (e,))
            return 0

        return imdb_id
        
def is_local_file_tvshow(item):
    return item["title"] and (int(item["year"])==0 or "smb:" in item["full_path"])
    
def get_subtitles(item,mode_subtitle,imdb_id,all_setting):
    myLogger('getting subs')
    global links_ktuvit,links_wizdom,sc_subtitle,links_subcenter,links_local,links_open
    import requests
    ########################################## Get IMDB ID ###############################################
    myLogger("get_subtitles imdb_id: " + imdb_id)
    myLogger('get_subtitles item: ' + repr(item))

    if mode_subtitle==3:
        dp = xbmcgui . DialogProgress ( )
        if KODI_VERSION>18:
            dp.create('אנא המתן'+'\n'+ 'מחפש כתוביות'+'\n'+ '','')
            dp.update(0, 'אנא המתן'+'\n'+ 'מחפש כתוביות'+'\n'+  imdb_id )
        else:
            dp.create('אנא המתן', 'מחפש כתוביות', '','')
            dp.update(0, 'אנא המתן','מחפש כתוביות',  imdb_id )
 
    #imdb_id=''
    try:
        if Player().isPlaying() and 'tt' not in imdb_id:    # Enable using subtitles search dialog when kodi is not playing
            playerid_query = '{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
            playerid = loads(executeJSONRPC(playerid_query))['result'][0]['playerid']
            imdb_id_query = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": {"playerid": ' + str(playerid) + ', "properties": ["imdbnumber"]}, "id": 1}'
            imdb_id = loads(executeJSONRPC (imdb_id_query))['result']['item']['imdbnumber']

            MyLog("imdb JSONRPC:%s" %imdb_id)
        
    except:    pass
    
    if imdb_id==None:
      imdb_id='0'
    if mode_subtitle==3:
       if KODI_VERSION>18:
        dp.update(0, 'אנא המתן'+'\n'+ 'עדיין מחפש IMDB'+'\n'+  imdb_id )
       else:
           dp.update(0, 'אנא המתן', 'עדיין מחפש IMDB',  imdb_id )
    else:
       notify2(' מחפש מספר IMDB '+imdb_id,all_setting)
    myLogger('get_subtitles: initial imdb_id is ' + imdb_id)

    try:
        myLogger('get_subtitles item: ' + repr(params))

        if not imdb_id[:2]=="tt":
            if item["tvshow"] or is_local_file_tvshow(item):
                type_search = 'tv'
                if item["tvshow"]:
                    s_string=item["tvshow"]
                else:
                    s_string = ("%s S%.2dE%.2d" % (item["title"], int(item["season"]), int(item["episode"])))      
  
                if (params['action'] == 'manualsearch' or params['action'] == 'autosub'):
                    if (item["tvshow"] and params['action'] == 'manualsearch'):
                        s_string = ("%s S%.2dE%.2d" % (item["tvshow"], int(item["season"]), int(item["episode"])))
                    else:                
                        s_string = ("%s S%.2dE%.2d" % (item["title"], int(item["season"]), int(item["episode"])))
                

            else:
                type_search='movie'
                s_string = ("%s %s" %(item["title"], str(item['year'])))

            myLogger('get_subtitles: search for a proper imdb_id - ' + s_string)
            imdb_id = getIMDB(s_string)
            myLogger('get_subtitles: imdb_id that has been founded is ' + imdb_id)

    except Exception as e:
        imdb_id = 0    
        myLogger('get_subtitles: exception searching imdb_id: ' + imdb_id)
        if mode_subtitle==3:
           if KODI_VERSION>18:
            dp.update(0, 'אנא המתן'+'\n'+ 'Wiz כשל '+'\n'+  str(e) )
           else:
               dp.update(0, 'אנא המתן','Wiz כשל ',  str(e) )
        else:
           notify2(' Wiz כשל  '+e,all_setting)
        pass

    #if 'tt' not in str(imdb_id)
    if not imdb_id[:2]=="tt":
        imdb_id = 0
        myLogger('get_subtitles: imdb_id has not been founded - ' + imdb_id)            
    else:
        if mode_subtitle==3:
           if KODI_VERSION>18:
            dp.update(0, 'אנא המתן'+'\n'+ 'מצאתי'+'\n'+  imdb_id )
           else:
               dp.update(0, 'אנא המתן', 'מצאתי',  imdb_id )
        else:
           notify2(' מצאתי'+imdb_id,all_setting)    
    
    
    save_all_data=[]
    thread=[]
    myLogger('get_subtitles: using imdb_id ' +imdb_id+ ' for subtitles searching ')
    
    if all_setting["wizset"]== 'true':
         thread.append(Thread(GetWizJson,imdb_id,mode_subtitle,item["season"],item["episode"],item['file_original_path']))
         #num_of_subs,subtitle,subtitle_list=GetWizJson(imdb_id,mode_subtitle,0,0,item['file_original_path'])    
    if all_setting["ktuvitset"]== 'true':# Ktuvit Search 
       thread.append(Thread(Ktuvit_Search,item,mode_subtitle,imdb_id))
       #num_of_subs,subtitle,saved_data=Ktuvit_Search(item,mode_subtitle,imdb_id)
    if all_setting["subscene"]== 'true':
        thread.append(Thread(search_subscene,item,mode_subtitle))
    if all_setting["aa_subs"]== 'true':# Subcenter Search 
        thread.append(Thread(aa_subs,item,mode_subtitle))
        #num_of_subs,subtitle,saved_data=subcenter_search(item,mode_subtitle)       
    if all_setting["opensubtitle"]== 'true':# Opensubtitle Search
        thread.append(Thread(Search_opensubtitle_in,item,imdb_id,mode_subtitle,all_setting))        

    #if all_setting["subscene"]== 'true':# Subscene Search 
     #  num_of_subs,subtitle,saved_data=search_subscene(item,mode_subtitle)

    #if all_setting["yify"]== 'true':# YIFY Search 
     #  num_of_subs,subtitle,saved_data=search_yify(item,imdb_id,mode_subtitle)
    
    if len(all_setting["storage"])>0 and all_setting["storage_en"]=='true':# Local 
        thread.append(Thread(search_local,item,mode_subtitle,all_setting))
        #num_of_subs,subtitle,saved_data=search_local(item,mode_subtitle,all_setting)
    
          
    for td in thread:
      td.start()
      

    tt={}
    for i in range (0,40): 
      tt[i]="red"
    start_time = time.time()
    #while 1:
    num_live=0

    while 1:
        for threads in thread:
              num_live=0
              string_dp=''

              still_alive=0
              for yy in range(0,len(thread)):
                if not thread[yy].is_alive():
                  num_live=num_live+1
                  tt[yy]="lightgreen"
                else:
                  still_alive=1
                  tt[yy]="red"
              elapsed_time = time.time() - start_time
             
              
              zz=0
             
              if all_setting["wizset"]== 'true':              
                 string_dp=string_dp+(prefix_wizdom.upper()+':[COLOR %s]%s[/COLOR] '%(tt[zz],len( links_wizdom)))
                 zz=zz+1
              if all_setting["ktuvitset"]== 'true':
                 #myLogger('links_ktuvit out:'+str(len(links_ktuvit)))
                 string_dp=string_dp+(prefix_ktuvit.upper()+':[COLOR %s]%s[/COLOR] '%(tt[zz],len( links_ktuvit)))
                 zz=zz+1
              if all_setting["opensubtitle"]== 'true':              
                 string_dp=string_dp+(prefix_open.upper()+':[COLOR %s]%s[/COLOR] '%(tt[zz],len( links_open)))
                 zz=zz+1
              if all_setting["subscene"]== 'true':
                 string_dp=string_dp+(prefix_subscene.upper()+':[COLOR %s]%s[/COLOR] '%(tt[zz],len( sc_subtitle)))
                 zz=zz+1
              if all_setting["aa_subs"]== 'true':              
                string_dp=string_dp+(prefix_acat.upper()+':[COLOR %s]%s[/COLOR] '%(tt[zz],len( links_subcenter)))
                zz=zz+1
              if len(all_setting["storage"])>0:              
                 string_dp=string_dp+(prefix_local.upper()+':[COLOR %s]%s[/COLOR] '%(tt[zz],len( links_local)))
                 zz=zz+1
              
              if mode_subtitle==3:
                if KODI_VERSION>18:
                    dp.update(int(((num_live* 100.0)/(len(thread))) ), ' אנא המתן '+ time.strftime("%H:%M:%S", time.gmtime(elapsed_time))+'\n'+ string_dp+'\n'+  string_dp)
                else:
                    dp.update(int(((num_live* 100.0)/(len(thread))) ), ' אנא המתן '+ time.strftime("%H:%M:%S", time.gmtime(elapsed_time)),string_dp,  string_dp)
             
        if still_alive==0:
            break
        
        if mode_subtitle==3:
          if dp.iscanceled() or elapsed_time>35: 
               
            for threads in thread:
                 if threads.is_alive():
                     stop_all=1
                     threads._Thread__stop()
        xbmc.sleep(100)
    
    if mode_subtitle==3:
      dp.close()
    else:
      notify2(str(string_dp),all_setting)


    save_all_data.append(links_wizdom)
    save_all_data.append(links_ktuvit)
    save_all_data.append(links_open)    
    save_all_data.append(links_subcenter)
    save_all_data.append(sc_subtitle)
    save_all_data.append(links_local)    
    if mode_subtitle==3:
      dp.close()
    dont_save=0

    if len (links_ktuvit)==0 and len(links_wizdom)==0 and len(links_subcenter)==0 and len (links_local)==0 and len(links_open)==0 and len(sc_subtitle)==0:
        dont_save=1
    return save_all_data,imdb_id,dont_save

def get_now_played():
    """
    Get info about the currently played file via JSON-RPC

    :return: currently played item's data
    :rtype: dict
    """
    request = json.dumps({
        'jsonrpc': '2.0',
        'method': 'Player.GetItem',
        'params': {
            'playerid': 1,
            'properties': ['showtitle', 'season', 'episode']
         },
        'id': '1'
    })
    item = json.loads(xbmc.executeJSONRPC(request))['result']['item']
    item['file'] = xbmc.Player().getPlayingFile()  # It provides more correct result
    return item

def search_all(mode_subtitle,all_setting,manual_search=False,manual_title=''):
    global links_wizdom,links_subcenter,links_local,links_ktuvit,links_open,imdbid
    running=1
    if mode_subtitle==3:
       dp = xbmcgui.DialogProgress()
       if KODI_VERSION>18:
            dp.create('מקבל מידע...','Getting item info...'+'\n'+''+'\n'+'')
       else:
           dp.create('מקבל מידע...','Getting item info...','','')
    else:
       notify2('Getting item info',all_setting)
    if mode_subtitle==1:
        try:
            shutil.rmtree(cache_list_folder)
        except: pass
        xbmcvfs.mkdirs(cache_list_folder)
    item = {}
    subs=" "
    
    ########################################## Get Item Data ###############################################
    imdb_id="0"
    
    if manual_search:
        item['3let_language'] = []
        #item['preferredlanguage'] = unicode(urllib.unquote(params.get('preferredlanguage', '')), 'utf-8')
        #item['preferredlanguage'] = xbmc.convertLanguage(item['preferredlanguage'], xbmc.ISO_639_2)
        item['preferredlanguage'] = 'heb'

        pattern = re.compile(r"%20|_|-|\+|\.")
        replaceWith = " "
        manual_title = re.sub(pattern, replaceWith, manual_title)      

        item['title']=manual_title
        item['file_original_path'] = ""
        item['year']='0'
        dialog = xbmcgui.Dialog()
        ret = dialog.select('בחר', ['סרט', 'סדרה'])
        if ret==-1:
          return 0
        else:
            if ret==0:
                item['tvshow'] =''
                item['season'] ='0'
                item['episode']='0'
                isItMovie=True
                isItEpisode=False
                d = dialog.input('הכנס שנה', type=xbmcgui.INPUT_NUMERIC)
                item['year'] = str(d)                
            else:
                item['tvshow']=manual_title
                dialog = xbmcgui.Dialog()
                d = dialog.input('הכנס עונה', type=xbmcgui.INPUT_NUMERIC)
                if d==-1:
                    return 0
                item['season'] =str(d)
                dialog = xbmcgui.Dialog()
                d = dialog.input('הכנס פרק', type=xbmcgui.INPUT_NUMERIC)
                if d==-1:
                    return 0
                item['episode'] =str(d)
                isItMovie=False
                isItEpisode=True
    else:
        if Player().isPlaying():
            try:
                item['season']=int(item['season'])
            except:
                item['season']=''
            try:
                item['episode']=int(item['episode'])
            except:
                item['episode']=''
            item['year'] = getInfoLabel("VideoPlayer.Year")  # Year

            item['season'] = str(getInfoLabel("VideoPlayer.Season"))  # Season
            if item['season']=='' or str(item['season'])=='0':
                item['season'] = 0
            item['episode'] = str(getInfoLabel("VideoPlayer.Episode"))  # Episode

            if item['episode']=='' or str(item['episode'])=='0':
                item['episode'] = 0

            item['tvshow'] = ''
            if item['episode']==0:
                item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")).replace("%20"," ")  # no original title, get just Title
            else:    
                item['title'] = getOriginalTitle().replace("%20"," ")  # Show
                item['tvshow'] = item['title']
                if (item['tvshow']):
                    item['tvshow'] = ("%s S%.2dE%.2d" % (item['tvshow'], int(item["season"]), int(item["episode"])))                 
                
            if item['title'] == "":
                item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")).replace("%20"," ")  # try to get original title
            imdb_id = normalizeString(xbmc.getInfoLabel("VideoPlayer.IMDBNumber"))  # try to get original title

            
            if 'tt' not in imdb_id:
                imdb_id_tmp=xbmc.getInfoLabel("VideoPlayer.Genre") 
                if imdb_id_tmp.startswith('tt'):
                  imdb_id = imdb_id_tmp
                 
            item['file_original_path'] = unquote((Player().getPlayingFile()))  # Full path of a playing file
            item['file_original_path'] = item['file_original_path'].split("?")
            item['file_original_path'] = path.basename(item['file_original_path'][0])[:-4]
            #item['preferredlanguage'] = unicode(urllib.unquote(params.get('preferredlanguage', '')), 'utf-8')
            #item['preferredlanguage'] = xbmc.convertLanguage(item['preferredlanguage'], xbmc.ISO_639_2)
            item['preferredlanguage'] = 'heb'
            item['rar'] = True
            
            if not item['tvshow'] and not (item['title'] and item['year']) :
                now_play_data = get_now_played()
                item['title'],item['year'],item['season'],item['episode']=get_more_data(now_play_data, item['title'])

        else:    # Take item params from window when kodi is not playing
            imdb_id = getInfoLabel("ListItem.IMDBNumber")
            item['year'] = getInfoLabel("ListItem.Year")
            item['season'] = getInfoLabel("ListItem.Season")
            item['episode'] = getInfoLabel("ListItem.Episode")
            item['file_original_path'] = ""
            item['temp'] = False
            item['rar'] = False

            
            if str(item['season'])=='' or str(item['season'])<str(1):
                item['season'] = 0


            if str(item['episode'])=='' or str(item['episode'])<str(1):
                item['episode'] = 0
            if str(item['season']) == '0' or str(item['episode']) == '0':
                item['tvshow'] =''

            else:
                #item['tvshow'] = take_title_from_focused_item()
                item['tvshow'] = takeTitleFromFocusedItem("tvshow") ###### burekas - fix check Hebrew titles in Kodi Library (Offlin subtitles check)
            
            #item['title'] = take_title_from_focused_item().replace("%20"," ")
            item['title'] = takeTitleFromFocusedItem("movie") ###### burekas - fix check Hebrew titles in Kodi Library (Offlin subtitles check)

            item['3let_language'] = []
            #item['preferredlanguage'] = unicode(urllib.unquote(params.get('preferredlanguage', '')), 'utf-8')
            #item['preferredlanguage'] = xbmc.convertLanguage(item['preferredlanguage'], xbmc.ISO_639_2)
            item['preferredlanguage'] = 'heb'
            labelType = getInfoLabel("ListItem.DBTYPE")  #movie/tvshow/season/episode    
            isItMovie = labelType == 'movie' or getCondVisibility("Container.Content(movies)")
            isItEpisode = labelType == 'episode' or getCondVisibility("Container.Content(episodes)")

            if isItMovie:
                item['title'] = getInfoLabel("ListItem.OriginalTitle").replace("%20"," ")
                #item['tvshow'] =''   # burekas Fix for offline subtitles checking for Movies for KT                        
            elif isItEpisode:
                item['title'] = getInfoLabel("ListItem.TVShowTitle").replace("%20"," ")                            
            else:
                item['title'] = "SearchFor..." # In order to show "No Subtitles Found" result.
    
    if item['title'] == "":
      item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title")).replace("%20"," ")  # no original title, get just Title
      
    item['full_path']=getInfoLabel("Player.Filenameandpath")
    
    if mode_subtitle==3:
       if KODI_VERSION>18:
            dp.update(0, 'אנא המתן'+'\n'+'מחפש מספר IMDB'+'\n'+ imdb_id )
       else:
           dp.update(0, 'אנא המתן','מחפש מספר IMDB', imdb_id )
    else:
       notify2('Serching IMDB '+imdb_id,all_setting)
       
    
    clean_title(item)
    #parse_rls_title(item)
    

    if mode_subtitle==3:
           if KODI_VERSION>18:
                dp.update(0, 'מנקה תקיות'+'\n'+ item['title'] )
           else:
               dp.update(0, 'מנקה תקיות', item['title'] )
    else:
           notify2('מנקה תקיות',all_setting)
    num_of_subs=0
    
    list_hash = hashlib.sha256(str(item).encode('utf-8','ignore')).hexdigest()
    last_sub=os.path.join(cache_list_folder, list_hash)
    timed_cache=subtitle_cache().get('save')
    
    if timed_cache!='save':
        try:
            shutil.rmtree(cache_list_folder)
        except: pass
        xbmcvfs.mkdirs(cache_list_folder)
    
    
    if mode_subtitle==3:
           if KODI_VERSION>18:
                dp.update(0, 'יאללה מתחילים לחפש כתוביות'+'\n'+ imdb_id )
           else:
               dp.update(0, 'יאללה מתחילים לחפש כתוביות', imdb_id )
    else:
           notify2('יאללה מתחילים לחפש כתוביות',all_setting)
    #save_all_data,imdb_id,dont_save=get_subtitles(item,mode_subtitle,imdb_id,all_setting)
    dd=[]
    dd.append((item,mode_subtitle,imdb_id,all_setting))
    myLogger('dd:::')
    myLogger(dd)
    
    try:
        save_all_data,imdb_id,dont_save=cache.get(get_subtitles,24,item,mode_subtitle,imdb_id,all_setting, table='subs')
    except:
        myLogger('Error')
        save_all_data = []
        imdb_id = 't00'
        dont_save = 0

    
    if dont_save==1:
        cache.clear([ 'subs'])
    
    links_ktuvit=[]
    links_wizdom=[]
    links_subcenter=[]
    links_local=[]
    links_open=[]
    
    
    if mode_subtitle>1:
      try:
       f = open(last_sub, 'w') 
    
       f.write(json.dumps(save_all_data)) 
       f.close()

       subtitle_cache.set('save','save')
      except: 
        pass
    highest_rating=0

    release_names=['bluray','hdtv','dvdrip','bdrip','web-dl','hdcam','hdrip','webrip']

    if mode_subtitle==3 or mode_subtitle==2:
      all_data=[]
      all_eng=[]
      Quality=(xbmc.getInfoLabel("VideoPlayer.VideoResolution"))+'p'
      for save_data_value in save_all_data:
         json_value2=json.loads(json.dumps(save_data_value))

         for json_value in json_value2:
       
          if 'label' in json_value and 'label2' in json_value and 'iconImage' in json_value and 'thumbnailImage' in json_value and 'sync' in json_value and 'hearing_imp' in json_value:
           array_original=item['file_original_path'].strip().replace("_",".").replace(" ",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")
           array_original=[line.strip().lower() for line in array_original]
           array_subs=json_value['label2'].replace("[COLOR lightskyblue]",'').replace(".srt",'').replace("[COLOR skyblue]",'').replace("[COLOR bisque]",'').replace("[COLOR lightcoral]",'').replace("[COLOR gray]",'').replace("[COLOR burlywood]",'').replace(prefix_open,'').replace(prefix_wizdom,'').replace(prefix_subscene,'').replace("[SCe]",'').replace("[SC]",'').replace("[/COLOR]",'').strip().replace("_",".").replace(" ",".").split(".")
          
           array_subs.pop(0)
           array_subs=[line.strip().lower() for line in array_subs]
           array_subs=[str(x).lower() for x in array_subs if x != '']
           array_subs_original=array_subs

           array_original=[str(x).lower() for x in array_original if x != '']
           if Quality not in array_original and Quality in array_subs:
             array_original.append(Quality)

           for item_2 in release_names:
            if item_2 in array_original and item_2 in array_subs:
              array_original.append(item_2)
              array_original.append(item_2)
              array_original.append(item_2)
              array_subs.append(item_2)
              array_subs.append(item_2)
              array_subs.append(item_2)
           
           precent=similar(array_original,array_subs)

           #if precent==0:
           array_original=xbmc.getInfoLabel("VideoPlayer.title").strip().replace("_",".").replace(" ",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")
           array_subs=json_value['label2'].replace(prefix_ktuvit,'').replace("[SZ]",'').replace("[sz]",'').replace(prefix_subscene,'').replace("[COLOR limegreen]",'').replace("[COLOR lightskyblue]",'').replace(".srt",'').replace("[COLOR skyblue]",'').replace("[COLOR bisque]",'').replace("[COLOR lightcoral]",'').replace("[COLOR gray]",'').replace("[COLOR burlywood]",'').replace(prefix_open,'').replace(prefix_wizdom,'').replace("[SCe]",'').replace("[SC]",'').replace("[/COLOR]",'').strip().replace("_",".").replace(" ",".").split(".")

           array_subs.pop(0)

           if Quality not in array_original and Quality in array_subs:
               array_original.append(Quality)
           array_subs=[str(x).lower() for x in array_subs if x != '']
           array_original=[str(x).lower() for x in array_original if x != '']

           for item_2 in release_names:
            if item_2 in array_original and item_2 in array_subs:
              array_original.append(item_2)
              array_original.append(item_2)
              array_original.append(item_2)
              array_subs.append(item_2)
              array_subs.append(item_2)
              array_subs.append(item_2)

           precent2=similar(array_original,array_subs)

           if precent2>precent:
              precent=precent2
    
           #if 'language=English' in json_value['url'] or 'language=Arabic' in json_value['url'] or 'language=Spanish' in json_value['url']:
           
           if 'language=Hebrew' not in json_value['url'] and 'language=he' not in json_value['url'] and ('language=' in  json_value['url'] or 'Hebrew' not in json_value['label']):
               
               all_eng.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],precent))
           else:

             all_data.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],precent))
      
      if all_setting["sort_subs"]=='true':
        all_data=sorted(all_data, key=lambda x: x[5], reverse=True)
        all_eng=sorted(all_eng, key=lambda x: x[5], reverse=True)
        
      all_data=all_data+all_eng
      
      f = open(last_sub+'_sort', 'w') 
    
      f.write(json.dumps(all_data)) 
      f.close()
       
      if mode_subtitle==2:
          for items in all_data:
             
             
             
             best_sub=items[4]
             highest_rating=items[5]
             label2=items[1]
             label=items[0]
             notify2(str(highest_rating)+' -' +label2+','+label,all_setting)
             if 1:#try:
                 if len(best_sub)>0:
       
                     best_sub_value=download_subs(best_sub)
          
                     subs=best_sub_value
                     
                     __last__ = (xbmc_tranlate_path(os.path.join(__profile__, 'last')))
           
                     try:
               
                       shutil.rmtree(__last__)
                       xbmc.sleep(100)
                     except: pass
                     
                     xbmcvfs.mkdirs(__last__)
                     xbmc.sleep(100)
                     if not os.path.exists(__last__):
                        os.makedirs(__last__)
                     #if ('language=English' in best_sub or  'language=Arabic' in best_sub or 'language=Spanish' in best_sub) and all_setting["auto_translate"]=='true':
                   
                     
                     if 'language=Hebrew' not in best_sub and  'language=he' not in best_sub and all_setting["auto_translate"]=='true' and ('language=' in  best_sub or 'Hebrew' not in label):
                      notify2('[COLOR red]מתרגם... המתן קטנה :-)[/COLOR]',all_setting)
                      try:
                        
                        translate_subs(subs,os.path.join(__last__, "trans.srt"),mode_subtitle)
                        subs=os.path.join(__last__, "trans.srt")
                        notify2('[COLOR red]אוף... הרבה מילים :-) סיימתי תהנה[/COLOR]',all_setting)
                      except Exception as e:
                       myLogger('e1')
                       myLogger(e, logLevel=xbmc.LOGERROR)
                       pass
                     dst=os.path.join(__last__, "last.srt")
                     xbmcvfs.copy(subs, dst)
                     if all_setting["enable_font"]=='true':
                          subs = srt2ass(subs,all_setting)
                     
           
                     json_value2=json.loads(json.dumps(save_all_data))
                     
                     params=getParams('?'+best_sub.split('?')[1])
                     
                     last_sub_download=hashlib.sha256(str(json.dumps(params)).encode('utf-8','ignore')).hexdigest()
                   
                     subtitle_cache_next().set('last_sub', last_sub_download)
                     notify2('[COLOR aqua]כתובית מוכנה[/COLOR]',all_setting)
                     xbmc.Player().setSubtitles(subs)
                     break
      else:
          for items in all_data:
      
              sub_name='[COLOR gold]'+str(items[5])+ "% "+'[/COLOR]'+items[1]
            
              #json_value['label2']='[COLOR gold]'+str(precent)+ "% "+'[/COLOR]'+json_value['label2']
              if item['file_original_path'].replace("."," ") in items[1].replace("."," ") and len(item['file_original_path'].replace("."," "))>5 or items[5]>80:
                     #json_value['label2']='[COLOR gold] GOLD [B]'+json_value['label2']+'[/B][/COLOR]'
                     sub_name='[COLOR gold] GOLD [B]'+sub_name+'[/B][/COLOR]'
              try:
                  listitem = xbmcgui.ListItem(label          = items[0],
                                                label2         = sub_name,
                                                iconImage      = items[2],
                                               
                                                thumbnailImage = items[3]
                                                )
              except:
                listitem = xbmcgui.ListItem(label          = items[0],
                                                label2         = sub_name
                                                
                                                )
                listitem.setArt({'thumb' : items[3], 'icon': items[2]})
              listitem.setProperty( "sync", json_value['sync'] )
              listitem.setProperty( "hearing_imp",json_value['hearing_imp'] )
                   
              addDirectoryItem(handle=int(sys.argv[1]), url=str(items[4]), listitem=listitem, isFolder=False)
    if mode_subtitle==3:
      dp.close()
    # Search Local File
    if mode_subtitle==3:
          
          listitem = ListItem(label=xbmcaddon.Addon().getLocalizedString(32030),label2='[COLOR plum][I]'+ xbmcaddon.Addon().getLocalizedString(32029)+'[/I][/COLOR]')
          url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "open_setting")
          addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)
          
          listitem = ListItem(label=xbmcaddon.Addon().getLocalizedString(32031),label2='[COLOR khaki][I]'+ xbmcaddon.Addon().getLocalizedString(32003)+'[/I][/COLOR]')
          url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "clean")
          addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)

          listitem = ListItem(label=xbmcaddon.Addon().getLocalizedString(32032),label2='[COLOR olive][I]'+ xbmcaddon.Addon().getLocalizedString(32033)+'[/I][/COLOR]')
          url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "keys")
          addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)

          listitem = ListItem(label=xbmcaddon.Addon().getLocalizedString(32032),label2='[COLOR seagreen][I]'+ xbmcaddon.Addon().getLocalizedString(32035)+'[/I][/COLOR]')
          url = "plugin://%s/?action=disable_subs"% (MyScriptID)
          addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)
          '''
          listitem = ListItem(label=xbmcaddon.Addon().getLocalizedString(32032),label2='[COLOR aqua][I]'+ 'יצא קובץ היסטוריה'+'[/I][/COLOR]')
          url = "plugin://%s/?action=export"% (MyScriptID)
          addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)
          '''
    if mode_subtitle==3:
     endOfDirectory(int(sys.argv[1]))
    if all_setting["Debug"] == "true":
        if imdb_id[:2]=="tt":
            Dialog().ok("Debug "+MyVersion,str(item) + "\n\n" + "imdb: "+str(imdb_id))
        else:
            Dialog().ok("Debug "+MyVersion,str(item) + "\n\n" + "NO IDS")

    running=0

def get_item_data():
        item={}
        item['year'] = getInfoLabel("VideoPlayer.Year")  # Year

        item['season'] = str(getInfoLabel("VideoPlayer.Season"))  # Season
        if item['season']=='' or item['season']<1:
            item['season'] = 0
        item['episode'] = str(getInfoLabel("VideoPlayer.Episode"))  # Episode

        if item['episode']=='' or item['episode']<1:
            item['episode'] = 0
        item['tvshow'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))  # Show
        if item['episode']==0:
            item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")).replace("%20"," ")  # no original title, get just Title
        else:    
            item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")).replace("%20"," ")  # Show
        if item['title'] == "":
            item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")).replace("%20"," ")  # try to get original title
        imdb_id = normalizeString(xbmc.getInfoLabel("VideoPlayer.IMDBNumber"))  # try to get original title
   
        item['file_original_path'] = unquote((Player().getPlayingFile()))  # Full path of a playing file
        item['file_original_path'] = item['file_original_path'].split("?")
        item['file_original_path'] = path.basename(item['file_original_path'][0])[:-4]
        #item['preferredlanguage'] = unicode(urllib.unquote(params.get('preferredlanguage', '')), 'utf-8')
        #item['preferredlanguage'] = xbmc.convertLanguage(item['preferredlanguage'], xbmc.ISO_639_2)
        item['preferredlanguage'] = 'heb'
        item['rar'] = True
        item['full_path']=getInfoLabel("Player.Filenameandpath")
        return item
def change_background(all_setting):
        
        
        sublist=os.listdir(__last__)
        sub=os.path.join(__last__, 'last.srt')

        if all_setting["enable_font"]=='true':
          if all_setting["background"]=='false':
           all_setting["background"]='true'
          else:
           all_setting["background"]='false'
          
          sub = srt2ass(sub,all_setting)
        else:
          if all_setting["background"]=='false':
           all_setting["background"]='true'
           sub = srt2ass(sub,all_setting)
          else:
           all_setting["background"]='false'
         
        xbmc.Player().setSubtitles(sub)
        return all_setting

if action=='clear_aa':
    cache.clear([ 'subs_aa','subs'])
    executebuiltin((u'Notification(%s,%s)' % (MyName, MyLang(32004))))
elif action=='search1':
 
  search_all(3,(all_setting))
elif action == 'manualsearch1':
    myLogger(params)
    #searchstring = getParam("searchstring", params)
    #search_all(3,(all_setting))
    #search_all(3,(all_setting),manual_search=True,manual_title=searchstring)
    #ManualSearch(searchstring,1,1,0,item)
    #ManualSearch(searchstring,1,0,' ')
    #endOfDirectory(int(sys.argv[1]))

elif action == 'download':
    
    id = getParam("id", params)
   
    if id=='open_setting' or id=='clean' or id=='keys':
       if id=='open_setting':
         __settings__.openSettings()
       elif id=='clean':
         try:
           shutil.rmtree(MyTmp)
           
         except: pass
         xbmcvfs.mkdirs(MyTmp)
         try:
           shutil.rmtree(cache_list_folder)
         except: pass
         xbmcvfs.mkdirs(cache_list_folder)
         subtitle_cache().delete("credentials")
         subtitle_cache().delete("save")
         cache.clear([ 'subs'])
         
         notify(32004)
       
         
         executebuiltin((u'Notification(%s,%s)' % (MyName, MyLang(32004))))

       elif id=='keys':

         xbmc.executebuiltin('RunScript(special://home/addons/script.subskeys/default.py)')

       try:
        
         refresh_setting()
         sublist=os.listdir(__last__)
         sub=os.path.join(__last__, 'last.srt')

         if all_setting["enable_font"]=='true':
           sub = srt2ass(sub,all_setting)
         listitem = ListItem(label=sub)
         addDirectoryItem(handle=int(sys.argv[1]), url=sub, listitem=listitem,isFolder=False)
       except:
        pass
        
       
    else:
      temp=' '
      MyLog("Download ID:%s"%id)

      if source=='subscence':
        
        if 'episode' in params:
          subs = download_subscene(params["link"],3, params["episode"])
        else:
          subs = download_subscene(params["link"],3)
      elif source=='opensubtitle':
        subs = Download_opensubtitle(params["ID"], params["link"],params["format"],3)
      elif source=='aa_subs':
                    
                    subs = Download_aa(params["link"],3)
                    
      else:

        subs,temp = download(id,language,key,filename,3)
        

      try:
        shutil.rmtree(__last__)
        xbmc.sleep(100)
      except: pass
      xbmcvfs.mkdirs(__last__)
      xbmc.sleep(100)
      
      if not os.path.exists(__last__):
        os.makedirs(__last__)

      last_sub_download=hashlib.sha256(str(json.dumps(params)).encode('utf-8','ignore')).hexdigest()

      subtitle_cache_next().set('last_sub', last_sub_download)

      for sub in subs:

        #if (language=='English' or language=='Arabic' or language=='Spanish')  and all_setting["auto_translate"]=='true':

        if language!='Hebrew'  and all_setting["auto_translate"]=='true' and language!='' and (source=='opensubtitle' or source=='subscence'):
          if 1:#try:
            translate_subs(sub,os.path.join(__last__, "trans.srt"),3)
            sub=os.path.join(__last__, "trans.srt")
          #except Exception as e:
          #  myLogger(e, logLevel=xbmc.LOGERROR)
          #  pass testtest
        if all_setting["history_log"]=='true':
                xbmcvfs.mkdirs(__history__)
                h_file=os.path.join(__history__, "hist_report.txt")
                if os.path.exists(h_file):
                    file = open(h_file, 'r') 
                    all_subs_hist= file.readlines() 
                    file.close()
                else:
                   all_subs_hist=[]
                   
                f_link=[]
                f_name=[]
                f_season=[]
                f_episode=[]
                all_data=[]
                f_original=[]
  
                for items in all_subs_hist:
                    f_name.append(items.split(':::')[0].strip())
                    f_link.append(items.split(':::')[1].strip())
                    
                    f_season.append(items.split(':::')[2].strip())
                    f_episode.append(items.split(':::')[3].strip())
                    f_original.append(items.split(':::')[4].strip())
                    all_data.append((items.split(':::')[0].strip(),items.split(':::')[1].strip(),items.split(':::')[2].strip(),items.split(':::')[3].strip(),items.split(':::')[4].strip()))
                
                new_f_link=getInfoLabel("VideoPlayer.DBID")
                new_f_season=(getInfoLabel("VideoPlayer.Season"))
                new_f_episode=(getInfoLabel("VideoPlayer.Episode"))
                new_f_original=(getInfoLabel("VideoPlayer.OriginalTitle"))
                
                if 'versioname' in params:
                  new_f_name=params['versioname']
                elif 'filename' in params:
                  new_f_name=params['filename']
                else:
                  new_f_name=(os.path.basename(sub))
                new_f_name=new_f_name.replace('.srt','').replace('.sub','')
                if new_f_link in f_link :
                   index_o=f_link.index(new_f_link)
                   if new_f_season.strip()==f_season[index_o].strip() and new_f_episode.strip()==f_episode[index_o].strip():
                       all_data.pop(index_o)
                       all_data.append((new_f_name,new_f_link,new_f_season,new_f_episode,new_f_original))
                else:
                   all_data.append((new_f_name,new_f_link,new_f_season,new_f_episode,new_f_original))
                file = open(h_file, 'w')

                for name_in,link_in,season_in,episode_in,f_original_in in all_data:
                   if season_in=='':
                     season_in=' '
                   if episode_in=='':
                     episode_in=' '
                   file.write(name_in+':::'+link_in+':::'+season_in+':::'+episode_in+':::'+f_original_in+'\n') 
                

                file.close()
        listitem = ListItem(label=sub)
        dst=os.path.join(__last__, "last.srt")
        xbmcvfs.copy(sub, dst)
        if all_setting["enable_font"]=='true':
          sub = srt2ass(sub,all_setting)
        #item=get_item_data()
        '''
        myLogger('sub path')
        myLogger(sub)
        fh = open(sub, 'r') 
        
        f_text=(fh.read())
        encoding=(chardet.detect(f_text)['encoding'])
        final_txt=(f_text.decode(encoding).encode("utf8"))
        '''
        '''
        dbcur.execute("SELECT * FROM AllData WHERE title = '%s'  AND season='%s' AND episode = '%s' AND year='%s' AND tvshow='%s' and file_original_path='%s' and full_path='%s'"%(item['title'].replace("'"," "),item['season'],item['episode'],item['year'],item['tvshow'].replace("'"," "),item['file_original_path'].replace("'"," "),item['full_path'].replace("'"," ")))
     
        match = dbcur.fetchone()
        
        if 'filename' in params:
          final_txt=params['filename'].replace('.srt','').replace('.sub','')
        elif 'versioname' in params:
          final_txt=params['versioname'].replace('.srt','').replace('.sub','')
          
        if match==None:
          
          
          dbcur.execute("INSERT INTO AllData Values ('%s', '%s', '%s', '%s','%s', '%s', '%s','%s');" %  (item['title'].replace("'"," "),item['season'],item['episode'],item['year'],item['tvshow'].replace("'"," "),item['file_original_path'].replace("'"," "),item['full_path'].replace("'"," "),final_txt.replace("'"," ")))
          
          dbcon.commit()
        else:
          dbcur.execute("UPDATE AllData SET subs='%s' WHERE title= '%s'  AND season='%s' AND episode = '%s' AND year='%s' AND tvshow='%s' and file_original_path='%s' and full_path='%s' " %  (final_txt.replace("'"," "),item['title'].replace("'"," "),item['season'],item['episode'],item['year'],item['tvshow'].replace("'"," "),item['file_original_path'].replace("'"," "),item['full_path'].replace("'"," ")))

          dbcon.commit()
        '''
        
       
        
        addDirectoryItem(handle=int(sys.argv[1]), url=sub, listitem=listitem,isFolder=False)
    endOfDirectory(int(sys.argv[1]))
elif action=='clean':
    try:
        shutil.rmtree(MyTmp)
        try:
           shutil.rmtree(cache_list_folder)
        except: pass
        subtitle_cache().delete("credentials")
        cache.clear(['subs'])
        notify(32004)
    except: pass
    executebuiltin((u'Notification(%s,%s)' % (MyName, MyLang(32004))).encode('utf-8'))
elif action=='login':
    login(True)
elif action=='disable_subs':
   myLogger("DISABLE")
   xbmc.Player().setSubtitles("")
   listitem = ListItem(label="a")
   addDirectoryItem(handle=int(sys.argv[1]), url="ww", listitem=listitem,isFolder=False)

   endOfDirectory(int(sys.argv[1]))

elif action=='export':
   myLogger("export")
   browse_dialog = xbmcgui.Dialog()
   iso_file = browse_dialog.browse(type=0, heading='Export Location', shares='files', useThumbs=False, treatAsFolder=True, defaultt='c:', enableMultiple=False)
   
   xbmcvfs.copy(cacheFile, os.path.join(iso_file,'subs_history.db'))
   xbmcgui.Dialog().ok("יצוא",'הועתק')
   

   endOfDirectory(int(sys.argv[1]))
