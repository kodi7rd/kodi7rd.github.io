# -*- coding: utf-8 -*-
import xbmcvfs,xbmcgui,xbmcaddon,xbmc
from xbmcplugin import endOfDirectory, addDirectoryItem
from xbmcgui import ListItem, Dialog
from xbmcvfs import listdir, exists
from xbmc import executebuiltin, getInfoLabel, executeJSONRPC, Player, getCondVisibility
import sys,unicodedata,urllib,zlib,os,zipfile,contextlib,hashlib,shutil,threading
from os import path

import json
from json import loads, load

import re
regexHelper = re.compile('\W+', re.UNICODE)

import codecs
#import cgi
import cache
import socket
import time
import linecache
import PTN,base64

from myLogger import myLogger

try:
    from HTMLParser import HTMLParser
    html_parser_unescape = HTMLParser.HTMLParser().unescape
except ImportError:
    if sys.version_info >= (3, 4):
        import html
        html_parser_unescape = html.unescape

try:
    from urllib import urlretrieve
    from urllib import  unquote_plus, unquote, urlopen, quote
except:
    # import html
    from urllib.request import urlretrieve
    from urllib.parse import  unquote_plus, unquote, quote, quote_plus


from unicodedata import normalize

from srt2ass import srt2ass

from wizdom_api.wizdom import GetWizJson,wizdom_download_sub
from ktuvit_api.ktuvit import GetKtuvitJson,ktuvit_download_sub
from subscene_api import SubtitleAPI
from opensubs_api.opensubtitle import GetOpenSubtitlesJson,Download_opensubtitle
from local_api.local import GetLocalJson

NONE_TITLE_TEXT = 'NoneTitle...' # SearchFor...'

KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
if KODI_VERSION<=18:
    xbmc_translate_path=xbmc.translatePath
else:
    import xbmcvfs
    xbmc_translate_path=xbmcvfs.translatePath

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

# For future change
# from enum import Enum
# class submode(Enum):
#     NEXT_SUB = 1
#     AUTO_SUBS = 2
#     SUBS_DIALOG = 3
# a = submode.AUTO_SUBS.value

class dialogprogress:
    def __init__(self):
        self.dp = xbmcgui.DialogProgress()

    def create(self, *args):
        if KODI_VERSION>18:
            msg = "\n".join(args)
            self.dp.create(msg)
        else:
            self.dp.create(args)

    def update(self, precent, *args):
        if KODI_VERSION>18:
            msg = "\n".join(args)
            self.dp.update(precent, msg);
        else:
            self.dp.update(precent, args)

    def iscanceled(self):
        return self.dp.iscanceled()

    def close(self):
        self.dp.close()


#reload(sys)
#sys.setdefaultencoding('utf8')

socket.setdefaulttimeout(10)
action=None
searchstring=None
myLogger('Subs On')
all_setting=[]
location=0
last_sub_download=''


running=0


global links_wizdom,links_local,links_ktuvit,links_open,imdbid,links_subscene
imdbid=''
links_wizdom=[]
links_ktuvit=[]
links_open=[]
links_subscene=[]
links_local=[]

prefix_wizdom='Wiz'
prefix_ktuvit='Ktu'
prefix_open='Ops'
prefix_subscene='Ssc'
prefix_acat='AC' #AA_CAT
prefix_local='Loc'
# prefix_wizdom='[Wiz]'
# prefix_ktuvit='[Ktu]'
# prefix_open='[Ops]'
# prefix_subscene='[Ssc]'
# prefix_acat='[AC]' #AA_CAT
# prefix_local='[Loc]'

main_languages = ["Kodi", "Spanish", "French", "Arabic", "Russian", "English", "Hebrew"]

#base_aa='aHR0cHM6Ly9yb2NrLnNlZWRob3N0LmV1L2tjYXQxMjMvSHViLw=='

MyAddon = xbmcaddon.Addon()
MyScriptID = MyAddon.getAddonInfo('id')
__settings__ = xbmcaddon.Addon(id=MyScriptID)
MyVersion = MyAddon.getAddonInfo('version')
__profile__ = xbmc_translate_path(MyAddon.getAddonInfo('profile'))

__cwd__ = xbmc_translate_path(MyAddon.getAddonInfo('path'))
__resource__ = xbmc_translate_path(os.path.join( __cwd__, 'resources'))
__languageDirMain__ = xbmc_translate_path(os.path.join( __resource__, 'language'))
__languageDirSources__ = xbmc_translate_path(os.path.join( __resource__, 'language_sources'))
__languageDirEn__ = xbmc_translate_path(os.path.join( __languageDirMain__, 'resource.language.en_gb', 'strings.po'))
__languageDirHe__ = xbmc_translate_path(os.path.join( __languageDirMain__, 'resource.language.he_il', 'strings.po'))
__language__ = MyAddon.getLocalizedString

def setLanguageSettings(type, fromSettings = False):
    if type == "en":
        source_file = xbmc_translate_path(os.path.join( __languageDirSources__, 'original_en_gb_strings.po'))
        shutil.copy(source_file, __languageDirEn__)
        shutil.copy(source_file, __languageDirHe__)
    elif type == "he":
        source_file = xbmc_translate_path(os.path.join( __languageDirSources__, 'force_he_il_strings.po'))
        shutil.copy(source_file, __languageDirEn__)
        shutil.copy(source_file, __languageDirHe__)
    else:
        source_file_en = xbmc_translate_path(os.path.join( __languageDirSources__, 'original_en_gb_strings.po'))
        source_file_he = xbmc_translate_path(os.path.join( __languageDirSources__, 'original_he_il_strings.po'))
        shutil.copy(source_file_en, __languageDirEn__)
        shutil.copy(source_file_he, __languageDirHe__)

    if (fromSettings):
        xbmcgui.Dialog().ok("Settings", "Please restart Kodi.")

setLanguageSettings('kodi', False)

MyTmp = xbmc_translate_path(os.path.join(__profile__, 'temp_download'))
MyZipFolder = xbmc_translate_path(path.join(MyTmp, 'zips'))
MySubFolder = xbmc_translate_path(path.join(MyTmp, 'subs'))
MyZipFolder2 = xbmc_translate_path(os.path.join(MyTmp, 'zips2'))
MySubFolder2 = xbmc_translate_path(os.path.join(MyTmp, 'subs2'))

__temp__ = xbmc_translate_path(os.path.join(__profile__, 'temp_jsons'))
__last__ = xbmc_translate_path(os.path.join(__profile__, 'last'))
__history__ = xbmc_translate_path(os.path.join(__profile__, '__history__'))
__scriptname__ = MyAddon.getAddonInfo('name')
last_sub_path = xbmc_translate_path(os.path.join(__last__, "last.srt"))

if not os.path.exists(__profile__):
     os.makedirs(__profile__)

try:
  if not path.exists(__temp__):
    xbmcvfs.mkdirs(__temp__)
except: pass

cache_list_folder=xbmc_translate_path(os.path.join(__profile__, 'cache_list_folder'))
try:
  if not path.exists(cache_list_folder):
    xbmcvfs.mkdirs(cache_list_folder)
except: pass

fonts_folder=xbmc_translate_path("special://home/")+'media\\fonts'
addon_font_path= MyAddon.getAddonInfo('path')+'\\fonts'
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

subskeys_addon = "script.subskeys"
keymap_addon = "script.keymap"
pathToAddonSubskeys = os.path.join(xbmc_translate_path('special://home/addons'), subskeys_addon)
pathToAddonKeymap = os.path.join(xbmc_translate_path('special://home/addons'), keymap_addon)

class subtitle_cache_next():
    def set(self, table,value):
        try:
            from sqlite3 import dbapi2 as database
        except:
            from pysqlite2 import dbapi2 as database

        cacheFile=os.path.join(__profile__,'database.db')
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
        cacheFile=os.path.join(__profile__,'database.db')
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

        cacheFile=os.path.join(__profile__,'database.db')
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

        cacheFile=os.path.join(__profile__,'database.db')
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
        cacheFile=os.path.join(__profile__,'database.db')
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

def notify2(msg_id,all_setting,timeout=-1):
    if all_setting["popup"]=="1":
        if timeout != -1:
            timeout *= 1000
            xbmc.executebuiltin((u'Notification(%s,%s,%s)' % (__scriptname__, msg_id, timeout)))
        else:
            xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, msg_id)))

def notify3(msg,timeout=-1):
    if timeout != -1:
        timeout *= 1000
        xbmc.executebuiltin((u'Notification(%s,%s,%s)' % (__scriptname__, msg, timeout)))
    else:
        xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, msg)))

def getKodiPreferredPlayerLanugageCode(all_setting):
    DEFAULT_PREF_LANG = 'heb'

    if all_setting["preferred_lang"] == '0':
        try:
            preferredLangResultQuery = {"jsonrpc": "2.0", "id": 1 , "method": "Settings.GetSettingValue", "params": {'setting': 'locale.subtitlelanguage'}}
            preferredLangResultResult = json.loads(xbmc.executeJSONRPC(json.dumps(preferredLangResultQuery)))
            preferredLangResultValue = preferredLangResultResult["result"]["value"]
        except Exception as e:
            myLogger("Error in getKodiPreferredPlayerLanugage: " + repr(e) + " | Set default as 'Hebrew'")
            preferredLangResultValue = 'Hebrew'

    else:
        preferredLangResultValue = main_languages[int(all_setting["preferred_lang"])]

        # preferredLangResultQuery = {"jsonrpc": "2.0", "id": 1 , "method": "Settings.SetSettingValue", "params": {'setting': 'locale.subtitlelanguage', 'value': preferredLangResultValue}}
        # xbmc.executeJSONRPC(json.dumps(preferredLangResultQuery))


    try:
        preferredLanguageCode = xbmc.convertLanguage(preferredLangResultValue, xbmc.ISO_639_2)
        if preferredLanguageCode == '':
            myLogger("preferredLanguageCode is empty | Set default as '%s'" % DEFAULT_PREF_LANG)
            preferredLanguageCode = DEFAULT_PREF_LANG
    except:
        myLogger("Error in getKodiPreferredPlayerLanugage: " + repr(e) + " | Set default as %s" % DEFAULT_PREF_LANG)
        preferredLanguageCode = DEFAULT_PREF_LANG

    myLogger("Preferred Language code: %s" %preferredLanguageCode)
    return preferredLanguageCode


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

    title = NONE_TITLE_TEXT
    if isItMovie and labelMovieTitle and labelYear:
        title = labelMovieTitle + " " + labelYear
    elif isItEpisode and labelTVShowTitle and labelSeason and labelEpisode:
        title = ("%s S%.2dE%.2d" % (labelTVShowTitle, int(labelSeason), int(labelEpisode)))

    return title
