# -*- coding: utf-8 -*-
import xbmcvfs,xbmcgui,xbmcaddon,xbmc
from xbmcplugin import endOfDirectory, addDirectoryItem
from xbmcgui import ListItem, Dialog
from xbmcvfs import listdir, exists
from xbmc import executebuiltin, getInfoLabel, executeJSONRPC, Player, sleep, log, getCondVisibility
import sys,logging,unicodedata,urllib,zlib,os,zipfile,contextlib,hashlib,shutil,threading
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

try:
    import HTMLParser
    html_parser = HTMLParser.HTMLParser()
    from urllib import urlretrieve
    from urllib import  unquote_plus, unquote, urlopen, quote
except:
    import html
    from urllib.request import urlretrieve
    from urllib.parse import  unquote_plus, unquote, quote, quote_plus


from unicodedata import normalize

from srt2ass import srt2ass

from wizdom_api.wizdom import GetWizJson,wizdom_download_sub
from ktuvit_api.ktuvit import GetKtuvitJson,ktuvit_download_sub
from subscene_api import SubtitleAPI
from opensubs_api.opensubtitle import GetOpenSubtitlesJson,Download_opensubtitle
from local_api.local import GetLocalJson
#from aa_subs_api.aa_subs import aa_subs, Download_aa

from myLogger import myLogger

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




#reload(sys)
#sys.setdefaultencoding('utf8')
#from yify_api.yify import search_yify
socket.setdefaulttimeout(10)
action=None
searchstring=None
myLogger('Subs On')
all_setting=[]
location=0
last_sub_download=''


running=0


global links_wizdom,links_subcenter,links_local,links_ktuvit,links_open,imdbid,links_subscene
imdbid=''
links_wizdom=[]
links_ktuvit=[]
links_open=[]
links_subscene=[]
links_subcenter=[]
links_local=[]

prefix_wizdom='Wiz'
prefix_ktuvit='Kt'
prefix_open='OpS'
prefix_subscene='SSc'
prefix_acat='AC' #AA_CAT
prefix_local='Loc'
# prefix_wizdom='[Wiz]'
# prefix_ktuvit='[Kt]'
# prefix_open='[OpS]'
# prefix_subscene='[SSc]'
# prefix_acat='[AC]' #AA_CAT
# prefix_local='[Loc]'

#base_aa='aHR0cHM6Ly9yb2NrLnNlZWRob3N0LmV1L2tjYXQxMjMvSHViLw=='

MyAddon = xbmcaddon.Addon()
MyScriptID = MyAddon.getAddonInfo('id')
__settings__ = xbmcaddon.Addon(id=MyScriptID)
MyVersion = MyAddon.getAddonInfo('version')
__profile__ = xbmc_translate_path(MyAddon.getAddonInfo('profile'))

MyTmp = xbmc_translate_path(os.path.join(__profile__, 'temp_download'))
MyZipFolder = xbmc_translate_path(path.join(MyTmp, 'zips'))
MySubFolder = xbmc_translate_path(path.join(MyTmp, 'subs'))
MyZipFolder2 = xbmc_translate_path(os.path.join(MyTmp, 'zips2'))
MySubFolder2 = xbmc_translate_path(os.path.join(MyTmp, 'subs2'))

__language__ = MyAddon.getLocalizedString
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
    if all_setting["popup"]=="true":
        if not timeout==-1:
            timeout*=1000
            xbmc.executebuiltin((u'Notification(%s,%s,%s)' % (__scriptname__, msg_id, timeout)))
        else:
            xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, msg_id)))
def notify3(msg,timeout=-1):
    if not timeout==-1:
        timeout*=1000
        xbmc.executebuiltin((u'Notification(%s,%s,%s)' % (__scriptname__, msg, timeout)))
    else:
        xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, msg)))


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
        except Exception as e:
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

    subs = []
    temp = ' '

    if source=='wizdom' or source=='ktuvit':
        subs,temp = download(id,language,thumbLang,sub_link,filename,mode_subtitle)
    elif source=='opensubtitle':
        subs = download(id,language,thumbLang,sub_link,filename,mode_subtitle)
        #subs = Download_opensubtitle(id, sub_link,filename,subformat,mode_subtitle)
    elif source=='subscene':
        #Since the "link" is not a download link and since getting the download link is long process
        #The download link will be fetch and generated only when choosing to download
        download_url = subscene.get_download_link(sub_link, language)
        if download_url != '' :
            subs,temp = download(id,language,thumbLang,download_url,'',mode_subtitle)
        #subs,temp = subscene.subscene_download_process(params,mode_subtitle)
    elif source=='local':
        subs,temp = download(id,language,thumbLang,sub_link,filename,mode_subtitle)
    # elif source=='aa_subs':
    #     myLogger('AA SUBS DOWNLOAD')
    #     subs = Download_aa(params["link"],mode_subtitle)
    else:
        subs,temp = download(id,language,thumbLang,sub_link,filename,mode_subtitle)
        # try:
        #     if len(subs[0])>0:
        #         subs=subs[0]
        # except:
        #     pass
        myLogger("download_manager - temp: %s" %(temp))

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

