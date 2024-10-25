import re
from cocoscrapers.modules import client
from cocoscrapers.modules import source_utils, cache
from cocoscrapers.modules.control import homeWindow, sleep

class source:
    priority = 1
    pack_capable = True
    hasMovies = True
    hasEpisodes = True
    def __init__(self):
        self.language = ['en']
        # APROPO Pastebin Torrents
        self.base_link = "https://pastebin.com/raw/YWR3ND0v"
        self.bypass_filter = 'false'

    def _get_files(self, imdb):
        if self.get_pack_files: return []
        
        response = client.request(self.base_link, timeout=10)
        
        regex = 'imdb:"(.+?)" info:"(.+?)" size:"(.+?)" url:"(.+?)"'
        
        results = re.compile(regex, re.DOTALL).findall(response)
        
        torrents = []
        for imdb_id, info, size, url in results:
            if imdb_id == imdb:
                hash = re.search(r'magnet:\?xt=urn:btih:(.*?)(?:&|$)', url, re.I).group(1)
                torrents.append({
                    "filename": info,
                    "size": size,
                    "hash": hash
                })
                
        return torrents

    def sources(self, data, hostDict):
        self.get_pack_files = False
        sources = []
        if not data:
            homeWindow.clearProperty('cocoscrapers.apropo_pb.performing_single_scrape')
            return sources
        sources_append = sources.append
        try:
            aliases = data['aliases']
            year = data['year']
            imdb = data['imdb']
            if 'tvshowtitle' in data:
                homeWindow.setProperty('cocoscrapers.apropo_pb.performing_single_scrape', 'true')
                title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
                episode_title = data['title']
                season = data['season']
                episode = data['episode']
                hdlr = 'S%02dE%02d' % (int(season), int(episode))
                years = None
                files = cache.get(self._get_files, 10, imdb)
            else:
                title = data['title'].replace('&', 'and').replace('/', ' ').replace('$', 's')
                episode_title = None
                hdlr = year
                years = [str(int(year)-1), str(year), str(int(year)+1)]
                files = self._get_files(imdb)
                
            homeWindow.clearProperty('cocoscrapers.apropo_pb.performing_single_scrape')
            undesirables = source_utils.get_undesirables()
            check_foreign_audio = source_utils.check_foreign_audio()
        except:
            homeWindow.clearProperty('cocoscrapers.apropo_pb.performing_single_scrape')
            source_utils.scraper_error('APROPO_PB')
            return sources

        for file in files:
            try:
                hash = file['hash']
                name = source_utils.clean_name(file['filename'])
                size = float(file['size'])
                
                if self.bypass_filter == 'false':
                    if not source_utils.check_title(title, aliases, name, hdlr, year, years): continue
                name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
                if source_utils.remove_lang(name_info, check_foreign_audio): continue
                if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

                if not episode_title: # filter for eps returned in movie query (rare but movie and show exists for Run in 2020)
                    ep_strings = [r'[.-]s\d{2}e\d{2}([.-]?)', r'[.-]s\d{2}([.-]?)', r'[.-]season[.-]?\d{1,2}[.-]?']
                    name_lower = name.lower()
                    if any(re.search(item, name_lower) for item in ep_strings): continue

                url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)
                
                quality, info = source_utils.get_release_quality(name_info, url)

                sources_append({'provider': 'apropo_pb', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info,
                                            'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': size})
            except:
                homeWindow.clearProperty('cocoscrapers.apropo_pb.performing_single_scrape')
                source_utils.scraper_error('APROPO_PB')
        return sources

    def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
        self.get_pack_files = True
        sources = []
        if not data: return sources
        count, finished_single_scrape = 0, False
        sleep(2000)
        while count < 10000 and not finished_single_scrape:
            finished_single_scrape = homeWindow.getProperty('cocoscrapers.apropo_pb.performing_single_scrape') != 'true'
            sleep(100)
            count += 100
        if not finished_single_scrape: return sources
        sources_append = sources.append
        try:
            title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
            aliases = data['aliases']
            imdb = data['imdb']
            year = data['year']
            season = data['season']
            files = cache.get(self._get_files, 10, imdb)
            undesirables = source_utils.get_undesirables()
            check_foreign_audio = source_utils.check_foreign_audio()
        except:
            source_utils.scraper_error('APROPO_PB')
            return sources

        for file in files:
            try:
                hash = file['hash']
                name = source_utils.clean_name(file['filename'])
                size = float(file['size'])
                
                if self.bypass_filter == 'true': bypass_filter = True

                episode_start, episode_end = 0, 0
                if not search_series:
                    if not bypass_filter:
                        valid, episode_start, episode_end = source_utils.filter_season_pack(title, aliases, year, season, name)
                        if not valid: continue
                    package = 'season'

                elif search_series:
                    if not bypass_filter:
                        valid, last_season = source_utils.filter_show_pack(title, aliases, imdb, year, season, name, total_seasons)
                        if not valid: continue
                    else: last_season = total_seasons
                    package = 'show'

                name_info = source_utils.info_from_name(name, title, year, season=season, pack=package)
                if source_utils.remove_lang(name_info, check_foreign_audio): continue
                if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

                url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)

                quality, info = source_utils.get_release_quality(name_info, url)

                item = {'provider': 'apropo_pb', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
                            'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': size, 'package': package}
                if search_series: item.update({'last_season': last_season})
                elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
                sources_append(item)
            except:
                source_utils.scraper_error('APROPO_PB')
        return sources