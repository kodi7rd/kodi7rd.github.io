import os
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import uuid

KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
if KODI_VERSION<=18:
    xbmc_translate_path=xbmc.translatePath
else:
    import xbmcvfs
    xbmc_translate_path=xbmcvfs.translatePath

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc_translate_path( __addon__.getAddonInfo('path') )
__resource__   = xbmc_translate_path( os.path.join( __cwd__, 'resources', 'lib' ) )


sys.path.append (__resource__)

from myLogger import myLogger

from .OSUtilities import OSDBServer, log, hashFile, normalizeString

try:
    # import HTMLParser
    # html_parser = HTMLParser.HTMLParser()
    from urllib import urlretrieve
    from urllib import  unquote_plus, unquote, quote
except:
    # import html
    from urllib.request import urlretrieve
    from urllib.parse import  unquote_plus, unquote,  quote

def GetOpenSubtitlesJson( item,imdb_id ,mode_subtitle,all_setting,prefix_open, color_open):
    from service import colorize_text
    myLogger("Search_opensubtitle imdb: " + imdb_id)
    search_data = []
    search_data = OSDBServer().searchsubtitles(item,imdb_id,all_setting)

    subtitle_list=[]

    if search_data != None:
        #myLogger("Search_opensubtitle search_data: " + repr(search_data))
        search_data.sort(key=lambda x: [not x['MatchedBy'] == 'moviehash',
                         not os.path.splitext(x['SubFileName'])[0] == os.path.splitext(os.path.basename(unquote(item['file_original_path'])))[0],
                         not normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")).lower() in x['SubFileName'].replace('.',' ').lower(),
                         not x['LanguageName'] == 'Undetermined'])

        myLogger("Search_opensubtitle search_data sorted: " + repr(search_data))
        #x=1
        url_list=[]
        for item_data in search_data:
            nlabel = item_data["LanguageName"]
            nlabel2 = colorize_text(item_data["SubFileName"],color_open)
            #nlabel2 = colorize_text(prefix_open+' '+item_data["SubFileName"],color_open)
            #nlabel2 = colorize_text(str(x)+ '. '+prefix_open+' '+item_data["SubFileName"],color_open)
            nicon = colorize_text(prefix_open,color_open)
            #nicon = str(int(round(float(item_data["SubRating"])/2)))
            nthumb = item_data["ISO639"]

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


                url = "plugin://%s/?action=download&link=%s&id=%s&filename=%s&subformat=%s&source=%s&language=%s&thumbLang=%s" % (__scriptid__,
                                                                                  item_data["ZipDownloadLink"],
                                                                                  'opensubs$$$' + item_data["IDSubtitleFile"],
                                                                                  item_data["SubFileName"],
                                                                                  item_data["SubFormat"],
                                                                                  'opensubtitle',
                                                                                  item_data["LanguageName"],
                                                                                  nthumb
                                                                                  )

                json_data={'url':url,
                         'label':nlabel,
                         'label2':nlabel2,
                         'iconImage':nicon,
                         'thumbnailImage':nthumb,
                         'hearing_imp':("false", "true")[int(item_data["SubHearingImpaired"]) != 0],
                         #'hearing_imp': "true" if int(item_data["SubHearingImpaired"]) != 0 else "false",
                         'sync': ("false", "true")[str(item_data["MatchedBy"]) == "moviehash"]}

                if mode_subtitle>1  :
                    if url not in url_list:

                      url_list.append(url)
                      subtitle_list.append(json_data)
                    #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
                    #x=x+1
                else:
                    subtitle_list.append(json_data)
                    return  Download_opensubtitle( item_data["IDSubtitleFile"],item_data["ZipDownloadLink"],item_data["SubFormat"],mode_subtitle),subtitle_list

                    break
        return subtitle_list,search_data

def Download_opensubtitle(id,url,filename,subformat,mode_subtitle,stack=False):
    from service import MyZipFolder2,MySubFolder2
    MyZipFolder = MyZipFolder2
    MySubFolder = MySubFolder2

    subtitle_list = []
    exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass" ]

    if stack:         ## we only want XMLRPC download if movie is not in stack,
                      ## you can only retreive multiple subs in zip
        isSucceeded = False
    else:
        #subtitle = os.path.join(MySubFolder, "%s.%s" %(str(uuid.uuid4()), subformat))
        ## filename = unquote(filename)
        ## filename = path.basename(filename)[:-4]
        ## subtitle = os.path.join(MySubFolder, "%s.%s" %(filename, subformat))
        subtitle = os.path.join(MySubFolder, filename)
        try:
            isSucceeded = OSDBServer().download(id, subtitle)
        except:
            log( __name__, "failed to connect to service for subtitle download")
            return subtitle_list

    if isSucceeded:
        subtitle_list.append(subtitle)
    else:
        log( __name__,"Download Using HTTP")
        zip = os.path.join( MyZipFolder, "OpenSubtitles.zip")
        f = urllib.request.urlopen(url)
        myLogger(url)
        with open(zip, "wb") as subFile:
            subFile.write(f.read())

        xbmc.sleep(500)
        xbmc.executebuiltin('Extract("%s","%s")' % (zip,MySubFolder,))

        for file in xbmcvfs.listdir(zip)[1]:
            file = os.path.join(MySubFolder, file)
            if (os.path.splitext( file )[1] in exts):
                subtitle_list.append(file)

    if mode_subtitle>1:
        return subtitle_list
    else:
        # if xbmcvfs.exists(subtitle_list[0]):
        if os.path.exists(subtitle_list[0]):
            return subtitle_list[0]

    #xbmc.Player().setSubtitles(subtitle_list[0])