def remove_and_generate_temp_subs_directories(fromZip):
    delete_junction(MyTmp)

    try:
        xbmcvfs.mkdirs(MyTmp)
        if (fromZip):
            xbmcvfs.mkdirs(MyZipFolder)
            xbmcvfs.mkdirs(MySubFolder)
        else:
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

    myLogger("download() : language=%s | thumbLang=%s | sub_link=%s | filename=%s | mode_subtitle=%s | id=%s"
             %(language,thumbLang,sub_link,filename,mode_subtitle,id))

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
                remove_and_generate_temp_subs_directories(True)
                id = id.replace('wizdom$$$','')
                archive_file = path.join(MyZipFolder, 'wizdom.sub.'+id+'.zip')
                wizdom_download_sub(id,archive_file)

            elif 'ktuvit$$$' in id:
                remove_and_generate_temp_subs_directories(False)
                #ktuvit doesn't download zip, it builds the subtitle file directly from data as plain text file
                return ktuvit_download_sub(id,MySubFolder2,mode_subtitle)

            elif 'opensubs$$$' in id:
                remove_and_generate_temp_subs_directories(False)
                id = id.replace('opensubs$$$','')
                #opensubtitles doesn't download zip when usin XMLRPC, it builds the subtitle file directly from data as plain text file
                #Only when there is an error it tries to download with HTTP and then it will us zip (handled inside)
                return Download_opensubtitle(id, sub_link,filename,subformat,mode_subtitle)

            elif 'subscene$$$' in id:
                remove_and_generate_temp_subs_directories(True)
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

            '''
            elif 'yify$$$' in id:
                archive_file = path.join(MyZipFolder, 'yify.sub.'+id.replace('yify$$$','').replace('/subtitles/','')+'.zip')

                if not path.exists(archive_file):
                    urlretrieve("https://www.yifysubtitles.org/subtitle/"+id.replace('yify$$$','').replace('/subtitles/','')+".zip", archive_file)
            '''

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
                #file_ = rename_sub_filename_with_language_prefix(ufile,MySubFolder,thumbLang)
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
        import linecache
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)

        myLogger('ERROR IN Download:'+str(lineno)+',Error:'+str(e), logLevel=xbmc.LOGERROR)
        notify2('[COLOR red] Error: [/COLOR]'+str(lineno)+' E:'+str(e),all_setting)

    if mode_subtitle>1:
        return '',False
    else:
        return 'NO',False

def rename_sub_filename_with_language_prefix(old_filename, dir, lang):
    if (lang==''):
        lang = "he"
    try:
        old_full_path_filename = path.join(dir, old_filename)
        myLogger("Rename filename: " + repr(old_full_path_filename))

        parts = old_filename.split('.')
        parts.insert(-1, lang)
        new_filename = '.'.join(parts)

        new_full_path_filename = path.join(dir, new_filename)
        myLogger("To this filename: " + repr(new_full_path_filename))

        _filename = ''
        if os.path.isfile(old_full_path_filename):
            os.replace(old_full_path_filename, new_full_path_filename)
            _filename = new_full_path_filename
        else:
            _filename = old_full_path_filename

        myLogger("Filename is: " + repr(_filename))
        return _filename;
    except Exception as e:
        myLogger("Renaming Error: " + repr(e), logLevel=xbmc.LOGERROR)
        return old_full_path_filename


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

#///////////////////////////////////////Wizdom////////////////////////////////////////////////
def Wizdom_Search(imdb,season=0,episode=0,version=0):
    global links_wizdom

    subtitle_list,json_object = GetWizJson(imdb,prefix_wizdom,color_wizdom,season,episode,version)

    links_wizdom = subtitle_list

    return len(json_object),links_wizdom

#///////////////////////////////////////Ktuvit////////////////////////////////////////////////

def Ktuvit_Search(item,imdb_id):
    global links_ktuvit

    parse_rls_title(item)

    myLogger("Ktuvit_Search item:" + repr(item))

    subtitle_list,m_pre = GetKtuvitJson(item,imdb_id,prefix_ktuvit,color_ktuvit)

    links_ktuvit = subtitle_list

    return len(m_pre),links_ktuvit

#///////////////////////////////////////Opensubtitles////////////////////////////////////////////////

def Search_Opensubtitle(item,imdb_id,mode_subtitle,all_setting):
        global links_open

        myLogger("Search_Opensubtitle item:" + repr(item))

        saved_data,search_data=GetOpenSubtitlesJson(item,imdb_id,mode_subtitle,all_setting,prefix_open,color_open)

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

#///////////////////////////////////////Subcenter archive////////////////////////////////////////////////
'''
def aa_subs_Search(item,mode_subtitle):
    global links_subcenter

    myLogger("ACat_Search item:" + repr(item))

    subtitle_list,result = aa_subs(item,mode_subtitle,prefix_acat,color_acat)

    links_subcenter = subtitle_list

    return len(result),links_subcenter
'''


def clean_title(item):
    myLogger("search_all: clean_title - title before: " + repr(item["title"]))

    try:
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

    except Exception as e:
        myLogger("clean_title Error: " + repr(e))


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
    global language,thumbLang,sub_link,filename,subformat,source

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

        params=getParams('?'+url.split('?')[1])

        id = getParam("id", params)
        try:
            language=params["language"]
        except:
            language=''
        try:
            thumbLang=params["thumbLang"]
        except:
            thumbLang=''
        try:
            sub_link=params["link"]
        except:
            sub_link=''
        try:
            filename=params["filename"]
        except:
            filename=''
        try:
            subformat=params["subformat"]
        except:
            subformat=''
        try:
            source=params["source"]
        except:
            source=''

        if x==value_for_subs :
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
                notify2('Setting sub [COLOR skyblue]'+str(total_count) +'/'+str(max_sub-1)+'[/COLOR]: ' +lab2,all_setting)

                xbmc.Player().setSubtitles(sub)
                break_now=1
                break
            else:
                notify2('[COLOR red]Cannot download [/COLOR][COLOR skyblue]'+str(total_count) +'/'+str(max_sub-1)+'[/COLOR]: ' +lab2,all_setting)

        x=x+1
        total_count=total_count+1
    return location