'''

def getTVShowOriginalTitle(source="notPlaying"): ###### burekas
    myLogger("getTVShowOriginalTitle")

    #First, check if database has the original title.
    labelTVShowTitle = getTVshowOriginalTitleByJSONandDBid(source)  ##using kodi database json
    #If not, try get the original title by using tmdb api
    if (labelTVShowTitle == "" or not labelTVShowTitle.isascii()):
        labelTVShowTitle = getTVshowOriginalTitleByTMDBapi(source)  ##New way using tmdb api

    return labelTVShowTitle

def takeTitleFromFocusedItem(type="movie"): ###### burekas
    labelMovieTitle = take_listitem_movie_title()
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
        labelTVShowTitle = getTVShowOriginalTitle("notPlaying").replace("%20"," ")

    title = NONE_TITLE_TEXT
    if isItMovie and labelMovieTitle and labelYear:
        title = ("%s" % (labelMovieTitle)) if type == 'movie' else '' ###### burekas
        # title = ("%s %s" % (labelMovieTitle, labelYear)) if type == 'movie' else '' ###### burekas
    elif isItEpisode and labelTVShowTitle and labelSeason and labelEpisode:
        title = ("%s S%.2dE%.2d" % (labelTVShowTitle, int(labelSeason), int(labelEpisode))) if type == 'tvshow' else '' ###### burekas

    return title

def getTVshowOriginalTitleByJSONandDBid(source="notPlaying"): ###### burekas
    myLogger("getTVshowOriginalTitleByJSONandDBid")

    try:
        if (source=="notPlaying"):
            labelDBID = xbmc.getInfoLabel("ListItem.DBID")
        else:
            labelDBID = xbmc.getInfoLabel("VideoPlayer.DBID")

        originalShowTitle = ''

        requestEpisodeDetails = {"jsonrpc": "2.0", "id": 1 , "method": "VideoLibrary.GetEpisodeDetails", "params": {"episodeid": int(labelDBID), "properties": ["tvshowid"]}}
        resultsEpisodeDetails = json.loads(xbmc.executeJSONRPC(json.dumps(requestEpisodeDetails)))

        tvshowDBID = resultsEpisodeDetails["result"]["episodedetails"]["tvshowid"]

        requestTVShowDetails = {"jsonrpc": "2.0", "id": 1 , "method": "VideoLibrary.GetTVShowDetails", "params": {"tvshowid": int(tvshowDBID), "properties": ["originaltitle"]}}
        resultsTVShowDetails = json.loads(xbmc.executeJSONRPC(json.dumps(requestTVShowDetails)))

        tvshowOriginalTitle = resultsTVShowDetails["result"]["tvshowdetails"]["originaltitle"]

        originalShowTitle = tvshowOriginalTitle

        myLogger("getTVshowOriginalTitleByJSONandDBid - originalShowTitle: " + repr(originalShowTitle))
        return originalShowTitle

    except Exception as err:
        myLogger('Caught Exception: error getTVshowOriginalTitleByJSONandDBid: %s' % format(err), logLevel=xbmc.LOGERROR)
        #originalShowTitle = ''
        return ''

def getTVshowOriginalTitleByTMDBapi(source="notPlaying"): ###### burekas
    myLogger("getTVshowOriginalTitleByTMDBapi")

    try:
        if (source=="notPlaying"):
            labelTVShowTitle = xbmc.getInfoLabel("ListItem.TVShowTitle")
            labelYear = xbmc.getInfoLabel("ListItem.Year")
        else:
            labelTVShowTitle = xbmc.getInfoLabel("VideoPlayer.TVShowTitle")
            labelYear = xbmc.getInfoLabel("VideoPlayer.Year")

        myLogger("getTVshowOriginalTitleByTMDBapi: labelTVShowTitle: %s, year: %s" %(labelTVShowTitle,labelYear))

        if labelTVShowTitle != '' and labelTVShowTitle.isascii():
            return normalizeString(labelTVShowTitle)

        originalTitle = ''

        if labelTVShowTitle != '':
            tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'
            filename = 'subs.search.tmdb.%s.%s.%s.json' % ("tv",lowercase_with_underscores(labelTVShowTitle), labelYear)

            # For TV Shows there is no actuall meaning when using the "yeat" param in the url
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
                itemIndex += 1
                if (item['vote_count'] > voteCountMax and item['popularity'] > popularityMax):
                    voteCountMax = item['vote_count']
                    popularityMax = item['popularity']
                    itemIndexMax = itemIndex

            if resultsLen > 0 :
                #originalTitle = json["results"][itemIndexMax]["original_name"]
                originalTitle = json["results"][itemIndexMax]["name"]
            '''

            try:    originalTitle = json_results[0]["name"]
            except Exception as e:
                myLogger( "getTVshowOriginalTitleByTMDBapi originalTitle Error [%s]" % (e,))
                return ''

        myLogger("getTVshowOriginalTitleByTMDBapi - title: " + originalTitle)
        return originalTitle

    except Exception as err:
        myLogger('Caught Exception: error searchTMDB: %s' % format(err), logLevel=xbmc.LOGERROR)
        #originalTitle = ''
        return ''

def lowercase_with_underscores(_str):   ####### burekas
    return unicodedata.normalize('NFKD', _str).encode('utf-8','ignore').decode('utf-8')
    #return normalize('NFKD', (_str)).encode('utf-8', 'ignore')
    #return normalize('NFKD', str(str(str, 'utf-8'))).encode('utf-8', 'ignore')

def caching_json(filename, url):   ####### burekas
    from requests import get

    if (MyAddon.getSetting( "json_cache" ) == "true"):
        json_file = path.join(__temp__, filename)
        if not path.exists(json_file) or not path.getsize(json_file) > 20 or (time.time()-path.getmtime(json_file) > 30*60):
            data = get(url, verify=False, timeout=60)   #timeout = 60 seconds
            open(json_file, 'wb').write(data.content)
        if path.exists(json_file) and path.getsize(json_file) > 20:
            with open(json_file,'r',encoding='utf-8') as json_data:
                json_object = load(json_data)
            return json_object
        else:
            return {}

    else:
        try:
          json_object = get(url, timeout=60).json()
        except:
          json_object = {}
          pass
        return json_object


def download_manager(mode_subtitle,id):
    myLogger("download_manager - source: %s" %(source))
    myLogger("download_manager - id: %s" %(id))
    myLogger("download_manager - mode: %s" %(mode_subtitle))
    myLogger("download_manager - filename: %s" %(filename))
    myLogger("download_manager - language: %s" %(language))

    subs = []
    temp = ' '

    if source=='wizdom' or source=='ktuvit':
        subs,temp = download(id,language,thumbLang,sub_link,filename,mode_subtitle)
    elif source=='opensubtitle':
        #The download link will be fetch and generated only when choosing to download
        subs = download(id,language,thumbLang,sub_link,filename,mode_subtitle)
    elif source=='subscene':
        #Since the "link" is not a download link and since getting the download link is long process
        #The download link will be fetch and generated only when choosing to download
        download_url = subscene.get_download_link(sub_link, language)
        if download_url != '' :
            subs,temp = download(id,language,thumbLang,download_url,'',mode_subtitle)
        #subs,temp = subscene.subscene_download_process(params,mode_subtitle)
    elif source=='local':
        subs,temp = download(id,language,thumbLang,sub_link,filename,mode_subtitle)

    else:
        subs,temp = download(id,language,thumbLang,sub_link,filename,mode_subtitle)
        # try:
        #     if len(subs[0])>0:
        #         subs=subs[0]
        # except:
        #     pass
        myLogger("download_manager - temp: %s" %(temp))


    #if mode_subtitle == 2:
        # subs = rename_sub_filename_with_language_prefix(subs,MySubFolder2,thumbLang)

    myLogger("download_manager - subs: %s" %(subs))
    return subs,temp

def delete_junction(dir_path):
    #myLogger(repr(xbmcvfs.exists(dir_path)))
    if path.exists(dir_path):
        try:
            myLogger("delete_junction: " + repr(dir_path))

            for root, dirs, files in os.walk(dir_path, topdown=False):
                try:
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                except: pass
            os.rmdir(dir_path)

            # option2
            # if xbmcvfs.exists(dir_path):
            #     with os.scandir(dir_path) as entries:
            #         for entry in entries:
            #             if entry.is_dir():
            #                 delete_junction(entry.path)
            #             else:
            #                 os.remove(entry.path)
            #     os.rmdir(dir_path)

            # option3
            # if xbmcvfs.exists(dir_path):
            #     try:
            #         shutil.rmtree(dir_path)
            #     except Exception as e:
            #         pass
        except Exception as e:
            myLogger("delete_junction Error: " + repr(e))

def remove_and_generate_directory(dir_path):
    delete_junction(dir_path)
    xbmcvfs.mkdirs(dir_path)

def remove_and_generate_temp_subs_directories():
    delete_junction(MyTmp)

    try:
        xbmcvfs.mkdirs(MyTmp)

        xbmcvfs.mkdirs(MyZipFolder)
        xbmcvfs.mkdirs(MySubFolder)

        xbmcvfs.mkdirs(MyZipFolder2)
        xbmcvfs.mkdirs(MySubFolder2)

    except Exception as e:
        myLogger("remove_and_generate_temp_subs_directories Error: " + repr(e))


def download(id,language,thumbLang,sub_link,filename,mode_subtitle):
    global all_setting
    try:
        from zfile_18 import ZipFile
    except:
        from zipfile import ZipFile

    import requests

    myLogger("download() : language=%s | mode_subtitle=%s | id=%s | thumbLang=%s | sub_link=%s | filename=%s"
             %(language,mode_subtitle,id,thumbLang,sub_link,filename))

    try:
        temp=[]

        if id=="LOCAL FILE":
            temp.append(filename)
            if mode_subtitle>1:
                return temp," "
            else:
                if len (temp)>0:
                    sub_result=temp[0]
                else:
                    sub_result='0'
                return sub_result,True

        else:
            subtitle_list = []
            exts = [".srt", ".sub", ".str"]

            if 'wizdom$$$' in id:
                remove_and_generate_temp_subs_directories()
                id = id.replace('wizdom$$$','')
                archive_file = path.join(MyZipFolder, 'wizdom.sub.'+id+'.zip')
                wizdom_download_sub(id,archive_file)

            elif 'ktuvit$$$' in id:
                remove_and_generate_temp_subs_directories()
                #ktuvit doesn't download zip, it builds the subtitle file directly from data as plain text file
                return ktuvit_download_sub(id,mode_subtitle)

            elif 'opensubs$$$' in id:
                remove_and_generate_temp_subs_directories()
                id = id.replace('opensubs$$$','')
                #opensubtitles doesn't download zip, it builds the subtitle file directly from data as plain text file
                return Download_opensubtitle(id ,mode_subtitle)

            elif 'subscene$$$' in id:
                remove_and_generate_temp_subs_directories()
                id = id.replace('subscene$$$','')
                archive_file = path.join(MyZipFolder, 'subscene.sub.'+id+'.zip')

                if not path.exists(archive_file):
                    subscene.download_zip(sub_link, archive_file)

            else:
                #archive_file = path.join(MyZipFolder, 'other.sub.'+id+'.zip')
                myLogger('ERROR IN Download: Unknown source - ' + id , logLevel=xbmc.LOGERROR)
                if mode_subtitle>1:
                    return '',False
                else:
                    return 'NO',False


            # Extract zip file if needed
            #executebuiltin(('XBMC.Extract("%s","%s")' % (archive_file, MySubFolder)).encode('utf-8'), True)
            try:
                with contextlib.closing(ZipFile(archive_file , "r")) as z:
                    z.extractall(MySubFolder)
            except:
                with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                    zip_ref.extractall(MySubFolder)

            myLogger("archive_file: " + repr(archive_file))
            myLogger("MySubFolder: " + repr(listdir(MySubFolder)))
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
                return sub_result,True
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)

        myLogger('ERROR IN Download:'+str(lineno)+',Error:'+str(e), logLevel=xbmc.LOGERROR)
        notify2(colorize_text(" Error: ","red")+str(lineno)+' E:'+str(e),all_setting)

    if mode_subtitle>1:
        return '',False
    else:
        return 'NO',False

def rename_sub_filename_with_language_prefix(sub, dir, lang):
    log_prefix = "Renaming :: "
    updated_subs = ''
    # updated_subs = []
    myLogger(log_prefix + repr(sub))
    myLogger(log_prefix + "lang: %s" %lang)

    if (lang==''):
        lang = "he"

    #for sub in subs:
    try:
        old_full_path_filename = sub
        myLogger(log_prefix + "Sub old filename path: " + repr(old_full_path_filename))
        old_filename = os.path.basename(old_full_path_filename)
        sub_temp = (old_filename.replace(" - No ","").replace("-No ","").replace(".no.","")
                                .replace("HI.",".").replace("- HI.",".").replace("-HI.","."))
        myLogger(log_prefix + "Rename filename: " + repr(old_filename))

        parts = sub_temp.split('.')
        parts.insert(-1, lang)
        new_filename = '.'.join(parts)

        myLogger(log_prefix + "To this filename: " + repr(new_filename))
        new_full_path_filename_before = path.join(dir, old_filename)
        new_full_path_filename_after = path.join(dir, new_filename)

        _filename_path = ''
        if os.path.isfile(old_full_path_filename):
            if not os.path.exists(new_full_path_filename_before):
                shutil.copy(old_full_path_filename, dir)
            os.replace(new_full_path_filename_before, new_full_path_filename_after)
            _filename_path = new_full_path_filename_after
        else:
            _filename_path = old_full_path_filename

        myLogger(log_prefix + "Sub new filename path is: " + repr(_filename_path))
        # updated_subs.append(_filename_path)
        updated_subs = _filename_path

    except Exception as e:
        # updated_subs.append(old_full_path_filename)
        updated_subs = old_full_path_filename
        myLogger(log_prefix + "Renaming Error: " + repr(e), logLevel=xbmc.LOGERROR)

    return updated_subs


