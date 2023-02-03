import os
import shutil
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs,logging
import uuid
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
if KODI_VERSION<=18:
    xbmc_tranlate_path=xbmc.translatePath
else:
    import xbmcvfs
    xbmc_tranlate_path=xbmcvfs.translatePath
__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc_tranlate_path( __addon__.getAddonInfo('path') )
__profile__    = xbmc_tranlate_path( __addon__.getAddonInfo('profile') )
__resource__   = xbmc_tranlate_path( os.path.join( __cwd__, 'resources', 'lib' ) )
__temp__       = xbmc_tranlate_path( os.path.join( __profile__, 'temp_download', '') )

if xbmcvfs.exists(__temp__):
  try:
    shutil.rmtree(__temp__)
  except:
    pass
xbmcvfs.mkdirs(__temp__)

sys.path.append (__resource__)

from myLogger import myLogger

from OSUtilities import OSDBServer, log, hashFile, normalizeString

try:
    import HTMLParser
    html_parser = HTMLParser.HTMLParser()
    from urllib import urlretrieve
    from urllib import  unquote_plus, unquote, urlopen, quote
except:
    import html
    from urllib.request import urlretrieve
    from urllib.parse import  unquote_plus, unquote,  quote
def Search_opensubtitle( item,imdb_id ,mode_subtitle,all_setting,prefix_open):

  myLogger("Search_opensubtitle imdb: " + imdb_id)
  search_data = []  
  search_data = OSDBServer().searchsubtitles(item,imdb_id,all_setting)

  subtitle_list=[]
 
  if search_data != None:
    myLogger("Search_opensubtitle search_data: " + repr(search_data))   
    search_data.sort(key=lambda x: [not x['MatchedBy'] == 'moviehash',
                     not os.path.splitext(x['SubFileName'])[0] == os.path.splitext(os.path.basename(unquote(item['file_original_path'])))[0],
                     not normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")).lower() in x['SubFileName'].replace('.',' ').lower(),
                     not x['LanguageName'] == 'Undetermined'])
    myLogger("Search_opensubtitle search_data sorted: " + repr(search_data))
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
  
        try:
            listitem = xbmcgui.ListItem(label          = item_data["LanguageName"],
                                    label2         = '[COLOR bisque]'+str(x)+ '. '+prefix_open+' '+item_data["SubFileName"]+'[/COLOR]',
                                    iconImage      = str(int(round(float(item_data["SubRating"])/2))),
                                    thumbnailImage = item_data["ISO639"]
                                    )
        except:
            listitem = xbmcgui.ListItem(label          = item_data["LanguageName"],
                                    label2         = '[COLOR bisque]'+str(x)+ '. '+prefix_open+' '+item_data["SubFileName"]+'[/COLOR]',
                                    
                                    )
        listitem.setProperty( "sync", ("false", "true")[str(item_data["MatchedBy"]) == "moviehash"] )
        listitem.setProperty( "hearing_imp", ("false", "true")[int(item_data["SubHearingImpaired"]) != 0] )
        url = "plugin://%s/?action=download&link=%s&ID=%s&filename=%s&format=%s&source=%s&language=%s" % (__scriptid__,
                                                                          item_data["ZipDownloadLink"],
                                                                          item_data["IDSubtitleFile"],
                                                                          item_data["SubFileName"],
                                                                          item_data["SubFormat"],
                                                                          'opensubtitle',
                                                                          item_data["LanguageName"]
                                                                          )

        json_data={'url':url,
                 'label':item_data["LanguageName"],
                 'label2':'[COLOR bisque]'+str(x)+ '. '+prefix_open+' '+item_data["SubFileName"]+'[/COLOR]',
                 'iconImage':str(int(round(float(item_data["SubRating"])/2))),
                 'thumbnailImage':item_data["ISO639"],
                 'hearing_imp':("false", "true")[int(item_data["SubHearingImpaired"]) != 0],
                 'sync': ("false", "true")[str(item_data["MatchedBy"]) == "moviehash"]}

        if mode_subtitle>1  :
          if url not in url_list:
           
            url_list.append(url)
            subtitle_list.append(json_data)
          #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
          x=x+1
        else:
          subtitle_list.append(json_data)
          return  Download_opensubtitle( item_data["IDSubtitleFile"],item_data["ZipDownloadLink"],item_data["SubFormat"],mode_subtitle),subtitle_list
          
          break
    return " ",subtitle_list
    
def Download_opensubtitle(id,url,format,mode_subtitle,stack=False):
  subtitle_list = []
  exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass" ]
  if stack:         ## we only want XMLRPC download if movie is not in stack,
                    ## you can only retreive multiple subs in zip
    result = False
  else:
    subtitle = os.path.join(__temp__, "%s.%s" %(str(uuid.uuid4()), format))
    try:
      result =OSDBServer().download(id, subtitle)
    except:
      log( __name__, "failed to connect to service for subtitle download")
      return subtitle_list
  if not result:
    log( __name__,"Download Using HTTP")
    zip = os.path.join( __temp__, "OpenSubtitles.zip")
    f = urllib.urlopen(url)
    myLogger(url)
    with open(zip, "wb") as subFile:
      subFile.write(f.read())
    subFile.close()
    xbmc.sleep(500)
    xbmc.executebuiltin(('Extract("%s","%s")' % (zip,__temp__,)).encode('utf-8'), True)
    for file in xbmcvfs.listdir(zip)[1]:
      file = os.path.join(__temp__, file)
      if (os.path.splitext( file )[1] in exts):
        subtitle_list.append(file)
  else:
    subtitle_list.append(subtitle)

  if xbmcvfs.exists(subtitle_list[0]):
    if mode_subtitle>1:
      return subtitle_list
    else:
      return subtitle_list[0]

      #xbmc.Player().setSubtitles(subtitle_list[0])
    