color_wizdom=''
color_ktuvit='limegreen'
color_open='yellow'
color_subscene='lightskyblue'
color_local='thistle'
color_result_percent='cyan'
color_result_counter='white'
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
    # cCustomAcat = all_setting["color_result_aa_subs_custom"]

    cWizdom = all_setting["color_result_wizdom"]
    cKtuvit = all_setting["color_result_ktuvit"]
    cOpen = all_setting["color_result_opensubs"]
    cSubscene = all_setting["color_result_subscene"]
    clocal = all_setting["color_result_local"]
    # cAcat = all_setting["color_result_aa_subs"]

    color_wizdom = cCustomWizdom if cWizdom == custom else cWizdom
    color_ktuvit = cCustomKtuvit if cKtuvit == custom else cKtuvit
    color_open = cCustomOpen if cOpen == custom else cOpen
    color_subscene = cCustomSubscene if cSubscene == custom else cSubscene
    color_local = cCustomlocal if clocal == custom else clocal
    # color_acat = cCustomAcat if cAcat == custom else cAcat

    '''
    cCustomPercent = all_setting["color_result_percent_custom"]
    cCustomCounter = all_setting["color_result_counter_custom"]
    cPercent = all_setting["color_result_percent"]
    cCounter = all_setting["color_result_counter"]
    color_result_percent = cCustomPercent if cPercent == custom else cPercent
    color_result_counter = cCustomCounter if cCounter == custom else cCounter
    '''

    myLogger("Colors: color_wizdom=%s | color_ktuvit=%s | color_open=%s | color_subscene=%s | color_local=%s" %(color_wizdom,color_ktuvit,color_open,color_subscene,color_local))

settings_list = {"Email":MyAddon.getSetting("Email"),
                 "Password":MyAddon.getSetting("Password"),
                 "action":MyAddon.getSetting("action"),
                 "OSuser":MyAddon.getSetting("OSuser"),
                 "OSpass":MyAddon.getSetting("OSpass"),
                 "wizset":MyAddon.getSetting("wizset"),
                 "subscene":MyAddon.getSetting("subscene"),
                 "opensubtitle":MyAddon.getSetting("opensubtitle"),
                 "English":MyAddon.getSetting("English"),
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
                 "Debug":MyAddon.getSetting("Debug"),
                 "color_result_wizdom":MyAddon.getSetting("color_result_wizdom"),
                 "color_result_wizdom_custom":MyAddon.getSetting("color_result_wizdom_custom"),
                 "color_result_ktuvit":MyAddon.getSetting("color_result_ktuvit"),
                 "color_result_ktuvit_custom":MyAddon.getSetting("color_result_ktuvit_custom"),
                 "color_result_opensubs":MyAddon.getSetting("color_result_opensubs"),
                 "color_result_opensubs_custom":MyAddon.getSetting("color_result_opensubs_custom"),
                 "color_result_subscene":MyAddon.getSetting("color_result_subscene"),
                 "color_result_subscene_custom":MyAddon.getSetting("color_result_subscene_custom"),
                 "color_result_aa_subs":MyAddon.getSetting("color_result_aa_subs"),
                 "color_result_aa_subs_custom":MyAddon.getSetting("color_result_aa_subs_custom"),
                 "color_result_local":MyAddon.getSetting("color_result_local"),
                 "color_result_local_custom":MyAddon.getSetting("color_result_local_custom"),
                 "result_style":MyAddon.getSetting("result_style")
                 }

def refresh_setting():
    global all_setting,settings_list

    all_setting={}
    all_setting=settings_list
    all_setting["aa_subs"]='false'
    all_setting["yify"]='false'
    '''
    "aa_subs":MyAddon.getSetting("aa_subs"),
    "yify":MyAddon.getSetting("yify"),
    "color_result_percent":MyAddon.getSetting("color_result_percent"),
    "color_result_percent_custom":MyAddon.getSetting("color_result_percent_custom"),
    "color_result_counter":MyAddon.getSetting("color_result_counter"),
    "color_result_counter_custom":MyAddon.getSetting("color_result_counter_custom")
    '''

    set_providers_colors()

    temp=json.dumps(all_setting)
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
try:
    language=params["language"]
except:
    language=''
try:
    thumbLang=params["thumbLang"]
except:
    thumbLang=''
try:
    sub_link=params["link"]
except:
    sub_link=''
try:
    filename=params["filename"]
except:
    filename=''
try:
    subformat=params["subformat"]
except:
    subformat=''
try:
    source=params["source"]
except:
    source=''
all_setting=refresh_setting()

#subscene init
#subscene = SubtitleAPI('English','Hebrew') # pass languages you want to have in results
#subscene = SubtitleAPI('Hebrew') # pass languages you want to have in results
selected_langs=[]
selected_langs.append('Hebrew')
if all_setting["English"]== 'true':
   selected_langs.append('English')
if all_setting["arab"]== 'true':
   selected_langs.append('Arabic')
if all_setting["spanish"]== 'true':
   selected_langs.append('Spanish')
if all_setting["all_lang"]== 'true':
   selected_langs=[]
if len(all_setting["other_lang"])>0:
   all_lang=all_setting["other_lang"].split(",")
   for items in all_lang:
     selected_langs.append(str(items))
myLogger('Langs: ' + repr(selected_langs))
subscene = SubtitleAPI(*selected_langs) # pass languages you want to have in results


