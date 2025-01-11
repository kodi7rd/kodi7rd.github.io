# created by Venom for Fenomscrapers (updated 3-02-2022) modified by umbrella_dev 10-8-24
"""
    Cocoscrapers Project
"""

import re, requests
from cocoscrapers.modules import source_utils, cache
from cocoscrapers.modules.control import setting as getSetting, homeWindow, sleep
from cocoscrapers.modules import log_utils
session = requests.Session()

############KODI-RD-IL###################
debrid_dict = {'Real-Debrid': 'realdebrid' , 'Premiumize.me': 'premiumize' , 'AllDebrid': 'alldebrid'}
############KODI-RD-IL###################


class source:
    priority = 1
    pack_capable = True
    hasMovies = True
    hasEpisodes = True
    def __init__(self):
        self.language = ['en']
        self.base_link = 'https://mediafusion.elfhosted.com'
        # mediafusion_encrypted_secret settings: Expired RD API Key | only_show_cached_streams:true | max_streams_per_resolution:999 | No sorting options | No nudity/certification filter | show_full_torrent_name:true | show_language_country_flag:false
        self.mediafusion_encrypted_secret = "D-MsqOk5Q1moSiVAYZw8RmHhmuqtfCpU-J06SlHDJH0kfNVEAqHepRqYKH9IDMdKUIES7mGWe-UQ1noze2U9HLkU-rv6QLqXUtU8k68yVpDYzpJ0N4FeaN301ZCj6OyZG-l-KRb4gvkx758sDB2P236O0urgd6TwKRGe9RPojRGrt1n3kZTxnYf-gkswJ01GxBfIYvGwc49AJmtapHHEhyFMysa3EeN8EKO_JpYlRd_Hw"
        self.movieSearch_link = '/%s/stream/movie/%s.json'
        self.tvSearch_link = '/%s/stream/series/%s:%s:%s.json'
        self.min_seeders = 0
        self.bypass_filter = getSetting('mediafusion_cached.bypass_filter')


    # def _get_mediafusion_encrypted_secret(self, debrid_service, debrid_token):
    
        # Important settings:
        # only_show_cached_streams=true
        # max_streams_per_resolution=999
        # mediafusion_user_settings = (
            # '{"streaming_provider":{"token":"%s","service":"%s","enable_watchlist_catalogs":false,'
            # '"download_via_browser":false,"only_show_cached_streams":true},"selected_catalogs":[],'
            # '"selected_resolutions":["4k","2160p","1440p","1080p","720p","576p","480p","360p","240p",null],'
            # '"enable_catalogs":false,"enable_imdb_metadata":true,"max_size":"inf","max_streams_per_resolution":"999",'
            # '"torrent_sorting_priority":[],"show_full_torrent_name":true,"show_language_country_flag":false,"nudity_filter":["Disable"],'
            # '"certification_filter":["Disable"],"language_sorting":["English","Tamil","Hindi","Malayalam","Kannada",'
            # '"Telugu","Chinese","Russian","Arabic","Japanese","Korean","Taiwanese","Latino","French","Spanish",'
            # '"Portuguese","Italian","German","Ukrainian","Polish","Czech","Thai","Indonesian","Vietnamese",'
            # '"Dutch","Bengali","Turkish","Greek",null],"quality_filter":["BluRay/UHD","WEB/HD","DVD/TV/SAT",'
            # '"CAM/Screener","Unknown"],"api_password":null,"mediaflow_config":null,"rpdb_config":null,'
            # '"live_search_streams":false,"contribution_streams":false}'
        # ) % (debrid_token, debrid_service)

        # mediafusion_encrypted_secret = "invalid_configuration"
        # try:
            # response = requests.post(
                # f"{self.base_link}/encrypt-user-data",
                # headers={"Content-Type": "application/json"},
                # data=mediafusion_user_settings,
                # timeout=10
            # )
            # if response.status_code == 200:
                # result = response.json()
                # if result.get("status") == "success":
                    # mediafusion_encrypted_secret = result.get("encrypted_str", "invalid_configuration")
        # except Exception as e:
            # log_utils.log(f"Exception: {e}", level=log_utils.LOGDEBUG)
            # pass

        # return mediafusion_encrypted_secret

    def _get_files(self, url):
        ############KODI-RD-IL###################
        # WEIRD SEASON PACK BUG
        # if self.get_pack_files: return []
        results = session.get(url, timeout=10)
        files = results.json()['streams']
        return files

    def sources(self, data, hostDict):
        # self.get_pack_files = False
        sources = []
        if not data:
            # homeWindow.clearProperty('cocoscrapers.mediafusion_cached.performing_single_scrape')
            return sources

        ############KODI-RD-IL###################
        debrid_service = debrid_dict[data['debrid_service']]
        if debrid_service!="realdebrid": return sources
        ############KODI-RD-IL###################

        append = sources.append
        self.pack_get = False
        try:
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
            aliases = data['aliases']
            episode_title = data['title'] if 'tvshowtitle' in data else None
            year = data['year']
            imdb = data['imdb']
            
            if 'tvshowtitle' in data:
                # homeWindow.setProperty('cocoscrapers.mediafusion_cached.performing_single_scrape', 'true')
                season = data['season']
                episode = data['episode']
                hdlr = 'S%02dE%02d' % (int(season), int(episode))
                ############KODI-RD-IL###################
                url = '%s%s' % (self.base_link, self.tvSearch_link % (self.mediafusion_encrypted_secret, imdb, season, episode))
                ############KODI-RD-IL###################
                files = cache.get(self._get_files, 10, url)
            else:
                ############KODI-RD-IL###################
                url = '%s%s' % (self.base_link, self.movieSearch_link % (self.mediafusion_encrypted_secret, imdb))
                ############KODI-RD-IL###################
                hdlr = year
                files = self._get_files(url)
            #log_utils.log('mediafusion sources url = %s' % url)
            # homeWindow.clearProperty('cocoscrapers.mediafusion_cached.performing_single_scrape')
            _INFO = re.compile(r'💾.*')
            undesirables = source_utils.get_undesirables()
            check_foreign_audio = source_utils.check_foreign_audio()
        except:
            # homeWindow.clearProperty('cocoscrapers.mediafusion_cached.performing_single_scrape')
            source_utils.scraper_error('MEDIAFUSION_CACHED')
            return sources
        for file in files:
            try:
                if 'url' in file:
                    path = requests.utils.urlparse(file['url']).path.split('/')
                    hash = path[path.index('stream') + 1]
                else: hash = file['infoHash']
                #log_utils.log('mediafusion hash: %s' % hash)
                file_title = file['description'].split('\n')
                #file_title = file['behaviorHints']['filename']
                file_info = [x for x in file_title if _INFO.match(x)][0]
                name = source_utils.clean_name(file_title[0])

                if not source_utils.check_title(title, aliases, name.replace('.(Archie.Bunker', ''), hdlr, year): continue
                name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
                if source_utils.remove_lang(name_info, check_foreign_audio): continue
                if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

                url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name) 

                quality, info = source_utils.get_release_quality(name_info, url)
                try:
                    size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', file_info).group(0)
                    dsize, isize = source_utils._size(size)
                    info.insert(0, isize)
                except: dsize = 0
                info = ' | '.join(info)

                append({'provider': 'mediafusion_cached', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
                            'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'cached_checked': 'true'})
            except:
                # homeWindow.clearProperty('cocoscrapers.mediafusion_cached.performing_single_scrape')
                source_utils.scraper_error('MEDIAFUSION_CACHED')
        return sources

    def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
        # self.get_pack_files = True
        sources = []
        if not data: return sources

        ############KODI-RD-IL###################
        debrid_service = debrid_dict[data['debrid_service']]
        if debrid_service!="realdebrid": return sources
        ############KODI-RD-IL###################

        # count, finished_single_scrape = 0, False
        # sleep(2000)
        # while count < 10000 and not finished_single_scrape:
            # finished_single_scrape = homeWindow.getProperty('cocoscrapers.mediafusion_cached.performing_single_scrape') != 'true'
            # sleep(100)
            # count += 100
        # if not finished_single_scrape: return sources
        # sleep(1000)
        sources_append = sources.append
        try:
            title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
            aliases = data['aliases']
            imdb = data['imdb']
            year = data['year']
            season = data['season']
            ############KODI-RD-IL###################
            url = '%s%s' % (self.base_link, self.tvSearch_link % (self.mediafusion_encrypted_secret, imdb, season, data['episode']))
            ############KODI-RD-IL###################
            files = cache.get(self._get_files, 10, url)
            _INFO = re.compile(r'💾.*') # _INFO = re.compile(r'👤.*')
            undesirables = source_utils.get_undesirables()
            check_foreign_audio = source_utils.check_foreign_audio()
        except:
            source_utils.scraper_error('MEDIAFUSION_CACHED')
            return sources
        for file in files:
            #log_utils.log('pack file: %s' % str(file),1)
            try:
                if 'url' in file:
                    path = requests.utils.urlparse(file['url']).path.split('/')
                    hash = path[path.index('stream') + 1]
                else: hash = file['infoHash']
                file_title = file['description'].split('\n')
                file_info = [x for x in file_title if _INFO.match(x)][0]

                name = source_utils.clean_name(file_title[0])

                episode_start, episode_end = 0, 0
                if not search_series:
                    if not bypass_filter:
                        valid, episode_start, episode_end = source_utils.filter_season_pack(title, aliases, year, season, name.replace('.(Archie.Bunker', ''))
                        if not valid: continue
                    package = 'season'

                elif search_series:
                    if not bypass_filter:
                        valid, last_season = source_utils.filter_show_pack(title, aliases, imdb, year, season, name.replace('.(Archie.Bunker', ''), total_seasons)
                        if not valid: continue
                    else: last_season = total_seasons
                    package = 'show'

                name_info = source_utils.info_from_name(name, title, year, season=season, pack=package)
                if source_utils.remove_lang(name_info, check_foreign_audio): continue
                if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

                url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)
                quality, info = source_utils.get_release_quality(name_info, url)
                try:
                    size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', file_info).group(0)
                    dsize, isize = source_utils._size(size)
                    info.insert(0, isize)
                except: dsize = 0
                info = ' | '.join(info)

                item = {'provider': 'mediafusion_cached', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
                            'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': package, 'cached_checked': 'true'}
                if search_series: item.update({'last_season': last_season})
                elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
                sources_append(item)
            except:
                source_utils.scraper_error('MEDIAFUSION_CACHED')
        return sources

