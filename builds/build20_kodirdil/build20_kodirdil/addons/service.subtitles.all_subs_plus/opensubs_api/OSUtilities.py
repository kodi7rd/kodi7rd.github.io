# -*- coding: utf-8 -*-

import xbmc, xbmcaddon
import requests
import os

from myLogger import myLogger

__addon__ = xbmcaddon.Addon()
__language__ = __addon__.getLocalizedString
MyAddonName = __addon__.getAddonInfo('name').replace(" ","_")
MyAddonVersion = __addon__.getAddonInfo('version')

BASE_URL_OS_API = u"https://api.opensubtitles.com/api/v1"
USER_AGENT = '%s v%s' %(MyAddonName, MyAddonVersion)

DEFAULT_USERNAME = 'allsubsplusos'
DEFAULT_PASS = 'allsubsplusos'

# DEFAULT_API_KEY = '9bOXkEUkqg5fHTWCrOQ6pYLBlHtRd9fM'
# OS_API_KEY = apiSettings if len(apiSettings) > 0 else DEFAULT_API_KEY
DEFAULT_API_KEYS = ['9bOXkEUkqg5fHTWCrOQ6pYLBlHtRd9fM', '3MeVyIKDINfXJPKMTAWtuGzJDYcAYTnb', 'yh4v2XkLaz4k341i5KW3a3yma46DafjE']
api_keys = DEFAULT_API_KEYS
apiSettings = __addon__.getSetting("OS_API_KEY")

if len(apiSettings) > 0:
    api_keys.insert(0, apiSettings)
OS_API_KEY = api_keys[0]

KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])