def similar(w1, w2):
    from difflib import SequenceMatcher

    s = SequenceMatcher(None, w1, w2)
    return int(round(s.ratio()*100))

def download_subs(link):
    global id,language,thumbLang,sub_link,filename,subformat,source
    params = getParams(link)
    id = getParam("id", params)
    try:
        language=params["language"]
    except:
        language=''
    try:
        thumbLang=params["thumbLang"]
    except:
        thumbLang=''
    try:
        sub_link=params["link"]
    except:
        sub_link=''
    try:
        filename=params["filename"]
    except:
        filename=''
    try:
        subformat=params["subformat"]
    except:
        subformat=''
    try:
        source=params["source"]
    except:
        source=''
    myLogger('source=='+source)

    subs,temp = download_manager(3,id)

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


def searchTMDB(type, query, year):
    import requests

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
        return '0000'


    url = "http://api.tmdb.org/3/%s/%s/external_ids?api_key=%s&language=en" % (type,tmdb_id, tmdbKey)
    json = requests.get(url, timeout=60).json()

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
        except Exception as e:
            myLogger( "[%s]" % (e,))
            return 0

        filename = 'subs.search.tmdb.fulldata.%s.%s.json'%(type_search,tmdb_id)
        url = "https://api.tmdb.org/3/%s/%s?api_key=%s&language=en&append_to_response=external_ids"%(type_search,tmdb_id,tmdbKey)
        myLogger("searchTMDB fulldata id: %s" % url)
        json = caching_json(filename,url)

        try:    imdb_id = json['external_ids']["imdb_id"]
        except Exception as e:
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
        except Exception as e:
            myLogger( "[%s]" % (e,))
            return 0

        filename = 'subs.search.tmdb.fulldata.%s.%s.json'%(type_search,tmdb_id)
        url = "https://api.tmdb.org/3/%s/%s?api_key=%s&language=en&append_to_response=external_ids"%(type_search,tmdb_id,tmdbKey)
        myLogger("searchTMDB fulldata id: %s" % url)
        json = caching_json(filename,url)

        try:    imdb_id = json['external_ids']["imdb_id"]
        except Exception as e:
            myLogger( "[%s]" % (e,))
            return 0

        return imdb_id

def is_local_file_tvshow(item):
    return item["title"] and (int(item["year"])==0 or "smb:" in item['full_path'])

def get_subtitles(item,mode_subtitle,imdb_id,all_setting):
    myLogger('getting subs')
    global links_wizdom,links_ktuvit,links_open,links_subscene,links_subcenter,links_local
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
                dp.update(0, 'אנא המתן'+'\n'+ 'imdb_id כשל '+'\n'+  str(e) )
            else:
                dp.update(0, 'אנא המתן','imdb_id כשל ',  str(e) )
        else:
           notify2(' imdb_id כשל  '+e,all_setting)
        pass

    #if 'tt' not in str(imdb_id)
    if not imdb_id[:2]=="tt":
        imdb_id = 0
        myLogger('get_subtitles: imdb_id has not been founded - ' + imdb_id)
    else:
        if mode_subtitle==3:
            if KODI_VERSION>18:
                dp.update(0, 'אנא המתן'+'\n'+ 'נמצא '+'\n'+  imdb_id )
            else:
                dp.update(0, 'אנא המתן', 'נמצא ',  imdb_id )
        else:
            notify2(' נמצא'+imdb_id,all_setting)


    save_all_data=[]
    threads=[]
    myLogger('get_subtitles: using imdb_id ' +imdb_id+ ' for subtitles searching ')

    if all_setting["wizset"]== 'true':
        threads.append(Thread(Wizdom_Search,imdb_id,item["season"],item["episode"],item['file_original_path']))
        #num_of_subs,subtitle,subtitle_list=Wizdom_Search(imdb_id,mode_subtitle,0,0,item['file_original_path'])
    if all_setting["ktuvitset"]== 'true':# Ktuvit Search
        threads.append(Thread(Ktuvit_Search,item,imdb_id))
        #num_of_subs,subtitle,saved_data=Ktuvit_Search(item,mode_subtitle,imdb_id)
    if all_setting["opensubtitle"]== 'true':# Opensubtitle Search
        threads.append(Thread(Search_Opensubtitle,item,imdb_id,mode_subtitle,all_setting))
    if all_setting["subscene"]== 'true':
        threads.append(Thread(Subscene_Search,item,imdb_id))
        #threads.append(Thread(Subscene_Search,item,mode_subtitle))
        #num_of_subs,subtitle,saved_data=search_subscene(item,mode_subtitle)
    '''
    if all_setting["aa_subs"]== 'true':# Subcenter Search
        threads.append(Thread(aa_subs_Search,item,mode_subtitle))
        #num_of_subs,subtitle,saved_data=subcenter_search(item,mode_subtitle)

    #if all_setting["yify"]== 'true':# YIFY Search
        #num_of_subs,subtitle,saved_data=search_yify(item,imdb_id,mode_subtitle)
    '''

    if all_setting["storage_en"]=='true' and len(all_setting["storage"])>0:# Local
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
            string_dp=string_dp+(prefix_subscene.upper()+':[COLOR %s]%s[/COLOR] '%(tt[zz],len( links_subscene)))
            zz=zz+1
        if all_setting["storage_en"]=='true' and len(all_setting["storage"])>0:
            string_dp=string_dp+(prefix_local.upper()+':[COLOR %s]%s[/COLOR] '%(tt[zz],len( links_local)))
            zz=zz+1
        #   if all_setting["aa_subs"]== 'true':
        #     string_dp=string_dp+(prefix_acat.upper()+':[COLOR %s]%s[/COLOR] '%(tt[zz],len( links_subcenter)))
        #     zz=zz+1

        if mode_subtitle==3:
            if KODI_VERSION>18:
                dp.update(int(((num_live* 100.0)/(len(threads))) ), ' אנא המתן '+ time.strftime("%H:%M:%S", time.gmtime(elapsed_time))+'\n'+ string_dp+'\n'+  string_dp)
            else:
                dp.update(int(((num_live* 100.0)/(len(threads))) ), ' אנא המתן '+ time.strftime("%H:%M:%S", time.gmtime(elapsed_time)),string_dp,  string_dp)
        #old end for

        if still_alive==0:
            break

        if mode_subtitle==3:
            if dp.iscanceled() or elapsed_time>45:
                for td in threads:
                    if td.is_alive():
                        stop_all=1
                        td._stop()
        xbmc.sleep(200)

    if mode_subtitle==3:
        dp.close()
    else:
        notify2(str(string_dp),all_setting)


    save_all_data.append(links_wizdom)
    save_all_data.append(links_ktuvit)
    save_all_data.append(links_open)
    save_all_data.append(links_subscene)
    save_all_data.append(links_local)
    # save_all_data.append(links_subcenter)

    if mode_subtitle==3:
        dp.close()
    dont_save=0

    if len(links_wizdom)==0 and len(links_ktuvit)==0 and len(links_open)==0 and len(links_subscene)==0 and len (links_local)==0: #and len(links_subcenter)==0
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

