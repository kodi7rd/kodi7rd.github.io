import uuid,shutil
import xbmcaddon,os,xbmc
global global_var,stop_all,site_id,sub_color#global
global_var=[]
import socket
import http.client as httplib
from resources.modules import log
import requests,json,re
from resources.modules import cache
from urllib.request import urlretrieve,urlopen
from urllib.parse import  unquote_plus, unquote,  quote
import urllib
import urllib.parse
from resources.modules.extract_sub import extract

que=urllib.parse.quote_plus
Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
BASE_URL_XMLRPC = u"https://api.opensubtitles.org/xml-rpc"
__version__    = Addon.getAddonInfo('version') # Module version
__scriptname__ = "XBMC Subtitles Unofficial"
site_id='[Op]'
sub_color='bisque'
try:
    import xmlrpclib
    from xmlrpclib import Transport
except:
    import xmlrpc.client as xmlrpclib
    from xmlrpc.client import Transport
import xbmcvfs
import struct
xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_open'))


class TimeoutTransport(xmlrpclib.Transport):

    def __init__(self, use_datetime=0, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 secure=False):
        xmlrpclib.Transport.__init__(self, use_datetime)
        self.timeout = timeout
        self.secure = secure

    def make_connection(self, host):
        if self._connection and host == self._connection[0]:
            return self._connection[1]
        chost, self._extra_headers, x509 = self.get_host_info(host)
        if self.secure:
            self._connection = host, httplib.HTTPSConnection(
                chost, None, timeout=self.timeout, **(x509 or {})
            )
        else:
            self._connection = host, httplib.HTTPConnection(
                chost, timeout=self.timeout
            )

        return self._connection[1]

    
class OSDBServer:
  def __init__( self, *args, **kwargs ):
    Addon=xbmcaddon.Addon()
    socket.setdefaulttimeout(5)
    self.server = xmlrpclib.Server( BASE_URL_XMLRPC, verbose=0 ,transport=TimeoutTransport())
     
    login = self.server.LogIn("", "", "en", "%s_v%s" %(__scriptname__.replace(" ","_"),__version__))
    log.warning(login)
    self.osdb_token  = login[ "token" ]
  def hashFile(self): 
      
                 
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
    
      
                
  
    
  def searchsubtitles( self, item):
     try:
        file_hash,filesize=self.hashFile()
     except:
        file_hash=None
        filesize=None
     
     Addon=xbmcaddon.Addon()
     tvshow=item['TVshowtitle']
     season=item['season']
     episode=item['episode']
     year=item['year']
     title=item['OriginalTitle']
     imdb=item['imdb']
     imdb_id=imdb
     if ( self.osdb_token ) :
      searchlist  = []
      lang=[]
      
      if Addon.getSetting("language_hebrew")=='true':
       lang.append('heb')
      if Addon.getSetting("language_english")=='true':
       lang.append('eng')
      if Addon.getSetting("language_russian")=='true':
        lang.append('rus')
      if Addon.getSetting("language_arab")=='true':
        lang.append('ara')
      if Addon.getSetting("all_lang")=='true':
        lang.append('ALL')
      if len(Addon.getSetting("other_lang"))>0:
         all_lang=Addon.getSetting("other_lang").split(",")
         for items in all_lang:
           lang.append(str(items))
      log.warning(lang)
      if len(tvshow) > 0:
         a=1
         OS_search_string = ("%s S%.2dE%.2d" % (tvshow,int(season),int(episode),)).replace(" ","+")
        
      else:

        
        if not imdb_id:
          OS_search_string = title.replace(" ","+")
        else:
          OS_search_string = imdb_id
         

      if not False:
        


       
        
        if 'tt' not in imdb:
          imdb=imdb_id.replace('tt','')
        if imdb=='':
           imdb=str((str(imdb_id)).replace('tt',''))
        imdb=imdb.replace('tt','')
        log.warning(imdb)
        log.warning(tvshow)
        if  (len(tvshow)==0 and imdb != ""):
        
          searchlist.append({'sublanguageid' :",".join(lang),
                             'imdbid'        :imdb,
                             
                             
                             
                            })
        if len(tvshow)>0:
          searchlist.append({'season' :season,
                             'sublanguageid' :",".join(lang),
                             'imdbid'        :imdb,
                             'query'        :OS_search_string,
                             'episode':episode,
                             
                             
                            })
        else:
        
          searchlist.append({'sublanguageid':",".join(lang),
                          'query'        :OS_search_string,
                          'year'         :year,
                          
                         }) 
      
      else:
        searchlist = [{'sublanguageid':",".join(lang),
                       'query'        :OS_search_string,
                       'year'         :year
                      }]
      if file_hash:
        searchlist.append({'sublanguageid':",".join(lang),
                          'moviehash':(file_hash)
                          
                         })
      search = self.server.SearchSubtitles( self.osdb_token, searchlist )


      if search["data"]:
        return search["data"]  


  def download(self, ID, dest):
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
         log( __name__,"Download Using XMLRPC")
         return True
       return False
     except:
       return False
       
