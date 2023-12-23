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

from .OSUtilities import OSDBServer, log, normalizeString

try:
    # import HTMLParser
    # html_parser = HTMLParser.HTMLParser()
    from urllib import urlretrieve
    from urllib import  unquote_plus, unquote, quote
except:
    # import html
    from urllib.request import urlretrieve
    from urllib.parse import  unquote_plus, unquote,  quote

def GetOpenSubtitlesJson( item,imdb_id ,mode_subtitle, all_setting ,prefix_open, color_open):
    from service import colorize_text
    myLogger("Search_opensubtitle imdb: " + imdb_id)
    search_data = []
    search_data = OSDBServer().searchsubtitles(item,imdb_id,all_setting)

    subtitle_list=[]

    if search_data != None:
        # #myLogger("Search_opensubtitle search_data: " + repr(search_data))
        # search_data.sort(key=lambda x: [not x['MatchedBy'] == 'moviehash',
        #             not os.path.splitext(x['SubFileName'])[0] == os.path.splitext(os.path.basename(unquote(item['file_original_path'])))[0],
        #         #  not normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")).lower() in x['SubFileName'].replace('.',' ').lower(),
        #             not x['LanguageName'] == 'Undetermined'])
        # myLogger("Search_opensubtitle search_data sorted: " + repr(search_data))

        #x=1
        url_list=[]
        for search_item in search_data:
            item_data = search_item['attributes']
            nlabel = xbmc.convertLanguage(item_data['language'], xbmc.ENGLISH_NAME)
            nlabel2 = colorize_text(item_data['files'][0]['file_name'],color_open)
            #nlabel2 = colorize_text(prefix_open+' '+item_data["SubFileName"],color_open)
            #nlabel2 = colorize_text(str(x)+ '. '+prefix_open+' '+item_data["SubFileName"],color_open)
            nicon = colorize_text(prefix_open,color_open)
            #nicon = str(int(round(float(item_data["SubRating"])/2)))
            nthumb = item_data["language"]
            # n_hearing_impaired = item_data["hearing_impaired"]
            n_hearing_impaired = "true" if item_data["hearing_impaired"] == True else "false"

            file_id = str(item_data['files'][0]['file_id'])

            # try:
            #     item['season'] = int(item['season'])
            #     item['episode'] = int(item['episode'])
            #     os_season_number = int(item_data['feature_details']['season_number'])
            #     os_episode_number = int(item_data['feature_details']['episode_number'])
            # except:
            #     pass

            # if ((item['season'] == os_season_number and
            #     item['episode'] == os_episode_number) or
            #     (item['season'] == 0 and item['episode'] == 0) ## for file search, season and episode == ""
            #    ):

            url = "plugin://%s/?action=download&id=%s&filename=%s&source=%s&language=%s&thumbLang=%s" % (
                                                                                __scriptid__,
                                                                                'opensubs$$$' + file_id,
                                                                                nlabel2,
                                                                                'opensubtitle',
                                                                                nlabel,
                                                                                nthumb
                                                                                )


            json_data = {'url':url,
                         'label':nlabel,
                         'label2':nlabel2,
                         'iconImage':nicon,
                         'thumbnailImage':nthumb,
                         'hearing_imp': n_hearing_impaired,
                         'sync': "false"}

            if mode_subtitle>1:
                if url not in url_list:
                    url_list.append(url)
                    subtitle_list.append(json_data)
                #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
                #x=x+1
            else:
                subtitle_list.append(json_data)
                return  Download_opensubtitle(file_id, mode_subtitle), subtitle_list

                #break
        return subtitle_list, search_data

def Download_opensubtitle(file_id ,mode_subtitle):
    from service import MySubFolder2
    subtitle_list = OSDBServer().download(file_id, MySubFolder2)

    if mode_subtitle>1:
        return subtitle_list
    else:
        # if xbmcvfs.exists(subtitle_list[0]):
        if os.path.exists(subtitle_list[0]):
            return subtitle_list[0]


