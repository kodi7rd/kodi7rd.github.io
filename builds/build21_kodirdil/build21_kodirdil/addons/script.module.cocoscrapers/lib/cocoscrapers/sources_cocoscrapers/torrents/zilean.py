from json import loads as jsloads
from cocoscrapers.modules import client
from cocoscrapers.modules import source_utils, cache
from cocoscrapers.modules.control import setting as getSetting, homeWindow, sleep

class source:
    priority = 1
    pack_capable = True
    hasMovies = True
    hasEpisodes = True
    def __init__(self):
        self.language = ['en']
        self.base_link = "https://zilean.elfhosted.com"
        self.movieSearch_link = '/dmm/filtered?ImdbId=%s'
        self.tvSearch_link = '/dmm/filtered?ImdbId=%s&Season=%s&Episode=%s'
        self.bypass_filter = getSetting('zilean.bypass_filter')

    def _get_files(self, url):
        if self.get_pack_files: return []
        results = client.request(url, timeout=10)
        files = jsloads(results)
        return files

    def sources(self, data, hostDict):
        self.get_pack_files = False
        sources = []
        if not data:
            homeWindow.clearProperty('cocoscrapers.zilean.performing_single_scrape')
            return sources
        sources_append = sources.append
        try:
            aliases = data['aliases']
            year = data['year']
            imdb = data['imdb']
            if 'tvshowtitle' in data:
                homeWindow.setProperty('cocoscrapers.zilean.performing_single_scrape', 'true')
                title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
                episode_title = data['title']
                season = data['season']
                episode = data['episode']
                hdlr = 'S%02dE%02d' % (int(season), int(episode))
                years = None
                url = '%s%s' % (self.base_link, self.tvSearch_link % (imdb, season, episode))
                files = cache.get(self._get_files, 10, url)
            else:
                title = data['title'].replace('&', 'and').replace('/', ' ').replace('$', 's')
                episode_title = None
                hdlr = year
                years = [str(int(year)-1), str(year), str(int(year)+1)]
                url = '%s%s' % (self.base_link, self.movieSearch_link % imdb)
                files = self._get_files(url)
            homeWindow.clearProperty('cocoscrapers.zilean.performing_single_scrape')
            undesirables = source_utils.get_undesirables()
            check_foreign_audio = source_utils.check_foreign_audio()
        except:
            homeWindow.clearProperty('cocoscrapers.zilean.performing_single_scrape')
            source_utils.scraper_error('ZILEAN')
            return sources

        for file in files:
            try:
                hash = file['info_hash']
                name = source_utils.clean_name(file['raw_title'])
                size = float(file['size']) / (1024 ** 3)
                
                if self.bypass_filter == 'false':
                    if not source_utils.check_title(title, aliases, name, hdlr, year, years): continue
                name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
                if source_utils.remove_lang(name_info, check_foreign_audio): continue
                if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

                url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)

                quality, info = source_utils.get_release_quality(name_info, url)

                sources_append({'provider': 'zilean', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info,
                                            'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': size})
            except:
                homeWindow.clearProperty('cocoscrapers.zilean.performing_single_scrape')
                source_utils.scraper_error('ZILEAN')
        return sources

    def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
        self.get_pack_files = True
        sources = []
        if not data: return sources
        count, finished_single_scrape = 0, False
        sleep(2000)
        while count < 10000 and not finished_single_scrape:
            finished_single_scrape = homeWindow.getProperty('cocoscrapers.zilean.performing_single_scrape') != 'true'
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
            url = '%s%s' % (self.base_link, self.tvSearch_link % (imdb, season, data['episode']))
            files = cache.get(self._get_files, 10, url)
            undesirables = source_utils.get_undesirables()
            check_foreign_audio = source_utils.check_foreign_audio()
        except:
            source_utils.scraper_error('ZILEAN')
            return sources

        for file in files:
            try:
                hash = file['info_hash']
                name = source_utils.clean_name(file['raw_title'])
                size = float(file['size']) / (1024 ** 3)
                
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

                item = {'provider': 'zilean', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
                            'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': size, 'package': package}
                if search_series: item.update({'last_season': last_season})
                elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
                sources_append(item)
            except:
                source_utils.scraper_error('ZILEAN')
        return sources