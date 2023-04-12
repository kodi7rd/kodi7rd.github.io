# -*- coding: utf-8 -*-

import os
import sys
import xbmc,socket
import struct
import urllib
import xbmcvfs
try:
    import xmlrpclib
except:
    import xmlrpc.client as xmlrpclib
import xbmcaddon
import unicodedata,logging
from xbmcaddon import Addon

from myLogger import myLogger

__addon__      = xbmcaddon.Addon()
__version__    = __addon__.getAddonInfo('version') # Module version
__scriptname__ = "XBMC Subtitles Unofficial"

BASE_URL_XMLRPC = u"https://api.opensubtitles.org/xml-rpc"
MyAddon = Addon()
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])

class OSDBServer:
    def __init__( self, *args, **kwargs ):
        self.server = xmlrpclib.Server( BASE_URL_XMLRPC, verbose=0 )
        socket.setdefaulttimeout(10)
        login = self.server.LogIn(__addon__.getSetting( "OSuser2" ), __addon__.getSetting( "OSpass2" ), "en", "%s_v%s" %(__scriptname__.replace(" ","_"),__version__))
        myLogger('OpenSubtitles')
        myLogger('OpenSubtitles Login: ' + repr(login))
        self.osdb_token  = login[ "token" ]

    def searchsubtitles( self, item, imdb_id, all_setting ):
        tvshow=item['tvshow']
        season=item['season']
        episode=item['episode']
        year=item['year']
        title=item['title']

        if ( self.osdb_token ) :
            searchlist  = []
            lang=[]
            lang.append('heb')

            if all_setting["English"]== 'true':
               lang.append('eng')
            if all_setting["arab"]== 'true':
               lang.append('ara')
            if all_setting["spanish"]== 'true':
               lang.append('spa')
            if all_setting["all_lang"]== 'true':
               lang.append('ALL')
            if len(all_setting["other_lang"])>0:
               all_lang=all_setting["other_lang"].split(",")
               for items in all_lang:
                 lang.append(str(items))
            myLogger('Lang: ' + repr(lang))
            if len(tvshow) > 0:
               a=1
               OS_search_string = ("%s S%.2dE%.2d" % (tvshow,int(season),int(episode),)).replace(" ","+")

            else:
                if str(year) == "" and xbmc.Player().isPlaying():
                    title, year = xbmc.getCleanMovieTitle( title )
                if not imdb_id:
                    OS_search_string = title.replace(" ","+")
                else:
                    OS_search_string = imdb_id


            #if not False:

            #if xbmc.Player().isPlaying():
            #    imdb_id = str(xbmc.Player().getVideoInfoTag().getIMDBNumber().replace('tt',''))
            #else:
            #    imdb_id = str(xbmc.getInfoLabel("ListItem.IMDBNumber").replace('tt',''))

            if 'tt' in imdb_id:
                imdb_id=imdb_id.replace('tt','')
            if imdb_id=='':
               imdb_id=str((str(imdb_id)).replace('tt',''))

            if (len(tvshow)==0 and imdb_id != ""):
                searchlist.append({'sublanguageid' :",".join(lang),
                                 'imdbid'        :imdb_id
                                })
            if len(tvshow)>0:
                searchlist.append({'season' :season,
                                 'sublanguageid' :",".join(lang),
                                 'imdbid'        :imdb_id,
                                 'query'        :OS_search_string,
                                 'episode':episode
                                })
            else:
                searchlist.append({'sublanguageid':",".join(lang),
                              'query'        :OS_search_string,
                              'year'         :year
                             })

            #else:
            #  searchlist = [{'sublanguageid':",".join(lang),
            #                 'query'        :OS_search_string,
            #                 'year'         :year
            #                }]

            myLogger("Opensubtitles SearchSubtitles searchlist: " + repr(searchlist))
            search = self.server.SearchSubtitles( self.osdb_token, searchlist )
            myLogger("Opensubtitles SearchSubtitles search result: " + repr(search))

            try:
                data = search["data"]
                return data
            except:
                return []

        else:
            return []


    def download(self, ID, dest):
        from service import convert_to_utf
        try:
            import zlib, base64
            down_id=[ID,]
            result = self.server.DownloadSubtitles(self.osdb_token, down_id)
            if result["data"]:
                local_file = open(dest, "w" + "b")
                d = zlib.decompressobj(16+zlib.MAX_WBITS)
                data = d.decompress(base64.b64decode(result["data"][0]["data"]))
                local_file.write(data)
                local_file.close()
                # convert_to_utf(local_file)
                log( __name__,"Download Using XMLRPC")
                return True
            return False
        except:
           return False