def getParams(arg):
    param = []
    paramstring = arg
    if len(paramstring) >= 2:
        params = arg
        cleanedparams = params.replace('?','')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

def getParam(name,params):
    try:
        return unquote_plus(params[name])
    except:    pass

#///////////////////////////////////////Wizdom////////////////////////////////////////////////
def Wizdom_Search(imdb,all_setting,season=0,episode=0,version=0,):

    global links_wizdom

    if all_setting["hebrew"] == 'false':
        return 0,[]

    subtitle_list,json_object = GetWizJson(imdb,prefix_wizdom,color_wizdom,season,episode,version)

    links_wizdom = subtitle_list

    return len(json_object),links_wizdom

#///////////////////////////////////////Ktuvit////////////////////////////////////////////////

def Ktuvit_Search(item,imdb_id,all_setting):
    global links_ktuvit

    if all_setting["hebrew"] == 'false':
        return 0,[]

    parse_rls_title(item)

    myLogger("Ktuvit_Search item:" + repr(item))

    subtitle_list,m_pre = GetKtuvitJson(item,imdb_id,prefix_ktuvit,color_ktuvit)

    links_ktuvit = subtitle_list

    return len(m_pre),links_ktuvit

#///////////////////////////////////////Opensubtitles////////////////////////////////////////////////

def Search_Opensubtitle(item,imdb_id,mode_subtitle,all_setting):
        global links_open

        myLogger("Search_Opensubtitle item:" + repr(item))

        saved_data,search_data = GetOpenSubtitlesJson(item,imdb_id,mode_subtitle,all_setting,prefix_open,color_open)

        links_open=saved_data

        return len(search_data),links_open

#///////////////////////////////////////Subscene////////////////////////////////////////////////

def Subscene_Search(item,imdb_id):
    global links_subscene

    myLogger("Subscene_Search item:" + repr(item))

    subtitle_list,result = subscene.GetSubsceneJson(imdb_id,item,prefix_subscene,color_subscene)

    links_subscene = subtitle_list

    return len(result),links_subscene

#///////////////////////////////////////Local////////////////////////////////////////////////
def Local_Search(item,all_setting):
    global links_local

    myLogger("Local_Search item:" + repr(item))

    subtitle_list = GetLocalJson(item,prefix_local,color_local,all_setting)

    links_local = subtitle_list

    return len(subtitle_list),links_local

#/////////////////////////////////////////////////////////////////////////////////////////////


def clean_title(text):
    try:
        myLogger("clean_title - before: " + repr(text))

        temp=re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", text)

        temp=temp.replace("(","")
        temp=temp.replace(")","")
        temp=temp.replace("[","")
        temp=temp.replace("]","")
        temp=temp.replace("1080 HD","")
        temp=temp.replace("720 HD","")

        if "  - " in temp:
            temp=temp.split("  - ")[0]

        title = path.splitext(temp)

        if len(title) > 1:
            if re.match(r'^\.[a-z]{2,4}$', title[1], re.IGNORECASE):
                text = title[0]
            else:
                text = ''.join(title)
        else:
            text = title[0]

        #text = str(text) #unicode(text, "utf-8")		# burekas fix - offline hebrew titles

        # Removes country identifier at the end
        text = re.sub(r'\([^\)]+\)\W*$', '', text).strip()

        myLogger("clean_title - after: " + repr(text))
        return text

    except Exception as e:
        myLogger("clean_title Error: " + repr(e))

def clean_titles(item):
    try:
        if 'title' in item:
            myLogger("clean_title [title]")
            item['title'] = clean_title(item['title'])
        if 'tvshow' in item:
            myLogger("clean_title [tvshow]")
            item['tvshow'] = clean_title(item['tvshow'])
    except Exception as e:
        myLogger("clean_titles Error: " + repr(e))


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
    global id,language,thumbLang,sub_link,filename,source

    x=0

    __last__ = (xbmc_translate_path(os.path.join(__profile__, 'last')))

    value_for_subs=location

    enable_count=0
    total_count=0
    break_now=0

    for save_data_value in save_all_data:
        if break_now>0:
            break

        lab1,lab2,icn,thu,url,pre=save_data_value

        params = getParams('?'+url.split('?')[1])
        extract_params(params)

        if x == value_for_subs:
            notify2('Downloading',all_setting)
            myLogger('source DOWNLOAD: '+source)

            subs,temp = download_manager(1,id)

            try:
                shutil.rmtree(__last__)
            except: pass
            xbmcvfs.mkdirs(__last__)

            last_sub_download=hashlib.sha256(str(json.dumps(params)).encode('utf-8','ignore')).hexdigest()

            subtitle_cache_next().set('last_sub', last_sub_download)
            if subs!='0' and subs!='NO':
                sub=subs
                if language!='Hebrew'  and all_setting["auto_translate"]=='true' and language!='' and (source=='opensubtitle' or source=='subscene'):
                    translate_subs(sub,os.path.join(__last__, "trans.srt"),3)
                    sub=os.path.join(__last__, "trans.srt")

                dst=last_sub_path
                xbmcvfs.copy(sub, dst)
                if all_setting["enable_font"]=='true':
                    sub = srt2ass(sub,all_setting)
                notify2('Setting sub '+colorize_text(str(total_count) +'/'+str(max_sub-1),"skyblue")+': ' +lab2,all_setting)

                xbmc.Player().setSubtitles(sub)
                break_now=1
                break
            else:
                notify2(colorize_text("Cannot download ","red")+colorize_text(str(total_count) +'/'+str(max_sub-1),"skyblue")+': ' +lab2,all_setting)

        x += 1
        total_count += 1
    return location

color_wizdom = ''
color_ktuvit = 'limegreen'
color_open = 'yellow'
color_subscene = 'lightskyblue'
color_local = 'thistle'
color_result_percent = 'cyan'
color_result_counter = 'white'
# color_acat='bisque' #AA_CAT

def set_providers_colors():
    global color_wizdom,color_ktuvit,color_open,color_subscene,color_local,color_result_percent,color_result_counter
    global all_setting
    '''
    color_wizdom=''
    color_ktuvit='limegreen'
    color_open='yellow'
    color_subscene='lightskyblue'
    color_acat='bisque' #AA_CAT
    color_local='thistle'
    '''

    custom = 'custom'

    cCustomWizdom = all_setting["color_result_wizdom_custom"]
    cCustomKtuvit = all_setting["color_result_ktuvit_custom"]
    cCustomOpen = all_setting["color_result_opensubs_custom"]
    cCustomSubscene = all_setting["color_result_subscene_custom"]
    cCustomlocal = all_setting["color_result_local_custom"]

    cWizdom = all_setting["color_result_wizdom"]
    cKtuvit = all_setting["color_result_ktuvit"]
    cOpen = all_setting["color_result_opensubs"]
    cSubscene = all_setting["color_result_subscene"]
    clocal = all_setting["color_result_local"]

    color_wizdom = cCustomWizdom if cWizdom == custom else cWizdom
    color_ktuvit = cCustomKtuvit if cKtuvit == custom else cKtuvit
    color_open = cCustomOpen if cOpen == custom else cOpen
    color_subscene = cCustomSubscene if cSubscene == custom else cSubscene
    color_local = cCustomlocal if clocal == custom else clocal

    '''
    cCustomPercent = all_setting["color_result_percent_custom"]
    cCustomCounter = all_setting["color_result_counter_custom"]
    cPercent = all_setting["color_result_percent"]
    cCounter = all_setting["color_result_counter"]
    color_result_percent = cCustomPercent if cPercent == custom else cPercent
    color_result_counter = cCustomCounter if cCounter == custom else cCounter
    '''

    myLogger("Colors: color_wizdom=%s | color_ktuvit=%s | color_open=%s | color_subscene=%s | color_local=%s" %(color_wizdom,color_ktuvit,color_open,color_subscene,color_local))

settings_list = {
                    "OSuser":MyAddon.getSetting("OSuser"),
                    "OSpass":MyAddon.getSetting("OSpass"),
                    "OS_API_KEY":MyAddon.getSetting("OS_API_KEY"),
                    "wizset":MyAddon.getSetting("wizset"),
                    "subscene":MyAddon.getSetting("subscene"),
                    "opensubtitle":MyAddon.getSetting("opensubtitle"),
                    "autosub":MyAddon.getSetting("autosub"),
                    "pause":MyAddon.getSetting("pause"),
                    "sync_percent":MyAddon.getSetting("sync_percent"),
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
                    "force":MyAddon.getSetting("force"),
                    "avoid_on_built_in":MyAddon.getSetting("avoid_on_built_in"),
                    "popup":MyAddon.getSetting("popup"),
                    "local_path":MyAddon.getSetting("local_path"),
                    "ktuvitset":MyAddon.getSetting("ktuvitset"),
                    "ktcode":MyAddon.getSetting("ktcode"),
                    "sort_subs":MyAddon.getSetting("sort_subs"),
                    "auto_translate":MyAddon.getSetting("auto_translate"),
                    "hebrew":MyAddon.getSetting("hebrew"),
                    "english":MyAddon.getSetting("english"),
                    "russian":MyAddon.getSetting("russian"),
                    "arabic":MyAddon.getSetting("arabic"),
                    "french":MyAddon.getSetting("french"),
                    "spanish":MyAddon.getSetting("spanish"),
                    "history_log":MyAddon.getSetting("history_log"),
                    "other_lang":MyAddon.getSetting("other_lang"),
                    "local_dir":MyAddon.getSetting("local_dir"),
                    "all_lang":MyAddon.getSetting("all_lang"),
                    "preferred_lang":MyAddon.getSetting("preferred_lang"),
                    "exlude_local_files_smb":MyAddon.getSetting("exlude_local_files_smb"),
                    "Debug":MyAddon.getSetting("Debug"),
                    "color_result_wizdom":MyAddon.getSetting("color_result_wizdom"),
                    "color_result_wizdom_custom":MyAddon.getSetting("color_result_wizdom_custom"),
                    "color_result_ktuvit":MyAddon.getSetting("color_result_ktuvit"),
                    "color_result_ktuvit_custom":MyAddon.getSetting("color_result_ktuvit_custom"),
                    "color_result_opensubs":MyAddon.getSetting("color_result_opensubs"),
                    "color_result_opensubs_custom":MyAddon.getSetting("color_result_opensubs_custom"),
                    "color_result_subscene":MyAddon.getSetting("color_result_subscene"),
                    "color_result_subscene_custom":MyAddon.getSetting("color_result_subscene_custom"),
                    "color_result_local":MyAddon.getSetting("color_result_local"),
                    "color_result_local_custom":MyAddon.getSetting("color_result_local_custom"),
                    "result_style":MyAddon.getSetting("result_style")
                }

def refresh_setting():
    global all_setting,settings_list

    all_setting = {}
    all_setting=settings_list

    '''
    "color_result_percent":MyAddon.getSetting("color_result_percent"),
    "color_result_percent_custom":MyAddon.getSetting("color_result_percent_custom"),
    "color_result_counter":MyAddon.getSetting("color_result_counter"),
    "color_result_counter_custom":MyAddon.getSetting("color_result_counter_custom")
    '''

    set_providers_colors()

    temp = json.dumps(all_setting)
    return json.loads(temp)

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