def calc_sub_percent_sync(json_value,array_original):
    release_names=['bluray','blu-ray','bdrip','brrip','brip',
                   'hdtv','hdtvrip','pdtv','tvrip','hdrip','hd-rip','hc',
                   'web','web-dl','web dl','web-dlrip','webrip','web-rip',
                   'dvdr','dvd-r','dvd-rip','dvdrip','cam','hdcam','cam-rip','screener','dvdscr','dvd-full',
                   'tc','telecine','ts','hdts','telesync']

    Quality=(xbmc.getInfoLabel("VideoPlayer.VideoResolution"))+'p'

    array_subs=json_value['label2'].replace(prefix_wizdom,'').replace(prefix_ktuvit,'').replace(prefix_open,'').replace(prefix_subscene,'').replace(prefix_acat,'').replace(prefix_local,'').replace("[SCe]",'').replace("[SC]",'').replace("[SZ]",'').replace("[sz]",'').replace("[COLOR "+color_wizdom+"]",'').replace("[COLOR "+color_ktuvit+"]",'').replace("[COLOR "+color_open+"]",'').replace("[COLOR "+color_subscene+"]",'').replace("[COLOR "+color_local+"]",'').replace("[COLOR skyblue]",'').replace("[COLOR lightcoral]",'').replace("[COLOR gray]",'').replace("[COLOR burlywood]",'').replace(".srt",'').replace("[/COLOR]",'').strip().replace("_",".").replace(" ",".").replace("+",".").replace("/",".").split(".")
    #array_subs.pop(0)
    array_subs=[element.strip().lower() for element in array_subs if element != '']
    array_subs=[element for element in array_subs if element not in ('-','no', 'hi')]
    #array_subs=[str(x).lower() for x in array_subs if x != '']

    array_original=[element.strip().lower() for element in array_original if element != '']
    #array_original=[element.strip().lower() for element in array_original]
    #array_original=[str(x).lower() for x in array_original if x != '']

    if Quality not in array_original and Quality in array_subs:
        array_original.append(Quality)

    #If we want to give more weight to the ratio score to the "release type" when comparing.
    for item_2 in release_names:
        if item_2 in array_original and item_2 in array_subs:
            array_original.append(item_2)
            # array_original.append(item_2)
            # array_original.append(item_2)
            array_subs.append(item_2)
            # array_subs.append(item_2)
            # array_subs.append(item_2)

    precent=similar(array_original,array_subs)
    return precent

def autosubs_download_first_sub(all_data,mode_subtitle,all_setting,save_all_data):
    counter=0
    for items in all_data:
        counter+=1
        label=items[0]
        label2=items[1]
        source_prefix=items[2]
        lang_prefix=items[3]
        best_sub=items[4]
        highest_rating=items[5]
        hearing_imp=items[6]
        # notify2('[COLOR yellow]'+str(highest_rating)+'%[/COLOR]' + ' - ' +label2+','+label ,all_setting)
        notify2('%s | %s | %s | %s' %('[COLOR yellow]'+str(highest_rating)+'%[/COLOR]',source_prefix,label2,label) ,all_setting,3)

        if len(best_sub)>0:
            subs=download_subs(best_sub)

            try:
                shutil.rmtree(__last__)
                xbmc.sleep(100)
            except: pass

            xbmcvfs.mkdirs(__last__)
            xbmc.sleep(100)
            if not os.path.exists(__last__):
                os.makedirs(__last__)

            #if ('language=English' in best_sub or  'language=Arabic' in best_sub or 'language=Spanish' in best_sub) and all_setting["auto_translate"]=='true':

            subs = check_and_translate_subs(subs,best_sub,label,mode_subtitle,'',all_setting)

            dst=last_sub_path
            xbmcvfs.copy(subs, dst)

            if all_setting["enable_font"]=='true':
                subs = srt2ass(subs,all_setting)

            json_value2=json.loads(json.dumps(save_all_data))

            params=getParams('?'+best_sub.split('?')[1])

            last_sub_download=hashlib.sha256(str(json.dumps(params)).encode('utf-8','ignore')).hexdigest()

            subtitle_cache_next().set('last_sub', last_sub_download)
            notify3('[COLOR aqua]כתובית מוכנה[/COLOR]',2)

            myLogger("AutoSub sub ready: " + repr(subs))

            # listitem = xbmcgui.ListItem(label          = label,
            #                             label2         = label2
            #                             )
            # listitem.setArt({'thumb' : lang_prefix, 'icon': source_prefix})
            # xbmc.Player().updateInfoTag(listitem)

            xbmc.Player().setSubtitles(subs)
            if all_setting["pause"]=='1':
                xbmc.Player().pause()
            break