def log(module, msg):
  xbmc.log((u"### [%s] - %s" % (module,msg,)),level=xbmc.LOGDEBUG )

def hashFile(file_path, rar):
    if rar:
      return OpensubtitlesHashRar(file_path)

    log( __name__,"Hash Standard file")
    longlongformat = 'q'  # long long
    bytesize = struct.calcsize(longlongformat)
    f = xbmcvfs.File(file_path)

    filesize = f.size()
    hash = filesize

    if filesize < 65536 * 2:
        return "SizeError"

    buffer = f.read(65536)
    f.seek(max(0,filesize-65536),0)
    buffer += f.read(65536)
    f.close()
    for x in range((65536/bytesize)*2):
        size = x*bytesize
        (l_value,)= struct.unpack(longlongformat, buffer[size:size+bytesize])
        hash += l_value
        hash = hash & 0xFFFFFFFFFFFFFFFF

    returnHash = "%016x" % hash
    return filesize,returnHash


def OpensubtitlesHashRar(firsrarfile):
    log( __name__,"Hash Rar file")
    f = xbmcvfs.File(firsrarfile)
    a=f.read(4)
    if a!='Rar!':
        raise Exception('ERROR: This is not rar file.')
    seek=0
    for i in range(4):
        f.seek(max(0,seek),0)
        a=f.read(100)
        type,flag,size=struct.unpack( '<BHH', a[2:2+5])
        if 0x74==type:
            if 0x30!=struct.unpack( '<B', a[25:25+1])[0]:
                raise Exception('Bad compression method! Work only for "store".')
            s_partiizebodystart=seek+size
            s_partiizebody,s_unpacksize=struct.unpack( '<II', a[7:7+2*4])
            if (flag & 0x0100):
                s_unpacksize=(struct.unpack( '<I', a[36:36+4])[0] <<32 )+s_unpacksize
                log( __name__ , 'Hash untested for files biger that 2gb. May work or may generate bad hash.')
            lastrarfile=getlastsplit(firsrarfile,(s_unpacksize-1)/s_partiizebody)
            hash=addfilehash(firsrarfile,s_unpacksize,s_partiizebodystart)
            hash=addfilehash(lastrarfile,hash,(s_unpacksize%s_partiizebody)+s_partiizebodystart-65536)
            f.close()
            return (s_unpacksize,"%016x" % hash )
        seek+=size
    raise Exception('ERROR: Not Body part in rar file.')

def getlastsplit(firsrarfile,x):
    if firsrarfile[-3:]=='001':
        return firsrarfile[:-3]+('%03d' %(x+1))
    if firsrarfile[-11:-6]=='.part':
        return firsrarfile[0:-6]+('%02d' % (x+1))+firsrarfile[-4:]
    if firsrarfile[-10:-5]=='.part':
        return firsrarfile[0:-5]+('%1d' % (x+1))+firsrarfile[-4:]
    return firsrarfile[0:-2]+('%02d' %(x-1) )

def addfilehash(name,hash,seek):
    f = xbmcvfs.File(name)
    f.seek(max(0,seek),0)
    for i in range(8192):
        hash+=struct.unpack('<q', f.read(8))[0]
        hash =hash & 0xffffffffffffffff
    f.close()
    return hash

def normalizeString(str):
  if KODI_VERSION<=18:
      return unicodedata.normalize(
             u'NFKD', unicode(str)
             ).encode('ascii','ignore').decode('utf-8')
  else:
      return unicodedata.normalize(
             'NFKD', (str)
             ).encode('ascii','ignore').decode('utf-8')