def extract_params(params):
    global id, language, thumbLang, sub_link, filename, source

    try:
        id = getParam("id", params)
    except:
        id = ''
    try:
        language = params["language"]
    except:
        language = ''
    try:
        thumbLang = params["thumbLang"]
    except:
        thumbLang = ''
    try:
        sub_link = params["link"]
    except:
        sub_link = ''
    try:
        filename = params["filename"]
    except:
        filename = ''
    try:
        source = params["source"]
    except:
        source = ''


extract_params(params)

all_setting = refresh_setting()

#subscene init
#subscene = SubtitleAPI('English','Hebrew') # pass languages you want to have in results
#subscene = SubtitleAPI('Hebrew') # pass languages you want to have in results
selected_langs=[]

for _lang in main_languages:
    if (_lang.lower() in all_setting
        and all_setting[_lang.lower()] == 'true'):
        selected_langs.append(_lang)
if len(all_setting["other_lang"]) > 0:
    all_lang=all_setting["other_lang"].split(",")
    for item in all_lang:
        selected_langs.append(str(convertLanguage(item, xbmc.ENGLISH_NAME)))
if all_setting["all_lang"] == 'true':
    selected_langs=[]
myLogger('Allsubs Langs: ' + repr(selected_langs))
subscene = SubtitleAPI(*selected_langs) # pass languages you want to have in results


def similar(w1, w2):
    from difflib import SequenceMatcher

    s = SequenceMatcher(None, w1, w2)
    return int(round(s.ratio()*100))

def download_subs(link):
    global id, language, thumbLang, sub_link, filename, source

    params = getParams(link)
    extract_params(params)

    myLogger('source=='+source)

    subs,temp = download_manager(2,id)

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


def rtl(text):
    try:
        text=html_parser_unescape(text.decode('utf-8'))
    except Exception as e:
        import xml.sax.saxutils as saxutils
        text=saxutils.unescape(text.decode('utf-8'))

    test_t=text[-1:]

    if test_t=='.' or test_t=='?' or test_t=='!'or test_t==','or test_t=='(':
       text=test_t+text[:len(text)-1]+' '

    return text


def translate_subs(input_file,output_file,mode_subtitle,targetlang='he'):
    try:
        import chardet

        myLogger('translate_subs - starting | targetlang: %s' %targetlang)
        translate_dp_message = __language__(32109) + str(xbmc.convertLanguage(targetlang,xbmc.ENGLISH_NAME))+"..."
        translate_notify_message = __language__(32109) + str(xbmc.convertLanguage(targetlang,xbmc.ENGLISH_NAME))+ "..."
        # sourcelang='eng'

        if mode_subtitle == 3:
            dp = dialogprogress()
            dp.create(__language__(32107),translate_dp_message)
            dp.update(0, translate_dp_message)
        elif mode_subtitle == 2 and all_setting["popup"] != "0":
            notify3(colorize_text(translate_notify_message,'aqua'),2)

        # url = 'https://www.googleapis.com/language/translate/v2?key={0}&q={1}&source={2}&target={3}'
        # api_key='AIzaSyCk5TfD_K1tU1AB2salwn2Lb_yZbesSmY8'

        # Open the file as binary data
        with open(input_file, 'rb') as f:
            # Join binary lines for specified number of lines
            rawdata = f.read()

        encoding=chardet.detect(rawdata)['encoding']
        myLogger('translate_subs - sub encoding: ' + encoding)

        text=rawdata

        if encoding=='ISO-8859-7':
            text=text.decode('cp1253','ignore')
        elif encoding=='MacCyrillic':
            text=text.decode('cp1256','ignore')
        else:
            text=text.decode(encoding,'ignore')

        from gtn.google_trans_new import google_translator
        translator = google_translator()

        # all_text_p1=[]
        # all_data=''
        # counter=0

        split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
        ax2 = split_string(text,4000)
        f_sub_pre = ''

        xx = 0
        for items in ax2:
            percent_translate_progress = int(((xx * 100.0) / (len(ax2)-1)) )
            if mode_subtitle == 3:
                dp.update(percent_translate_progress, translate_dp_message, str(percent_translate_progress)+'%')
                # dp.update(percent_translate_progress, ' מתרגם ' + encoding, str(percent_translate_progress)+'%')
            elif mode_subtitle == 2 and all_setting["popup"]!="0":
                notify3(colorize_text(translate_notify_message + " " + str(percent_translate_progress)+'%','aqua'),3)

            if (items != None):
                translation = translator.translate(items, lang_tgt=targetlang)
            # time.sleep(1)
                f_sub_pre += translation
            xx += 1

        all_text = f_sub_pre.replace(': ',':').replace('"# ','"#').split('\r\n')

        f_all = ''
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

        myLogger('translate_subs - Done')
        # return f_all
        return True
    except Exception as e:
        myLogger('translate_subs - Error: [%s]' %(e))
        return False

#not in use
def searchTMDB(type, query, year):
    import requests
    myLogger("searchTMDB")

    tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'

    if int(year) > 0:
        url = "http://api.tmdb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=en" % (
            type,tmdbKey, query, str(year))
    else:
        url = "http://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en" % (
            type,tmdbKey, query)

    json = requests.get(url, timeout=60).json()
    json_results = json["results"]
    myLogger("searchTMDB: json_results - " + repr(json_results))
    json_results.sort(key = lambda x:x["popularity"], reverse=True)
    myLogger("searchTMDB: json_results sorted - " + repr(json_results))
    try:
        tmdb_id = int(json_results[0]["id"])
    except Exception as err:
        myLogger("searchTMDB Error: " + repr(err))
        return '0000'


    url = "http://api.tmdb.org/3/%s/%s/external_ids?api_key=%s&language=en" % (type,tmdb_id, tmdbKey)
    json = requests.get(url, timeout=60).json()

    try:
        imdb_id = json["imdb_id"]
    except Exception as err:
        myLogger("searchTMDB Error: " + repr(err))
        return '0000'

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
    myLogger("get_TMDB_data_popularity_and_votes_sorted: json_results - " + repr(json_results))
    # 1st priority: popularity
    # 2nd priority: vote_count
    json_results.sort(key = lambda x:(x["popularity"],x["vote_count"]), reverse=True)
    # json_results = sorted(json_results, key = lambda x:(x["popularity"],x["vote_count"]), reverse=True)
    # json_results.sort(key = lambda x:x["popularity"], reverse=True)
    # json_results.sort(key = lambda x:x["vote_count"], reverse=True)
    myLogger("get_TMDB_data_popularity_and_votes_sorted: json_results sorted - " + repr(json_results))

    return json_results

def get_TMDB_data_filtered(url,filename,query,type,year=0):    ##### burekas
    myLogger("searchTMDB: %s" % url)
    myLogger("query filtered: %s" % query)
    json = caching_json(filename,url)
    json_results = json["results"]
    myLogger("get_TMDB_data_filtered: json_results - " + repr(json_results))
    if type=='tv':
        json_results.sort(key = lambda x:x["name"]==query, reverse=True)
    else:
        if int(year) > 0:
            json_results.sort(key = lambda x:(x["title"]==query,str(year) in str(x["release_date"])), reverse=True)
            #json_results.sort(key = lambda x:(x["title"]==query), reverse=True)
        else:
            json_results.sort(key = lambda x:x["title"]==query, reverse=True)
    myLogger("get_TMDB_data_filtered: json_results sorted - " + repr(json_results))

    return json_results

def getIMDB(title,imdb_id):    ##### burekas
    myLogger("getIMDB: SelfSearch for title: %s" % title)

    item = {}
    item['imdb_id'] = imdb_id #previous imdb_id
    item['tvshow'], item['season'], item['episode'], item['dbtype'] = checkAndParseIfTitleIsTVshowEpisode(title)
    myLogger("Parse item tvshow result: " + item['tvshow'])
    myLogger("getIMDB: SelfSearch for item: %s" % repr(item))

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
        if item['imdb_id'] != '' or item['imdb_id'] == '0':
            return item['imdb_id']
        else:
            return '0'

    except Exception as err:
        myLogger('getIMDB: Caught Exception: error in self search: %s' % format(err))
        pass

def searchForIMDBID(query,item):  ##### burekas
    myLogger("searchForIMDBID")
    myLogger("searchForIMDBID - item: " + repr(item))
    myLogger("searchForIMDBID - query: " + repr(query))

    tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'

    info=(PTN.parse(query))

    if item["tvshow"] and item['dbtype'] == 'episode':
        type_search='tv'
        temp_query = item["tvshow"]
        year = 0 #year = item["year"]
        url="https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en&append_to_response=external_ids"%(type_search,tmdbKey,quote_plus(temp_query))
        #url="https://api.tmdb.org/3/search/tv?api_key=%s&query=%s&year=%s&language=he&append_to_response=external_ids"%(tmdbKey,quote_plus(temp_query),year)
        #url='https://www.omdbapi.com/?apikey=8e4dcdac&t=%s&year=%s'%(temp_query,item["year"])

    elif info['title']: # and item['dbtype'] == 'movie':
        type_search='movie'
        temp_query = info['title'] # was item['title'] for get_TMDB_data_filtered, and 'query' for filename
        year = item["year"]
        if int(year) > 0:
            url = "https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=en"%(type_search,tmdbKey,quote(temp_query),year)
        else:
            url = "https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en"%(type_search,tmdbKey,quote(temp_query))

    filename = 'subs.search.tmdb.%s.%s.%s.json'%(type_search,lowercase_with_underscores(temp_query),year)
    #json_results = get_TMDB_data_popularity_and_votes_sorted(url,filename)

    json_results = get_TMDB_data_filtered(url,filename,temp_query,type_search,year)

    try:
        tmdb_id = int(json_results[0]["id"])
    except Exception as e:
        myLogger("searchForIMDBID (%s_1) Error: [%s]" % (type_search,e))
        tmdb_id = ''
        pass
        # return "0"

    if tmdb_id == '':
        if item['imdb_id'] != '':
            tmdb_id = item['imdb_id']
        else:
            return "0"

    filename = 'subs.search.tmdb.fulldata.%s.%s.json'%(type_search,tmdb_id)
    url = "https://api.tmdb.org/3/%s/%s?api_key=%s&language=en&append_to_response=external_ids"%(type_search,tmdb_id,tmdbKey)
    #url = "https://api.themoviedb.org/3/%s/%s?api_key=%s&language=en-US&append_to_response=external_ids"%(type_search,tmdb_id,tmdbKey)
    myLogger("searchTMDB fulldata id: %s" % url)

    json = caching_json(filename,url)

    try:
        imdb_id = json['external_ids']["imdb_id"]
    except Exception as e:
        myLogger("searchForIMDBID (%s_2) Error: [%s]" % (type_search,e))
        return "0"

    return imdb_id


def is_local_file_tvshow(item):
    try:
        return item["title"] and (int(item["year"]) == 0) # or "smb:" in item['full_path'])
    except:
        return False