def get_subs(item):
    global global_var
    log.warning('Searching Opensubtitles')
    search_data = []

   
      
    search_data = OSDBServer().searchsubtitles(item)
    log.warning('search_data:')
    log.warning(search_data)
   
    subtitle_list=[]
    

    if search_data != None:
       
        #search_data.sort(key=lambda x: [not x['MatchedBy'] == 'moviehash',
        #                 not os.path.splitext(x['SubFileName'])[0] == os.path.splitext(os.path.basename(unquote(item['file_original_path'])))[0],
        #                 not (item["OriginalTitle"]).lower() in x['SubFileName'].replace('.',' ').lower(),
        #                 not x['LanguageName'] == 'Undetermined'])
        x=1
        url_list=[]
        for item_data in search_data:
          


          ## hack to work around issue where Brazilian is not found as language in XBMC

          try:
           item['season']=int(item['season'])
           item['episode']=int(item['episode'])
           item_data['SeriesSeason']=int(item_data['SeriesSeason'])
           item_data['SeriesEpisode']=int(item_data['SeriesEpisode'])
          except:
             pass
          if ((item['season'] == item_data['SeriesSeason'] and
              item['episode'] == item_data['SeriesEpisode']) or
              (item['season'] == 0 and item['episode'] == 0) ## for file search, season and episode == ""
             ):
            download_data={}
            download_data['link']=item_data["ZipDownloadLink"]
            download_data['id']=item_data["IDSubtitleFile"]
            download_data['format']=item_data["SubFormat"]
            
            url = "plugin://%s/?action=download&filename=%s&language=%s&download_data=%s&source=opensubtitles" % (MyScriptID,
                                                                              
                                                                              que(item_data["SubFileName"]),
                                                                              item_data["LanguageName"],
                                                                              que(json.dumps(download_data))
                                                                              )

            json_data={'url':url,
                     'label':item_data["LanguageName"],
                     'label2':site_id+' '+item_data["SubFileName"],
                     'iconImage':str(int(round(float(item_data["SubRating"])/2))),
                     'thumbnailImage':item_data["ISO639"],
                     'hearing_imp':("false", "true")[int(item_data["SubHearingImpaired"]) != 0],
                     'site_id':site_id,
                     'sub_color':sub_color,
                     'filename':item_data["SubFileName"],
                     'sync': ("false", "true")[str(item_data["MatchedBy"]) == "moviehash"]}

            
            if url not in url_list:
               
                url_list.append(url)
                subtitle_list.append(json_data)
                global_var=subtitle_list
              
            x=x+1
            
def download(download_data,MySubFolder):
    
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)
    id=download_data['id']
    format=download_data['format']
    url=download_data['link']
 

    exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass" ]
    
    subFile = os.path.join(MyTmp, "%s.%s" %(str(uuid.uuid4()), format))
    try:
      result =OSDBServer().download(id, subFile)
    except Exception as e:
      log.warning( __name__, "failed to connect to service for subtitle download")
      log.warning(str(e))
      
    log.warning(result)
    if not result:

        subFile = os.path.join( MyTmp, "OpenSubtitles.zip")
        f = urlopen(url)
        log.warning(url)
        with open(subFile, "wb") as zip_subFile:
          zip_subFile.write(f.read())
        zip_subFile.close()
        log.warning(subFile)
    sub_file=extract(subFile,MySubFolder)
    return sub_file
        


            