def check_and_translate_subs(subs_to_translate_path,best_sub_url,label,mode_subtitle,language,all_setting):
    subs = subs_to_translate_path

    if mode_subtitle == 2:
        if all_setting["auto_translate"]=='true' and (best_sub_url!='' and label!=''
                                                      and not any(s in best_sub_url for s in ['language=Hebrew','language=hebrew',
                                                                                      'language=He','language=he'])
                                                      and not any(s in label for s in ['Hebrew','hebrew','He','he'])
                                                     ):
            notify2('[COLOR red]מתרגם... המתן קטנה :-)[/COLOR]',all_setting)
            subs = start_tranlate_sub(subs_to_translate_path,mode_subtitle)

    elif mode_subtitle == 3:
        #if (language=='English' or language=='Arabic' or language=='Spanish')  and all_setting["auto_translate"]=='true':
        if all_setting["auto_translate"]=='true' and (language!=''
                                                      and not any(s in language for s in ['Hebrew','hebrew','He','he'])):
                                #  and (source=='opensubtitle' or source=='subscene')):
            subs = start_tranlate_sub(subs_to_translate_path,mode_subtitle)

    return subs;

def check_and_save_history_logs(sub,all_setting):
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

def start_tranlate_sub(subs_to_translate,mode_subtitle):
    try:
        translated_sub_path = os.path.join(__last__, "trans.srt")
        translate_subs(subs_to_translate,translated_sub_path,mode_subtitle)
    except Exception as e:
        myLogger('e'+str(mode_subtitle))
        myLogger(e, logLevel=xbmc.LOGERROR)
        pass

    return translated_sub_path

def search_all(mode_subtitle,all_setting,manual_search=False,manual_title=''):
    global links_wizdom,links_subcenter,links_local,links_ktuvit,links_open,imdbid
    running=1

    myLogger("search_all: mode_subtitle - " + repr(mode_subtitle))

    if mode_subtitle==3:
        dp = xbmcgui.DialogProgress()
        if KODI_VERSION>18:
            dp.create('מקבל מידע...','Getting item info...'+'\n'+''+'\n'+'')
        else:
            dp.create('מקבל מידע...','Getting item info...','','')
    else:
        notify2('Getting item info',all_setting)

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
        item,d_value_s,d_value_e = get_manual_search_item_data(item,manual_title)
        if d_value_s == 0 or d_value_e == 0:
            return 0

    else:
        if Player().isPlaying():
            item,imdb_id = get_player_item_data(item)
        else:    # Take item params from window when kodi is not playing
            item,imdb_id = get_non_player_item_data(item)

    if item['title'] == "":
        item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title")).replace("%20"," ")  # no original title, get just Title

    #item['full_path']=getInfoLabel("Player.Filenameandpath")

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
            dp.update(0, 'מנקה תיקיות'+'\n'+ item['title'] )
        else:
            dp.update(0, 'מנקה תיקיות', item['title'] )
    else:
        notify2('מנקה תיקיות',all_setting)

    #num_of_subs=0

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
            dp.update(0, 'מתחיל לחפש כתוביות'+'\n'+ imdb_id )
        else:
            dp.update(0, 'מתחיל לחפש כתוביות', imdb_id )
    else:
        notify2('מתחיל לחפש כתוביות',all_setting)


    dd=[]
    dd.append((item,mode_subtitle,imdb_id,all_setting))
    myLogger('dd::: %s' %(dd))

    try:
        #save_all_data,imdb_id,dont_save=get_subtitles(item,mode_subtitle,imdb_id,all_setting)
        save_all_data,imdb_id,dont_save=cache.get(get_subtitles,24,item,mode_subtitle,imdb_id,all_setting, table='subs')
    except:
        myLogger('Error')
        save_all_data = []
        imdb_id = 't00'
        dont_save = 0


    if dont_save==1:
        cache.clear(['subs'])

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

    #2 = from autosubs
    #3 = from Subs dialog search (auto/manual)
    if mode_subtitle==3 or mode_subtitle==2:
        all_data = results_subs_processing(save_all_data,item,last_sub)

        if mode_subtitle==2:
            if len(all_data)==0:
                notify3('[COLOR aqua]לא נמצאו כתוביות[/COLOR]',2)
            else:
                autosubs_download_first_sub(all_data,mode_subtitle,all_setting,save_all_data)
        else:
            counter=0
            ############## Styling subs results and build the result list ###############
            for items in all_data:
                counter+=1
                listitem = results_styling_subs(counter,items,item,manual_title)
                addDirectoryItem(handle=int(sys.argv[1]), url=str(items[4]), listitem=listitem, isFolder=False)

    if mode_subtitle==3:
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
    item['full_path']=''
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
            #isItMovie=True
            #isItEpisode=False
            d_value_y = dialog.input('הכנס שנה', type=xbmcgui.INPUT_NUMERIC)
            item['year'] = str(d_value_y)
            d_value_s = -1
            d_value_e = -1
        else:
            item['tvshow']=manual_title
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

    return item,d_value_s,d_value_e