def get_subtitles(item, mode_subtitle, imdb_id, all_setting):
    myLogger('getting subs')
    global links_wizdom,links_ktuvit,links_open,links_subscene,links_local
    ########################################## Get IMDB ID ###############################################
    if imdb_id == None:
        imdb_id = '0'

    myLogger("get_subtitles imdb_id: " + imdb_id)
    myLogger('get_subtitles item: ' + repr(item))

    if mode_subtitle == 3:
        dp = dialogprogress()
        dp.create(__language__(32107), __language__(32108))
        dp.update(0, __language__(32108)) #, imdb_id)

    if mode_subtitle==3:
        dp.update(0, __language__(32110)) #, imdb_id)
    else:
        notify2(__language__(32110), all_setting)

    myLogger('get_subtitles: initial imdb_id is ' + imdb_id)

    try:
        myLogger('get_subtitles main item: ' + repr(params))

        if not imdb_id[:2] == "tt":
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
            imdb_id = getIMDB(s_string, imdb_id)
            myLogger('get_subtitles: imdb_id that has been founded is ' + imdb_id)

    except Exception as e:
        imdb_id = '0'
        myLogger('get_subtitles: exception searching imdb_id: ' + imdb_id)
        if mode_subtitle == 3:
            dp.update(0, __language__(32112), str(e))
        else:
           notify2(__language__(32112)+ " " + e,all_setting)
        pass

    #if 'tt' not in str(imdb_id)
    if not imdb_id[:2] == "tt":
        imdb_id = '0'
        myLogger('get_subtitles: imdb_id has not been founded - ' + imdb_id)
    else:
        if mode_subtitle == 3:
            dp.update(0, __language__(32113), imdb_id)
        else:
            notify2(__language__(32113) + ": " +imdb_id, all_setting)


    save_all_data = []
    threads = []
    myLogger('get_subtitles: using imdb_id ' +imdb_id+ ' for subtitles searching ')


    if all_setting["wizset"] == 'true':
        threads.append(Thread(Wizdom_Search,imdb_id,all_setting,item["season"],item["episode"],item['file_original_path']))
        #num_of_subs,subtitle,subtitle_list=Wizdom_Search(imdb_id,mode_subtitle,0,0,item['file_original_path'])
    if all_setting["ktuvitset"] == 'true':# Ktuvit Search
        threads.append(Thread(Ktuvit_Search,item,imdb_id,all_setting))
        #num_of_subs,subtitle,saved_data=Ktuvit_Search(item,mode_subtitle,imdb_id)
    if all_setting["opensubtitle"] == 'true':# Opensubtitle Search
        threads.append(Thread(Search_Opensubtitle,item,imdb_id,mode_subtitle,all_setting))
    if all_setting["subscene"] == 'true':
        threads.append(Thread(Subscene_Search,item,imdb_id))
        #threads.append(Thread(Subscene_Search,item,mode_subtitle))
        #num_of_subs,subtitle,saved_data=search_subscene(item,mode_subtitle)

    if all_setting["local_dir"] =='true' and len(all_setting["local_path"])>0:# Local
        threads.append(Thread(Local_Search,item,all_setting))
        #num_of_subs,subtitle,saved_data=Local_Search,item,all_setting)

    for td in threads:
        td.start()


    tt={}
    for i in range (0,40):
        tt[i]="red"
    start_time = time.time()
    #while 1:
    num_live=0

    while 1:
        #for td in threads:
        num_live=0
        string_dp=''

        still_alive=0
        for yy in range(0,len(threads)):
            if not threads[yy].is_alive():
                num_live += 1
                tt[yy]="lightgreen"
            else:
                still_alive=1
                tt[yy]="red"
        elapsed_time = time.time() - start_time

        zz=0

        if all_setting["wizset"]== 'true':
            string_dp += prefix_wizdom.upper() + ':' + colorize_text(len(links_wizdom),tt[zz]) + " "
            zz += 1
        if all_setting["ktuvitset"]== 'true':
            #myLogger('links_ktuvit out:'+str(len(links_ktuvit)))
            string_dp += prefix_ktuvit.upper() + ':' + colorize_text(len(links_ktuvit),tt[zz]) + " "
            zz += 1
        if all_setting["opensubtitle"]== 'true':
            string_dp += prefix_open.upper() + ':' + colorize_text(len(links_open),tt[zz]) + " "
            zz += 1
        if all_setting["subscene"]== 'true':
            string_dp += prefix_subscene.upper() + ':' + colorize_text(len(links_subscene),tt[zz]) + " "
            zz += 1
        if all_setting["local_dir"]=='true' and len(all_setting["local_path"])>0:
            string_dp += prefix_local.upper() + ':' + colorize_text(len(links_local),tt[zz]) + " "
            zz += 1

        percent_search_progress = int(((num_live* 100.0)/(len(threads))))
        if mode_subtitle==3:
            dp.update(percent_search_progress,"("+ time.strftime("%M:%S", time.gmtime(elapsed_time))+")" + " " + __language__(32108) + " " + colorize_text(str(percent_search_progress) + "%","lightgreen"), string_dp)
            xbmc.sleep(500)
        elif mode_subtitle == 2 and all_setting["popup"]!="0":
            msg_percent = str(percent_search_progress) + "%"
            notify3(__language__(32108) + " " + colorize_text(msg_percent,"lightgreen"), 0.5)
            xbmc.sleep(200)

        #old end for

        if still_alive==0:
            break

        if mode_subtitle==3:
            if dp.iscanceled() or elapsed_time>45:
                for td in threads:
                    if td.is_alive():
                        stop_all=1
                        td._stop()

        # xbmc.sleep(1000)

    if mode_subtitle==3:
        dp.close()
    else:
        notify2(str(string_dp),all_setting)


    save_all_data.append(links_local)
    save_all_data.append(links_wizdom)
    save_all_data.append(links_ktuvit)
    save_all_data.append(links_open)
    save_all_data.append(links_subscene)

    if mode_subtitle==3:
        dp.close()

    dont_save=0

    if len(links_wizdom)==0 and len(links_ktuvit)==0 and len(links_open)==0 and len(links_subscene)==0 and len (links_local)==0:
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

def calc_sub_percent_sync(sub_filename,array_original):
    #json_value is the subtitle filename
    #array_original is the video/source filename

    release_names=['bluray','blu-ray','bdrip','brrip','brip',
                   'hdtv','hdtvrip','pdtv','tvrip','hdrip','hd-rip','hc',
                   'web','web-dl','web dl','web-dlrip','webrip','web-rip',
                   'dvdr','dvd-r','dvd-rip','dvdrip','cam','hdcam','cam-rip',
                   'screener','dvdscr','dvd-full',
                   'tc','telecine','ts','hdts','telesync']

    resolutions = ['720p','1080p','1440p','2160p','2k','4320p','4k']

    quality = xbmc.getInfoLabel("VideoPlayer.VideoResolution")+'p'

    text = sub_filename

    text = clean_allsubs_tags(text)
    text = replace_chars_from_text(text)
    text = (text.replace(".srt",''))
    # text = remove_brackets_content_from_text(text)
    array_subs = (text.split("."))
    ##array_subs.pop(0)

    #remove empty items from sub array
    array_subs = [element.strip().lower() for element in array_subs if element != '']
    #array_subs=[str(x).lower() for x in array_subs if x != '']

    # remove language code if exist
    if array_subs[-1].lower() != 'hi' and len(array_subs[-1]) == 2:
        array_subs.pop(-1)

    # fix for 'Opensubtitles" subs - remove 'cc' addition ('hi', 'no hi') if exist
    if array_subs[-1].lower()=='hi' and array_subs[-2].lower()=='no':
        array_subs.pop(-1)
        array_subs.pop(-1)
    #array_subs=[element for element in array_subs if element not in ('hi')] # was ('-','no','hi')

    #myLogger("Video source array before compare: %s" %array_original)
    #myLogger("Subtitle array before compare: %s" %array_subs)

    array_original=[element.strip().lower() for element in array_original if element != '']
    #array_original=[element.strip().lower() for element in array_original]
    #array_original=[str(x).lower() for x in array_original if x != '']

    #----------------------------------------------------------------------------------#
    # 1st priority "release name" (+3 if "release name" are equal)
    # 2nd priority "release type" (+2 if "release name" and "release type" are equal)
    # 3th priority "resolution"   (+1 if "release name" and "release type" and "resolution" are equal)
    #----------------------------------------------------------------------------------#

    # Give "release name" more weight (x3) to the ratio score of the compare
    # 1st priority "release name"
    #myLogger("Video source release: %s" %array_original[-1])
    #myLogger("Subtitle release: %s" %array_subs[-1])
    release_name_position = -2 if array_subs[-1].lower()=='hi' else -1
    sub_release_name = array_subs[release_name_position]
    video_release_name = array_original[-1]
    if sub_release_name.lower() == video_release_name.lower():
        for i in range(3):
            array_subs.append(sub_release_name)
            array_original.append(video_release_name)

        # Give "release type" more weight (x2) to the ratio score of the compare
        # 2nd priority "release type"
        sub_release_type = list(set(array_subs).intersection(release_names))
        video_release_type = list(set(array_original).intersection(release_names))
        if len(sub_release_type) > 0 and len(video_release_type) > 0 and sub_release_type[-1] == video_release_type[-1]:
            for i in range(2):
                array_original.append(video_release_type[-1])
                array_subs.append(sub_release_type[-1])

            # 3th priority "resolution"
            video_quality = list(set(array_original).intersection(resolutions))
            sub_quality = list(set(array_subs).intersection(resolutions))
            if len(video_quality) > 0 and len(sub_quality) > 0 and sub_quality[-1] == video_quality[-1]:
                for i in range(1):
                    array_original.append(video_quality[-1])
                    array_subs.append(sub_quality[-1])
                    #myLogger("Video source quality: %s" %repr(video_quality[0]))
                    #myLogger("Subtitle quality: %s" %repr(sub_quality[0]))

    # myLogger("Video source array for compare: %s" %array_original)
    # myLogger("Subtitle array for compare: %s" %array_subs)
    precent = similar(array_original,array_subs)
    return precent

def autosubs_download_first_sub(all_data,mode_subtitle,all_setting,save_all_data):
    counter=0
    for items in all_data:
        counter+=1
        label = items[0]
        label2 = items[1]
        source_prefix = items[2]
        lang_prefix = items[3]
        best_sub = items[4]
        highest_rating = items[5]
        hearing_imp = items[6]

        # notify2(colorize_text(str(highest_rating)+'%',"yellow") + ' - ' +label2+','+label ,all_setting)
        notify2('%s | %s | %s | %s' %(colorize_text(str(highest_rating)+'%',"yellow"),source_prefix,label2,label) ,all_setting,3)

        if len(best_sub) > 0:
            sub = download_subs(best_sub)

            try:
                shutil.rmtree(__last__)
                xbmc.sleep(100)
            except: pass

            xbmcvfs.mkdirs(__last__)
            xbmc.sleep(100)
            if not os.path.exists(__last__):
                os.makedirs(__last__)

            #if ('language=English' in best_sub or  'language=Arabic' in best_sub or 'language=Spanish' in best_sub) and all_setting["auto_translate"]=='true':

            (sub, isSuccess) = translate_subs_and_renaming(sub, best_sub, label, mode_subtitle, all_setting)

            dst=last_sub_path
            xbmcvfs.copy(sub, dst)

            if all_setting["enable_font"]=='true':
                sub = srt2ass(sub,all_setting)

            json_value2 = json.loads(json.dumps(save_all_data))

            params = getParams('?'+best_sub.split('?')[1])

            last_sub_download = hashlib.sha256(str(json.dumps(params)).encode('utf-8','ignore')).hexdigest()

            subtitle_cache_next().set('last_sub', last_sub_download)
            # if all_setting["popup"]!="0" and isSuccess:
            #     notify3(colorize_text(__language__(32101),'aqua'),2)
            if isSuccess:
                if all_setting["popup"] == "1":
                    notify3(colorize_text(__language__(32101),'aqua'),2)
                if all_setting["popup"] == "2":
                    notify3(colorize_text(__language__(32101) + ' | %s Synced' %(colorize_text(str(highest_rating)+'%',"yellow")),'aqua'),2)

            myLogger("AutoSub sub ready: " + repr(sub))

            # listitem = xbmcgui.ListItem(label          = label,
            #                             label2         = label2
            #                             )
            # listitem.setArt({'thumb' : lang_prefix, 'icon': source_prefix})
            # xbmc.Player().updateInfoTag(listitem)

            xbmc.Player().setSubtitles(sub)
            if all_setting["pause"] == '1' and isSuccess: #resume
                xbmc.Player().pause()
            break