class OSDBServer:
    def __init__( self, *args, **kwargs ):
        try:
            usernameSettings = __addon__.getSetting("OSuser")
            passSettings = __addon__.getSetting("OSpass")
            username = usernameSettings if len(usernameSettings) > 0 else DEFAULT_USERNAME
            password = passSettings if len(passSettings) > 0 else DEFAULT_PASS

            payload = {
                "username": username,
                "password": password
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
                "Api-Key": OS_API_KEY
            }

            url = BASE_URL_OS_API + '/login';
            myLogger('OpenSubtitles Login: url - ' + repr(url))
            #myLogger('OpenSubtitles Login: details - ' + repr(payload))
            #myLogger('OpenSubtitles Login: api - ' + repr(OS_API_KEY))

            response = requests.post(url, json=payload, headers=headers)
            response_json = response.json()

            if response.status_code == 200:
                myLogger('OpenSubtitles Login: Succeeded')
                # response_json = response.json()
                myLogger('OpenSubtitles Login: response json - ' + repr(response_json))

                self.osdb_token  = response_json['token']
                myLogger('OpenSubtitles token: ' + repr(self.osdb_token))
            else:
                myLogger('OpenSubtitles Login: Failed - status code: ' + repr (response.status_code))
                self.failedToLoginError(response_json)

        except Exception as e:
            myLogger('OpenSubtitles Login error: ' + repr(e))
            self.failedToLoginError(response_json)
            pass


    def failedToLoginError(self, response_json):
        from service import notify3
        msg = (__language__(32120) + repr(response_json['message'])).replace(","," - ").replace("'","")
        myLogger(msg)
        notify3(msg, 5)

    def searchsubtitles( self, item, imdb_id, all_setting ):
        from service import main_languages
        tvshow = item['tvshow']
        season = item['season']
        episode = item['episode']
        year = item['year']
        title = item['title']

        if (hasattr(self,'osdb_token')):
            url = BASE_URL_OS_API + '/subtitles';

            headers = {
                "User-Agent": USER_AGENT,
                "Api-Key": OS_API_KEY
            }

            lang=[]
            for _lang in main_languages:
                if (_lang.lower() in all_setting
                    and all_setting[_lang.lower()] == 'true'):
                    lang.append(xbmc.convertLanguage(_lang, xbmc.ISO_639_1))
            if all_setting["all_lang"] == 'true':
                lang.append('ALL')
            if len(all_setting["other_lang"]) > 0:
                all_lang=all_setting["other_lang"].split(",")
                for item in all_lang:
                    # full_lang = str(xbmc.convertLanguage(item, xbmc.ENGLISH_NAME))
                    # short_lang = xbmc.convertLanguage(full_lang, xbmc.ISO_639_1)
                    # lang.append(str(short_lang))
                    lang.append(str(item))

            lang_string = ','.join(lang)
            myLogger('OS Langs: ' + repr(lang_string))

            querystring = {}
            querystring['languages'] = lang_string

            if imdb_id.startswith('tt'):
                # With imdb (Can be with ot without the 'tt' prefix)
                # querystring['imdb_id'] = imdb_id
                if len(tvshow) > 0:
                    #################################################
                    # option 1 - TV Shows - by imdb/season/episode
                    #################################################
                    querystring['parent_imdb_id'] = imdb_id
                    querystring['season_number'] = season
                    querystring['episode_number'] = episode
                else:
                    #################################################
                    # option 2 - Movies - by imdb
                    #################################################
                    querystring['imdb_id'] = imdb_id

            else:
                # Without imdb
                querystring['query'] = title
                if len(tvshow) > 0:
                    #################################################
                    # option 3 - TV Shows - by tvshow/season/episode
                    #################################################
                    querystring['season_number'] = season
                    querystring['episode_number'] = episode
                else:
                    #################################################
                    # option 4 - Movies - by title/year
                    #################################################
                    querystring['year'] = year

            response_json_data = []

            myLogger("Opensubtitles SearchSubtitles querystring: " + repr(querystring))
            response = requests.get(url, headers=headers, params=querystring)
            response_json = response.json()

            myLogger("Opensubtitles SearchSubtitles search result: Number of pages - " + repr(response_json['total_pages']))
            for _page in range(response_json['total_pages']):
                querystring['page'] = _page + 1
                myLogger("Opensubtitles SearchSubtitles querystring: " + repr(querystring))
                response = requests.get(url, headers=headers, params=querystring)
                response_json = response.json()
                response_json_data.extend(response_json['data'])

            myLogger("Opensubtitles SearchSubtitles search result: " + repr(response_json_data))

            try:
                return response_json_data
            except:
                return []

        else:
            return []


    def download(self, file_id, MySubFolder2):
        from service import notify3

        if (hasattr(self,'osdb_token')):
            url = BASE_URL_OS_API + '/download';
            payload = {"file_id": int(file_id)}

            apikey_index = 1
            for _apikey in api_keys:
                myLogger("Opensubtitles download API Key (%s)" %(apikey_index))
                apikey_index += 1

                headers = {
                    "User-Agent": USER_AGENT,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Api-Key": _apikey,
                    "Authorization": "Bearer %s" %(self.osdb_token)
                }

                #try catch

                myLogger("Opensubtitles download payload: " + repr(payload))
                response = requests.post(url, json=payload, headers=headers)
                response_json = response.json()
                myLogger("Opensubtitles download result: " + repr(response_json))

                if (response.status_code == 200):

                    _filename = response_json['file_name']
                    archive_file = os.path.join(MySubFolder2, _filename)

                    _url = response_json['link']
                    response = requests.get(_url)

                    subtitle_list = []
                    with open(archive_file, 'wb') as handle:
                        for block in response.iter_content(1024):
                            handle.write(block)

                    subtitle_list.append(archive_file)

                    return subtitle_list

            #If failed after all api_keys attemps
            myLogger('OpenSubtitles download: Failed - status code: ' + repr (response.status_code))
            msg = __language__(32119) + repr(response_json['message'])
            myLogger(msg)
            notify3(msg, 5)
            # return []



def log(module, msg):
  xbmc.log((u"### [%s] - %s" % (module,msg,)),level=xbmc.LOGDEBUG )

def normalizeString(str):
  import unicodedata

  if KODI_VERSION<=18:
      return unicodedata.normalize(
             u'NFKD', unicode(str)
             ).encode('ascii','ignore').decode('utf-8')
  else:
      return unicodedata.normalize(
             'NFKD', (str)
             ).encode('ascii','ignore').decode('utf-8')