def get_player_item_data(item):
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

    if item['episode']==0:
        item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")).replace("%20"," ")  # no original title, get just Title
    else:
        #item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")).replace("%20"," ")  # Show
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
    item['full_path']=getInfoLabel("Player.Filenameandpath")
    item['file_name']=''

    if not item['tvshow'] and not (item['title'] and item['year']) :
        now_play_data = get_now_played()
        item['title'],item['year'],item['season'],item['episode']=get_more_data(now_play_data, item['title'])

    return item, imdb_id

def get_non_player_item_data(item):
    imdb_id = getInfoLabel("ListItem.IMDBNumber")
    item['year'] = getInfoLabel("ListItem.Year")
    item['season'] = getInfoLabel("ListItem.Season")
    item['episode'] = getInfoLabel("ListItem.Episode")
    item['file_original_path'] = unquote(getInfoLabel("ListItem.FileNameAndPath"))
    item['file_original_path'] = item['file_original_path'].split("?")
    item['file_original_path'] = path.basename(item['file_original_path'][0])[:-4]
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

    return item,imdb_id

def is_to_check_percent(item):
    #Check % only when player is playing
    # or not playing and library based on local file:
    # Without 'strm' which is video addon file or 'plugin://' which is video addon menu
    return Player().isPlaying() or not Player().isPlaying() and not any(s in item['full_path'] for s in ['strm','plugin://'])

def results_subs_processing(save_all_data,item,last_sub):
    ########## Calc Percent and Langauge Sort ##########
    all_data=[]
    all_eng=[]
    all_arb=[]
    all_spn=[]

    ############## Subs Proccessing ###############
    for save_data_value in save_all_data:
        json_value2=json.loads(json.dumps(save_data_value))

        for json_value in json_value2:
            if 'label' in json_value and 'label2' in json_value and 'iconImage' in json_value and 'thumbnailImage' in json_value and 'sync' in json_value and 'hearing_imp' in json_value:
                ############## Calc Sync Percentage ###############
                if is_to_check_percent(item):
                    array_original=item['file_original_path'].strip().replace("_",".").replace(" ",".").replace("+",".").replace("/",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")
                    percent = calc_sub_percent_sync(json_value, array_original)
                    #if precent==0:

                    array_original=xbmc.getInfoLabel("VideoPlayer.title").strip().replace("_",".").replace(" ",".").replace("+",".").replace("/",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")
                    percent2 = calc_sub_percent_sync(json_value, array_original)

                    if percent2>percent:
                        percent=percent2
                else:
                    percent=0

                ############## Build subs data ###############
                ############## Language Filtering & attach percent value foe each ###############
                #Sort by lanugage, Hebrew first then all the rest

                #if 'language=English' in json_value['url'] or 'language=Arabic' in json_value['url'] or 'language=Spanish' in json_value['url']:
                # if 'language=Hebrew' not in json_value['url'] and 'language=he' not in json_value['url'] and ('language=' in  json_value['url'] or 'Hebrew' not in json_value['label'] or 'he' not in json_value['label']):
                #     all_eng.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent))
                # else:
                #     all_data.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent))
                if ('language=Hebrew' in json_value['url'] or 'language=he' in json_value['url']
                    or 'Hebrew' in json_value['label'] or 'hebrew' in json_value['label']
                    or 'He' in json_value['label'] or 'he' in json_value['label']):
                    all_data.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                elif ('language=English' in json_value['url'] or 'language=en' in json_value['url']
                      or 'English' in json_value['label'] or 'english' in json_value['label']
                      or 'En' in json_value['label'] or 'en' in json_value['label']):
                    all_eng.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                elif ('language=Arabic' in json_value['url'] or 'language=arabic' in json_value['url']
                      or 'Arabic' in json_value['label'] or 'arabic' in json_value['label']):
                    all_arb.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                elif ('language=Spanish' in json_value['url'] or 'language=spanish' in json_value['url']
                      or 'Spanish' in json_value['label'] or 'spanish' in json_value['label']):
                    all_spn.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))
                #else:
                #    all_eng.append((json_value['label'],json_value['label2'],json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],percent,json_value['hearing_imp']))

    ############## Sort by Percentage ###############
    if all_setting["sort_subs"]=='true':
        all_data=sorted(all_data, key=lambda x: x[5], reverse=True)
        all_eng=sorted(all_eng, key=lambda x: x[5], reverse=True)
        all_arb=sorted(all_arb, key=lambda x: x[5], reverse=True)
        all_spn=sorted(all_spn, key=lambda x: x[5], reverse=True)

    all_data=all_data+all_eng+all_arb+all_spn

    f = open(last_sub+'_sort', 'w')

    f.write(json.dumps(all_data))
    f.close()

    return all_data