def translate_subs_and_renaming(subs_to_translate_path,best_sub_url,label,mode_subtitle,all_setting):
    myLogger("translate_subs_and_renaming - sub language: " + repr(language))
    sub_language_code = xbmc.convertLanguage(language, xbmc.ISO_639_1)
    pref_langauge = getKodiPreferredPlayerLanugageCode(all_setting)
    #pref_langauge = xbmc.convertLanguage(pref_langauge, xbmc.ENGLISH_NAME)
    pref_langauge_code = xbmc.convertLanguage(pref_langauge, xbmc.ISO_639_1)
    myLogger("translate_subs_and_renaming - preferred language: " + repr(pref_langauge_code))
    try:
        isSuccess = True
        sub = subs_to_translate_path

        myLogger("translate_subs_and_renaming - sub path before: " + repr(sub))

        if all_setting["auto_translate"]=='true':
            # translation_in_progress = false
            if (mode_subtitle == 2 and (best_sub_url!='' and label!=''
                                    and sub_language_code!=pref_langauge_code)
                or mode_subtitle == 3 and sub_language_code!=pref_langauge_code):
                    (sub,isSuccess) = start_tranlate_sub(subs_to_translate_path,mode_subtitle,pref_langauge_code)
                    if isSuccess:
                        target_lang = pref_langauge_code
                    else:
                        target_lang = thumbLang
                        notify3(colorize_text(__language__(32105), 'red'),3)
            else:
                target_lang = thumbLang

        else:
            target_lang = thumbLang

        myLogger("translate_subs_and_renaming - target lang: " + repr(target_lang))
        sub = rename_sub_filename_with_language_prefix(sub,MySubFolder2,target_lang)
        myLogger("translate_subs_and_renaming - sub path after: " + repr(sub))
        return (sub,isSuccess);

    except Exception as e:
        myLogger("translate_subs_and_renaming - Error [%s]" %(e))
        return (subs_to_translate_path,False)


class historylog:
    def __init__(self, line):
        self.name = ""
        self.link = ""
        self.season = ""
        self.episode = ""
        self.original = ""

    def parse_line(self, line):
        arr = line.split(' ::: ')
        self.name = arr[0].strip()
        self.link = arr[1].strip()
        self.season = arr[2].strip()
        self.episode = arr[3].strip()
        self.original = arr[4].strip()

    def same_season_episode(self, other):
        return self.season == other.season and self.episode == other.episode

    def __str__(self):
        data = ""
        data += self.name
        data += ' ::: ' + self.link
        data += ' ::: ' + self.season
        data += ' ::: ' + self.episode
        data += ' ::: ' + self.original
        data += '\n'

def check_and_save_history_logs(sub,all_setting):
    if all_setting["history_log"] != 'true':
        return

    xbmcvfs.mkdirs(__history__)
    h_file=os.path.join(__history__, "hist_report.txt")

    all_subs_hist = []
    if os.path.exists(h_file):
        with open(h_file, 'r') as file:
            all_subs_hist = file.readlines()

    all_data={}
    for items in all_subs_hist:
        data = historylog()
        data.parseline(items)
        all_data[data.link] = data

    newdata = historylog()
    newdata.name = params.get('versioname')
    if "" == newdata.name:
        newdata.name = params.get('filename')
    if "" == newdata.name:
        newdata.name = os.path.basename(sub)
    newdata.name = newdata.name.replace('.srt', '').replace('.sub','')

    newdata.link = xbmc.getInfoLabel("VideoPlayer.DBID")
    newdata.season = xbmc.getInfoLabel("VideoPlayer.Season").strip()
    newdata.episode = xbmc.getInfoLabel("VideoPlayer.Episode").strip()
    newdata.original = xbmc.getInfoLabel("VideoPlayer.OriginalTitle")

    data = all_data.get(newdata.link, historylog())
    if newdata.link == data.link:
        if data.same_season_episode(newdata):
            all_data[newdata.link] = newdata
        #else: dont update ?
    else:
        all_data[newdata.link] = newdata

    with open(h_file, 'w') as file:
        for data in all_data:
            file.write(str(data))

def start_tranlate_sub(subs_to_translate,mode_subtitle,targetLang='he'):
    try:
        translated_sub_path = os.path.join(__last__, "trans.srt")
        isSuccess = translate_subs(subs_to_translate,translated_sub_path,mode_subtitle,targetLang)
    except Exception as e:
        myLogger("start_tranlate_sub - Error: " + repr(e), logLevel=xbmc.LOGERROR)
        isSuccess = False
        pass

    dst=subs_to_translate
    xbmcvfs.copy(translated_sub_path, dst)
    return (dst,isSuccess)

def search_all(mode_subtitle,all_setting,manual_search=False,manual_title=''):
    global links_wizdom,links_local,links_ktuvit,links_open,links_subscene,imdbid
    running=1

    myLogger("search_all: mode_subtitle - " + repr(mode_subtitle))

    if mode_subtitle==3:
        dp = dialogprogress()
        dp.create(__language__(32107), __language__(32115))
    else:
        notify2(__language__(32115),all_setting)

    #This case never happens?
    '''
    if mode_subtitle==1:
        try:
            shutil.rmtree(cache_list_folder)
        except: pass
        xbmcvfs.mkdirs(cache_list_folder)
    '''

    item = {}
    subs=" "
    imdb_id="0"

    ########################################## Get Item Data ###############################################

    if manual_search:
        myLogger("search_all: manual_search")
        item, d_value_s, d_value_e = get_manual_search_item_data(item, manual_title)
        if d_value_s == 0 or d_value_e == 0:
            return 0

    else:
        if Player().isPlaying():
            item, imdb_id = get_player_item_data(item)

            if mode_subtitle == 3:
                from autosub import isExcluded
                try:
                    is_excluded = isExcluded(item['full_path'])
                except:
                    is_excluded = False
                if is_excluded:
                    dp.close()
                    results_generate_menu_items()
                    endOfDirectory(int(sys.argv[1]))
                    return
        else:    # Take item params from window when kodi is not playing
            item, imdb_id = get_non_player_item_data(item)

    if item['title'] == "":
        item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title")).replace("%20"," ")  # no original title, get just Title

    #item['full_path']=getInfoLabel("Player.Filenameandpath")

    if mode_subtitle == 3:
        dp.update(0, __language__(32110)) #, imdb_id)
    else:
        notify2(__language__(32110), all_setting)

    clean_titles(item)
    #parse_rls_title(item)

    if mode_subtitle==3:
        dp.update(0, __language__(32114), item['title'])
    else:
        notify2(__language__(32110), all_setting)

    #num_of_subs=0

    list_hash = hashlib.sha256(str(item).encode('utf-8','ignore')).hexdigest()
    last_sub = os.path.join(cache_list_folder, list_hash)
    timed_cache = subtitle_cache().get('save')

    if timed_cache != 'save':
        try:
            shutil.rmtree(cache_list_folder)
        except: pass
        xbmcvfs.mkdirs(cache_list_folder)


    if mode_subtitle == 3:
        dp.update(0,  __language__(32100)) #, imdb_id)
    elif all_setting["popup"] != "0":
        notify3(colorize_text(__language__(32100),'aqua'),2)


    dd = []
    dd.append((item, mode_subtitle, imdb_id, all_setting))
    myLogger('dd::: %s' %(dd))

    try:
        #save_all_data,imdb_id,dont_save = get_subtitles(item,mode_subtitle,imdb_id,all_setting)
        save_all_data, imdb_id, dont_save = cache.get(get_subtitles, 24, item, mode_subtitle, imdb_id, all_setting, table='subs')
    except Exception as e:
        myLogger('Error in cache.get get_subtitles: ' + repr(e))
        save_all_data = []
        imdb_id = 't00'
        dont_save = 0

    if dont_save==1:
        cache.clear(['subs'])

    links_ktuvit=[]
    links_wizdom=[]
    links_subscene=[]
    links_local=[]
    links_open=[]

    if mode_subtitle>1:
        try:
            with open(last_sub, 'w') as f:
                f.write(json.dumps(save_all_data))

            subtitle_cache.set('save','save')
        except:
            pass

    #2 = from autosubs
    #3 = from Subs dialog search (auto/manual)
    if mode_subtitle == 3 or mode_subtitle == 2:
        all_data = results_subs_processing(save_all_data,item,last_sub)

        if mode_subtitle==2:
            if len(all_data) == 0:
                if all_setting["popup"] != "0":
                    notify3(colorize_text(__language__(32106),'aqua'),2)
            else:
                autosubs_download_first_sub(all_data, mode_subtitle, all_setting, save_all_data)
        else:
            counter=0
            ############## Styling subs results and build the result list ###############
            for items in all_data:
                counter+=1
                listitem = results_styling_subs(counter,items,item,manual_title)
                addDirectoryItem(handle=int(sys.argv[1]), url=str(items[4]), listitem=listitem, isFolder=False)

    if mode_subtitle == 3:
        dp.close()
        results_generate_menu_items()
        endOfDirectory(int(sys.argv[1]))

    if all_setting["Debug"] == "true":
        if imdb_id[:2]=="tt":
            Dialog().ok("Debug "+MyVersion,str(item) + "\n\n" + "imdb: "+str(imdb_id))
        else:
            Dialog().ok("Debug "+MyVersion,str(item) + "\n\n" + "NO IDS")

    running=0

def get_manual_search_item_data(item,manual_title):
    item['3let_language'] = []
    #item['preferredlanguage'] = unicode(urllib.unquote(params.get('preferredlanguage', '')), 'utf-8')
    #item['preferredlanguage'] = xbmc.convertLanguage(item['preferredlanguage'], xbmc.ISO_639_2)
    item['preferredlanguage'] = getKodiPreferredPlayerLanugageCode(all_setting)

    pattern = re.compile(r"%20|_|-|\+|\.")
    replaceWith = " "
    manual_title = re.sub(pattern, replaceWith, manual_title)

    item['title']=manual_title
    item['file_original_path'] = ""
    item['full_path'] = ""
    item['year']='0'
    dialog = xbmcgui.Dialog()
    ret = dialog.select('בחר', ['סרט', 'סדרה'])
    if ret == -1:
        return 0
    else:
        if ret == 0:
            item['tvshow'] = ''
            item['season'] = '0'
            item['episode'] = '0'
            #isItMovie=True
            #isItEpisode=False
            d_value_y = dialog.input('הכנס שנה', type=xbmcgui.INPUT_NUMERIC)
            item['year'] = str(d_value_y)
            d_value_s = -1
            d_value_e = -1
        else:
            item['tvshow'] = manual_title
            dialog = xbmcgui.Dialog()
            d_value_s = dialog.input('הכנס עונה', type=xbmcgui.INPUT_NUMERIC)
            # if d==-1:
            #     return 0
            if d_value_s != 0:
                item['season'] =str(d_value_s)
            dialog = xbmcgui.Dialog()
            d_value_e = dialog.input('הכנס פרק', type=xbmcgui.INPUT_NUMERIC)
            # if d==-1:
            #     return 0
            if d_value_e != 0:
                item['episode'] =str(d_value_e)
            #isItMovie=False
            #isItEpisode=True

    return item, d_value_s, d_value_e

def take_video_movie_title():
    # labelMovie = xbmc.getInfoLabel("VideoPlayer.Title")
    # labelMovieOriginal = xbmc.getInfoLabel("VideoPlayer.OriginalTitle")
    # labelMovieTitle = labelMovieOriginal if labelMovieOriginal.isascii() else labelMovie
    labelMovieTitle = xbmc.getInfoLabel("VideoPlayer.OriginalTitle")
    return labelMovieTitle

def take_listitem_movie_title():
    # labelMovie = xbmc.getInfoLabel("ListItem.Title")
    # labelMovieOriginal = xbmc.getInfoLabel("ListItem.OriginalTitle")
    # labelMovieTitle = labelMovieOriginal if labelMovieOriginal.isascii() else labelMovie #xbmc.getInfoLabel("ListItem.OriginalTitle")
    labelMovieTitle = xbmc.getInfoLabel("ListItem.OriginalTitle")
    return labelMovieTitle

def get_player_item_data(item):
    myLogger("get_player_item_data")
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
    #if item['season']=='' or item['season']<1:
    if item['season']=='' or str(item['season'])=='0':
        item['season'] = 0

    item['episode'] = str(getInfoLabel("VideoPlayer.Episode"))  # Episode
    #if item['episode']=='' or item['episode']<1:
    if item['episode']=='' or str(item['episode'])=='0':
        item['episode'] = 0

    #item['tvshow'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))  # Show
    item['tvshow'] = ''

    if item['episode'] == 0:
        labelMovieTitle = take_video_movie_title()
        item['title'] = normalizeString(labelMovieTitle).replace("%20"," ")  # no original title, get just Title
        # if (item['title'].isascii() == False):
        #     item['title'] = getTVShowOriginalTitle().replace("%20"," ")
    else:
        #item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")).replace("%20"," ")  # Show
        item['title'] = getTVShowOriginalTitle("playing").replace("%20"," ")  # Show
        item['tvshow'] = item['title']
        if (item['tvshow']):
            item['tvshow'] = ("%s S%.2dE%.2d" % (item['tvshow'], int(item["season"]), int(item["episode"])))

    if item['title'] == "":
        labelMovieTitle = take_video_movie_title()
        item['title'] = normalizeString(labelMovieTitle).replace("%20"," ")

    imdb_id = normalizeString(xbmc.getInfoLabel("VideoPlayer.IMDBNumber"))  # try to get original title
    if 'tt' not in imdb_id:
        imdb_id_tmp = xbmc.getInfoLabel("VideoPlayer.Genre")
        if imdb_id_tmp.startswith('tt'):
            imdb_id = imdb_id_tmp

    # try:
    #     if Player().isPlaying() and 'tt' not in imdb_id:    # Enable using subtitles search dialog when kodi is not playing
    #         playerid_query = '{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
    #         playerid = loads(executeJSONRPC(playerid_query))['result'][0]['playerid']
    #         imdb_id_query = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": {"playerid": ' + str(playerid) + ', "properties": ["imdbnumber"]}, "id": 1}'
    #         imdb_id = loads(executeJSONRPC (imdb_id_query))['result']['item']['imdbnumber']

    #         MyLog("imdb JSONRPC:%s" %imdb_id)

    # except:
    #     pass

    item['file_original_path'] = prepare_video_filename(Player().getPlayingFile()) # Full path of a playing file
    #item['preferredlanguage'] = unicode(urllib.unquote(params.get('preferredlanguage', '')), 'utf-8')
    #item['preferredlanguage'] = xbmc.convertLanguage(item['preferredlanguage'], xbmc.ISO_639_2)
    item['preferredlanguage'] = getKodiPreferredPlayerLanugageCode(all_setting)
    item['rar'] = True
    item['full_path'] = getInfoLabel("Player.Filenameandpath")
    item['file_name'] = ''

    if not item['tvshow'] and not (item['title'] and item['year']) and "pvr://" not in item['full_path'] :
        now_play_data = get_now_played()
        item['title'],item['year'],item['season'],item['episode']=get_more_data(now_play_data, item['title'])

    return item, imdb_id

def get_non_player_item_data(item):
    myLogger("get_non_player_item_data")

    imdb_id = getInfoLabel("ListItem.IMDBNumber")
    item['year'] = getInfoLabel("ListItem.Year")
    item['season'] = getInfoLabel("ListItem.Season")
    item['episode'] = getInfoLabel("ListItem.Episode")
    item['file_original_path'] = prepare_video_filename(getInfoLabel("ListItem.FileNameAndPath"))
    item['temp'] = False
    item['rar'] = False
    item['full_path']=unquote(getInfoLabel("ListItem.FileNameAndPath"))
    # myLogger("DDDDDDDD "+ repr(getInfoLabel("Container(20).ListItem.Label")))

    if str(item['season'])=='' or str(item['season'])<str(1):
        item['season'] = 0

    if str(item['episode'])=='' or str(item['episode'])<str(1):
        item['episode'] = 0

    if str(item['season']) == '0' or str(item['episode']) == '0':
        item['tvshow'] =''
        item['title'] = takeTitleFromFocusedItem("movie")
    else:
        #item['tvshow'] = take_title_from_focused_item()
        item['tvshow'] = takeTitleFromFocusedItem("tvshow") ###### burekas - fix check Hebrew titles in Kodi Library (Offlin subtitles check)
        item['title'] = getInfoLabel("ListItem.TVShowTitle").replace("%20"," ")

    #item['title'] = take_title_from_focused_item().replace("%20"," ")
    #item['title'] = takeTitleFromFocusedItem("movie") ###### burekas - fix check Hebrew titles in Kodi Library (Offlin subtitles check)

    item['3let_language'] = []
    #item['preferredlanguage'] = unicode(urllib.unquote(params.get('preferredlanguage', '')), 'utf-8')
    #item['preferredlanguage'] = xbmc.convertLanguage(item['preferredlanguage'], xbmc.ISO_639_2)
    item['preferredlanguage'] = getKodiPreferredPlayerLanugageCode(all_setting)

    # labelType = getInfoLabel("ListItem.DBTYPE")  #movie/tvshow/season/episode
    # isItMovie = labelType == 'movie' or getCondVisibility("Container.Content(movies)")
    # isItEpisode = labelType == 'episode' or getCondVisibility("Container.Content(episodes)")

    # if isItMovie:
    #     item['title'] = getInfoLabel("ListItem.OriginalTitle").replace("%20"," ")
    #     #item['tvshow'] =''   # burekas Fix for offline subtitles checking for Movies for KT
    # elif isItEpisode:
    #     item['title'] = getInfoLabel("ListItem.TVShowTitle").replace("%20"," ")
    # else:
    #     item['title'] = NONE_TITLE_TEXT # In order to show "No Subtitles Found" result.

    return item,imdb_id

def prepare_video_filename(filename):
    clean_filename = unquote(filename)
    clean_filename = clean_filename.split("?")
    clean_filename = path.basename(clean_filename[0])[:-4]
    return clean_filename

def is_to_check_percent(item):
    # Check % only when player is playing
    # or not playing and library based on local file:
    # Without 'strm' which is video addon file or 'plugin://' which is video addon menu
    return (Player().isPlaying() or
            not Player().isPlaying() and not (len(item['full_path'])<=1
                                              or any(s in item['full_path'] for s in ['strm','plugin://'])))

def clean_allsubs_tags(text):
    text = (text.replace(prefix_wizdom,'').replace(prefix_ktuvit,'')
                .replace(prefix_open,'').replace(prefix_subscene,'').replace(prefix_acat,'')
                .replace(prefix_local,'').replace("[SCe]",'').replace("[SC]",'').replace("[SZ]",'')
                .replace("[sz]",'').replace("[COLOR "+color_wizdom+"]",'')
                .replace("[COLOR "+color_ktuvit+"]",'').replace("[COLOR "+color_open+"]",'')
                .replace("[COLOR "+color_subscene+"]",'').replace("[COLOR "+color_local+"]",'')
                .replace("[COLOR skyblue]",'').replace("[COLOR lightcoral]",'')
                .replace("[COLOR gray]",'').replace("[COLOR burlywood]",'').replace("[/COLOR]",''))
    return text

def remove_brackets_content_from_text(text):
    # # Count the number of bracket pairs in the text
    # bracket_count = text.count('[')
    # # If there are more than one pair of brackets, remove the last pair and their content
    # if bracket_count > 1:

    # Find the last occurrence of '[' and ']'
    last_open_bracket = text.rfind('[')
    last_close_bracket = text.rfind(']')

    if last_open_bracket != -1 and last_close_bracket != -1 and last_open_bracket < last_close_bracket:
        # Remove the last set of brackets and their content
        text = text[:last_open_bracket] + text[last_close_bracket + 1:]

    return text

def replace_chars_from_text(_text):
    text = (_text.strip()
            .replace("_",".").replace(" ",".")
            .replace("/",".")
            .replace("-",".").replace("+",".")
            .replace("[",".").replace("]",".")
            .replace("(",".").replace(")","."))

    return text

def orginaize_video_filename_for_compare(_text):
    text = remove_brackets_content_from_text(_text)
    text = replace_chars_from_text(text)
    text = (text.replace(".avi","").replace(".mp4","").replace(".mkv",""))
    text = (text.split("."))

    return text

def results_subs_processing(save_all_data,item,last_sub):
    ########## Calc Percent and Langauge Sorting ##########
    all_heb=[]
    all_eng=[]
    all_rus=[]
    all_arb=[]
    all_fre=[]
    all_spn=[]
    all_unknown=[]
    all_other=[]

    ############## Subs Proccessing ###############
    array_original = orginaize_video_filename_for_compare(item['file_original_path'])
    array_original2 = orginaize_video_filename_for_compare(xbmc.getInfoLabel("VideoPlayer.title"))

    for save_data_value in save_all_data:
        json_value2=json.loads(json.dumps(save_data_value))

        for json_value in json_value2:
            if 'label' in json_value and 'label2' in json_value and 'iconImage' in json_value and 'thumbnailImage' in json_value and 'sync' in json_value and 'hearing_imp' in json_value:
                ############## Calc Sync Match Percentage ###############
                if is_to_check_percent(item):
                    percent = calc_sub_percent_sync(json_value['label2'], array_original) if len(array_original) > 1 else 0
                    percent2 = calc_sub_percent_sync(json_value['label2'], array_original2) if len(array_original2) > 1 else 0

                    if percent2 > percent:
                        percent = percent2
                else:
                    percent = 0

                ############## Build subs data ###############
                ############## Language Filtering & attach percent value foe each ###############
                #Sort by lanugage, Hebrew first then all the rest

                #if 'language=English' in json_value['url'] or 'language=Arabic' in json_value['url'] or 'language=Spanish' in json_value['url']:
                # if 'language=Hebrew' not in json_value['url'] and 'language=he' not in json_value['url'] and ('language=' in  json_value['url'] or 'Hebrew' not in json_value['label'] or 'he' not in json_value['label']):
                #     all_eng.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent))
                # else:
                #     all_heb.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent))
                if ('Hebrew' in json_value['label'] or 'hebrew' in json_value['label']
                    or 'He' in json_value['thumbnailImage'] or 'he' in json_value['thumbnailImage']):
                    all_heb.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                elif ('English' in json_value['label'] or 'english' in json_value['label']
                      or 'En' in json_value['thumbnailImage'] or 'en' in json_value['thumbnailImage']):
                    all_eng.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                elif ('Russian' in json_value['label'] or 'russian' in json_value['label']
                      or 'Ru' in json_value['thumbnailImage'] or 'ru' in json_value['thumbnailImage']):
                    all_rus.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                elif ('Arabic' in json_value['label'] or 'arabic' in json_value['label']
                       or 'Ar' in json_value['thumbnailImage'] or 'ar' in json_value['thumbnailImage']):
                    all_arb.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                elif ('French' in json_value['label'] or 'french' in json_value['label']
                        or 'Fr' in json_value['thumbnailImage'] or 'fr' in json_value['thumbnailImage']):
                    all_fre.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                elif ('Spanish' in json_value['label'] or 'spanish' in json_value['label']
                        or 'Es' in json_value['thumbnailImage'] or 'es' in json_value['thumbnailImage']):
                    all_spn.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                elif (len(json_value['label']) == 0 and len(json_value['thumbnailImage']) == 0):
                    all_unknown.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                else:
                    all_other.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))

    ############## Sort by Sync Percentages ###############
    if all_setting["sort_subs"]=='true':
        all_heb     = sorted(all_heb,     key=lambda x: x[5], reverse=True)
        all_eng     = sorted(all_eng,     key=lambda x: x[5], reverse=True)
        all_rus     = sorted(all_rus,     key=lambda x: x[5], reverse=True)
        all_arb     = sorted(all_arb,     key=lambda x: x[5], reverse=True)
        all_fre     = sorted(all_fre,     key=lambda x: x[5], reverse=True)
        all_spn     = sorted(all_spn,     key=lambda x: x[5], reverse=True)
        all_unknown = sorted(all_unknown, key=lambda x: x[5], reverse=True)
        all_other   = sorted(all_other,   key=lambda x: x[5], reverse=True)

    if item['preferredlanguage'] == xbmc.convertLanguage("Hebrew", xbmc.ISO_639_2):
        all_data = all_heb + all_eng + all_rus + all_arb + all_fre + all_spn + all_other
    elif item['preferredlanguage'] == xbmc.convertLanguage("English", xbmc.ISO_639_2):
        all_data = all_eng + all_heb + all_rus + all_arb + all_fre + all_spn + all_other
    elif item['preferredlanguage'] == xbmc.convertLanguage("Russian", xbmc.ISO_639_2):
        all_data = all_rus + all_heb + all_eng + all_arb + all_fre + all_spn + all_other
    elif item['preferredlanguage'] == xbmc.convertLanguage("Arabic", xbmc.ISO_639_2):
        all_data = all_arb + all_heb + all_eng + all_rus + all_fre + all_spn + all_other
    elif item['preferredlanguage'] == xbmc.convertLanguage("French", xbmc.ISO_639_2):
        all_data = all_fre + all_heb + all_eng + all_rus + all_arb + all_spn + all_other
    elif item['preferredlanguage'] == xbmc.convertLanguage("Spanish", xbmc.ISO_639_2):
        all_data = all_spn + all_heb + all_eng + all_rus + all_arb + all_fre + all_other
    else:
        all_data = all_other + all_heb + all_eng + all_rus + all_arb + all_fre + all_spn

    all_data = all_data + all_unknown
    # if all_setting["local_dir"]=='true':
    #     all_data[:0] = all_unknown
    # else:
    #     all_data = all_data + all_unknown

    with open(last_sub+'_sort', 'w') as f:
        f.write(json.dumps(all_data))

    return all_data