def results_styling_subs(counter,items,item,manual_title):
    #items[0] = 'label', items[1] = 'label2 : sub',items[2] = 'iconImage', items[3] = 'thumbnailImage : flag',
    #items[4] = 'url : download', items[5] = 'percent', items[6] = 'hearing_imp'

    #sub_name='[COLOR cyan]'+str(items[5])+ "% "+'[/COLOR]'+items[1]
    language=items[0] #or second string for menu item
    sub_name=items[1]
    source_prefix=items[2]
    lang_prefix=items[3]
    sync_percent=items[5]
    hearing_imp=items[6]

    str_percent = str(sync_percent) + "%"
    str_counter = str(counter) + "."
    str_source_prefix = str(str(source_prefix))

    ##### Set 'Sync' #####
    #json_value['label2']='[COLOR gold]'+str(precent)+ "% "+'[/COLOR]'+json_value['label2']
    #if sync_percent>int(all_setting["sync_percent"]) or item['file_original_path'].replace("."," ") in sub_name.replace("."," ") and len(item['file_original_path'].replace("."," "))>5:
    if sync_percent>int(all_setting["sync_percent"]):
        isSynced = 'true'
        #isSynced = 'true' if items[5]>int(all_setting["sync_percent"]) else 'false'
        #sub_name='[COLOR gold]GOLD [B]'+sub_name+'[/B][/COLOR]'
        ##json_value['label2']='[COLOR gold] GOLD [B]'+json_value['label2']+'[/B][/COLOR]'
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

        if Player().isPlaying():
            sub_name=wrap_text_with_color(prefix1,color_result)+sub_name
        else:
            sub_name=wrap_text_with_color(prefix2,color_result)+sub_name
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
            sub_name=wrap_text_with_color(prefix2,color_result)+sub_name
        if is_to_check_percent(item) and manual_title=='' or not "%" in prefix1:
            sub_name=wrap_text_with_color(prefix1,color_result)+sub_name
        if not is_to_check_percent(item) and "%" in iconData or manual_title!='':
            iconData=''

    #sub_name="[COLOR %s]%s.[/COLOR] %s" %(color_result_counter, counter, sub_name)

    if iconData!='':
        iconData = wrap_text_with_color(iconData,color_result)

    try:
        listitem = xbmcgui.ListItem(label          = language,
                                    label2         = sub_name
                                    )
        listitem.setArt({'thumb' : lang_prefix, 'icon': iconData})

    except:
        listitem = xbmcgui.ListItem(label          = language,
                                    label2         = sub_name,
                                    thumbnailImage = lang_prefix,
                                    iconImage      = iconData
                                    )

    listitem.setProperty( "sync", isSynced )
    listitem.setProperty( "hearing_imp", hearing_imp )

    return listitem


def wrap_text_with_color(text,color):
    return '[COLOR '+color+']'+str(text)+'[/COLOR]'

def results_generate_menu_items():
    listitem = ListItem(label=__language__(32030),
                        label2='[COLOR plum][I]'+ __language__(32029)+'[/I][/COLOR]')
    url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "open_setting")
    addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)

    listitem = ListItem(label=__language__(32031),
                        label2='[COLOR khaki][I]'+ __language__(32003)+'[/I][/COLOR]')
    url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "clean")
    addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)

    if os.path.exists(pathToAddonSubskeys) or os.path.exists(pathToAddonKeymap):
        listitem = ListItem(label=__language__(32032),
                            label2='[COLOR olive][I]'+ __language__(32033)+'[/I][/COLOR]')
        url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "keys")
        addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)

    '''
    listitem = ListItem(label=__language__(32036),
                        label2='[COLOR seagreen][I]'+ __language__(32035)+'[/I][/COLOR]')
    url = "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, "1", "disable_subs")
    #url = "plugin://%s/?action=disable_subs" % (MyScriptID)
    addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)
    '''

    '''
    listitem = ListItem(label=__language__(32032),label2='[COLOR aqua][I]'+ 'יצא קובץ היסטוריה'+'[/I][/COLOR]')
    url = "plugin://%s/?action=export"% (MyScriptID)
    addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=True)
    '''

def change_background(all_setting):
        #sublist=os.listdir(__last__)
        sub=last_sub_path

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

def clear_data():
    try:
        delete_junction(MyTmp)
        delete_junction(cache_list_folder)
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

if action=='search1':
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

    if id=='open_setting' or id=='clean' or id=='keys' or id=='disable_subs':
        if id=='open_setting':
            __settings__.openSettings()
            refresh_setting()

        elif id=='clean':
            clear_data()

        elif id=='keys':
            if os.path.exists(pathToAddonSubskeys):
                xbmc.executebuiltin('RunScript(%s)' %(subskeys_addon))
            elif os.path.exists(pathToAddonKeymap):
                xbmc.executebuiltin('RunScript(%s)' %(keymap_addon))
        '''
        elif action=='disable_subs':
            myLogger("DISABLE")
            xbmc.Player().showSubtitles(False)
            #xbmc.Player().setSubtitles("")
            listitem = ListItem(label="ww")
        '''

        try:
            #sublist=os.listdir(__last__)
            sub=last_sub_path
            end_sub_progress(sub,all_setting)
        except:
            pass

    else:
        temp=' '
        MyLog("Download ID:%s"%id)

        subs,temp = download_manager(3,id)

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
            sub = check_and_translate_subs(sub,'','',3,language,all_setting)

            check_and_save_history_logs(sub,all_setting)

            dst=last_sub_path
            xbmcvfs.copy(sub, dst)

            end_sub_progress(sub,all_setting)

    endOfDirectory(int(sys.argv[1]))

elif action=='clean':
    clear_data()

'''
elif action=='disable_subs':
    myLogger("DISABLE")
    xbmc.Player().showSubtitles(False)
    #xbmc.Player().setSubtitles("")
    listitem = ListItem(label="a")
    addDirectoryItem(handle=int(sys.argv[1]), url="ww", listitem=listitem,isFolder=False)

    endOfDirectory(int(sys.argv[1]))
'''
'''
elif action=='clear_aa':
     cache.clear(['subs_aa','subs'])
     executebuiltin((u'Notification(%s,%s)' % (__scriptname__, __language__(32004))))

elif action=='export':
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
    xbmcgui.Dialog().ok("יצוא",'הועתק')


    endOfDirectory(int(sys.argv[1]))
'''