def results_styling_subs(counter,items,item,manual_title):
    #items[0] = 'label', items[1] = 'label2 : sub',items[2] = 'iconImage', items[3] = 'thumbnailImage : flag',
    #items[4] = 'url : download', items[5] = 'percent', items[6] = 'hearing_imp'

    #sub_name=colorize_text(str(items[5])+ "% ","cyan")+items[1]
    sub_lang = items[0] #or second string for menu item
    sub_name = items[1]
    source_prefix = items[2]
    lang_prefix = items[3]
    sync_percent = items[5]
    hearing_imp = items[6]

    str_percent = str(sync_percent) + "%"
    str_counter = str(counter) + "."
    str_source_prefix = str(str(source_prefix))

    ##### Set 'Sync' #####
    #json_value['label2']=colorize_text(str(precent)+ "% ",'gold')+json_value['label2']
    #if sync_percent>int(all_setting["sync_percent"]) or item['file_original_path'].replace("."," ") in sub_name.replace("."," ") and len(item['file_original_path'].replace("."," "))>5:
    if sync_percent > int(all_setting["sync_percent"]):
        isSynced = 'true'
        #isSynced = 'true' if items[5]>int(all_setting["sync_percent"]) else 'false'
        #sub_name=colorize_text('GOLD [B]'+sub_name+'[/B]','gold')
        #sub_name=colorize_text(' GOLD [B]'+json_value['label2']+'[/B]','gold')
    else:
        isSynced = 'false'

    ##### Get provider color and use it ti extra wrapped data #####
    pattern = r'\[COLOR (.+?)\]'
    result = re.search(pattern, sub_name).group(1)
    #print(result)
    # color_result_percent = result
    # color_result_counter = result
    color_result = result
    color_result = result

    ##### Wrap sub with extra data #####

    if all_setting["result_style"]=='4':
        #0: rating=rating + sub=[i,%,source,sub]
        iconData = str(round(float(sync_percent / 20)))
        prefix1 = str_counter + " " + str_percent + " [" + str_source_prefix + "] "
        prefix2 = str_counter + " [" + str_source_prefix + "] "

        if is_to_check_percent(item):
            sub_name=colorize_text(prefix1,color_result)+sub_name
        else:
            sub_name=colorize_text(prefix2,color_result)+sub_name
            iconData=''
    else:
        if all_setting["result_style"]=='0':
            #4: rating=% + sub=[i,source,sub]
            #% i. n s
            iconData = str_percent
            prefix1 = str_counter + " "
            prefix2 = str_source_prefix + " | "
        elif all_setting["result_style"]=='1':
            #3: rating=source + sub=[i,%,sub]
            #n i. % s
            iconData = str_source_prefix
            prefix1 = str_counter + " "
            prefix2 = str_percent + " | "
        elif all_setting["result_style"]=='2':
            #2: rating=index + sub=[source,%,sub]
            #i. n % s
            iconData = str_counter
            prefix1 = str_source_prefix + " | "
            prefix2 = str_percent + " | "
        elif all_setting["result_style"]=='3':
            #1: rating=index + sub=[%,source,sub]
            #i. % n s
            iconData = str_counter
            prefix1 = str_percent + " | "
            prefix2 = str_source_prefix + " | "

        #Show % or rating only when percent can be calculate
        #Do not show when running manual search
        if is_to_check_percent(item) and manual_title=='' or not "%" in prefix2:
            sub_name=colorize_text(prefix2,color_result)+sub_name
        if is_to_check_percent(item) and manual_title=='' or not "%" in prefix1:
            sub_name=colorize_text(prefix1,color_result)+sub_name
        if not is_to_check_percent(item) and "%" in iconData: # or manual_title!=''
            iconData=''

    #sub_name=colorize_text(counter,color_result_counter) + ' ' + sub_name

    if iconData!='':
        iconData = colorize_text(iconData,color_result)

    try:
        listitem = xbmcgui.ListItem(label          = sub_lang,
                                    label2         = sub_name
                                    )
        listitem.setArt({'thumb' : lang_prefix, 'icon': iconData})

    except:
        listitem = xbmcgui.ListItem(label          = sub_lang,
                                    label2         = sub_name,
                                    thumbnailImage = lang_prefix,
                                    iconImage      = iconData
                                    )

    listitem.setProperty( "sync", isSynced )
    listitem.setProperty( "hearing_imp", hearing_imp )

    return listitem


def colorize_text(text, color):
    return "[COLOR %s]%s[/COLOR]" %(color, str(text))

def results_generate_menu_items():
    listitem = ListItem(label=__language__(32030),
                        label2=colorize_text('[I]'+ __language__(32029)+'[/I]','plum'))
    url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "open_setting")
    addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)

    listitem = ListItem(label=__language__(32031),
                        label2=colorize_text('[I]'+ __language__(32003)+'[/I]','khaki'))
    url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "clean")
    addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)

    if os.path.exists(pathToAddonSubskeys) or os.path.exists(pathToAddonKeymap):
        listitem = ListItem(label=__language__(32032),
                            label2=colorize_text('[I]'+ __language__(32033)+'[/I]','olive'))
        url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "keys")
        addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)

    '''
    listitem = ListItem(label=__language__(32036),
                        label2=colorize_text('[I]'+ __language__(32035)+'[/I]','seagreen'))
    url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "disable_subs")
    #url = "plugin://%s/?action=disable_subs" % (MyScriptID)
    addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)
    '''

    '''
    listitem = ListItem(label=__language__(32032),
                        label2=colorize_text('[I]'+ 'יצא קובץ היסטוריה' +'[/I]','aqua'))
    url = "plugin://%s/?action=export"% (MyScriptID)
    addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)
    '''

def change_background(all_setting):
    #sublist=os.listdir(__last__)
    sub = last_sub_path

    if all_setting["enable_font"]=='true':
        if all_setting["background"]=='false':
            all_setting["background"]='true'
        else:
            all_setting["background"]='false'

        sub = srt2ass(sub, all_setting)
    else:
        if all_setting["background"]=='false':
            all_setting["background"]='true'
            sub = srt2ass(sub, all_setting)
        else:
            all_setting["background"]='false'

    xbmc.Player().setSubtitles(sub)
    return all_setting

def clear_data():
    try:
        remove_and_generate_temp_subs_directories()
        delete_junction(cache_list_folder)
        #delete_junction(MyTmp)
        #remove_and_generate_directory(MyTmp)
        #remove_and_generate_directory(cache_list_folder)

        # try:
        #     shutil.rmtree(MyTmp)
        # except: pass
        # xbmcvfs.mkdirs(MyTmp)

        # try:
        #     shutil.rmtree(cache_list_folder)
        # except: pass
        # xbmcvfs.mkdirs(cache_list_folder)

        subtitle_cache().delete("credentials")
        subtitle_cache().delete("save")
        cache.clear(['subs'])

        notify(32004)

    except: pass

    executebuiltin((u'Notification(%s,%s)' % (__scriptname__, __language__(32004))))
    #executebuiltin((u'Notification(%s,%s)' % (__scriptname__, __language__(32004))).encode('utf-8'))

def end_sub_progress(sub,all_setting):
    if all_setting["enable_font"]=='true':
        sub = srt2ass(sub,all_setting)

    #sub = xbmc_translate_path(sub)
    listitem = ListItem(label=sub)

    addDirectoryItem(handle=int(sys.argv[1]), url=sub, listitem=listitem,isFolder=False)



if action =='search1':
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
    MyLog("Download ID: %s" %id)

    if id == 'open_setting' or id == 'clean' or id == 'keys' or id == 'disable_subs':
        if id=='open_setting':
            __settings__.openSettings()
            refresh_setting()

        elif id == 'clean':
            clear_data()

        elif id == 'keys':
            if os.path.exists(pathToAddonSubskeys):
                xbmc.executebuiltin('RunScript(%s)' %(subskeys_addon))
            elif os.path.exists(pathToAddonKeymap):
                xbmc.executebuiltin('RunScript(%s)' %(keymap_addon))
        '''
        elif action =='disable_subs':
            myLogger("DISABLE")
            xbmc.Player().showSubtitles(False)
            #xbmc.Player().setSubtitles("")
            listitem = ListItem(label="ww")
        '''

        try:
            #sublist=os.listdir(__last__)
            with open(last_sub_path, 'w') as file:
                file.write("dummy")

            sub = last_sub_path
            end_sub_progress(sub,all_setting)
        except:
            pass

    else:
        temp=' '

        subs,temp = download_manager(3,id)

        try:
            shutil.rmtree(__last__)
            xbmc.sleep(100)
        except: pass
        xbmcvfs.mkdirs(__last__)
        xbmc.sleep(100)
        if not os.path.exists(__last__):
            os.makedirs(__last__)

        last_sub_download = hashlib.sha256(str(json.dumps(params)).encode('utf-8','ignore')).hexdigest()
        subtitle_cache_next().set('last_sub', last_sub_download)

        if subs and len(subs) > 0:
            for sub in subs:
                (sub, isSuccess) = translate_subs_and_renaming(sub,'','',3,all_setting)

                check_and_save_history_logs(sub,all_setting)

                dst=last_sub_path
                xbmcvfs.copy(sub, dst)

                end_sub_progress(sub,all_setting)
                break


    #xbmc.Player().setSubtitles(sub)
    endOfDirectory(int(sys.argv[1]))

elif action =='clean':
    clear_data()

elif action =='settingsHe':
    setLanguageSettings('he', True)

elif action =='settingsEn':
    setLanguageSettings('en', True)

elif action =='settingsKodi':
    setLanguageSettings('kodi', True)

'''
elif action =='disable_subs':
    myLogger("DISABLE")
    xbmc.Player().showSubtitles(False)
    #xbmc.Player().setSubtitles("")
    listitem = ListItem(label="a")
    addDirectoryItem(handle=int(sys.argv[1]), url="ww", listitem=listitem,isFolder=False)

    endOfDirectory(int(sys.argv[1]))

elif action =='export':
    myLogger("export")
    addonInfo = MyAddon.getAddonInfo
    dataPath = xbmc_translate_path(addonInfo('profile')).decode('utf-8')
    cacheFile = os.path.join(dataPath, 'subs_history.db')
    xbmcvfs.mkdir(dataPath)
    dbcon = database.connect(cacheFile)
    dbcur = dbcon.cursor()

    browse_dialog = xbmcgui.Dialog()
    iso_file = browse_dialog.browse(type=0, heading='Export Location', shares='files', useThumbs=False, treatAsFolder=True, defaultt='c:', enableMultiple=False)

    xbmcvfs.copy(cacheFile, os.path.join(iso_file,'subs_history.db'))
    xbmcgui.Dialog().ok("יצוא" + "\n\n" + "הועתק")


    endOfDirectory(int(sys.argv[1]))
'''