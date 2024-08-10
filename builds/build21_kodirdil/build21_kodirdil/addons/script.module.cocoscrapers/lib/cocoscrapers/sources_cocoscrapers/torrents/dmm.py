from json import loads as jsloads
import re
from cocoscrapers.modules import client
from cocoscrapers.modules import source_utils
from cocoscrapers.modules import control

class source:
    priority = 1
    pack_capable = True
    hasMovies = True
    hasEpisodes = True
    def __init__(self):
        self.language = ['en']
        self.base_link = 'https://debridmediamanager.com/api/torrents'
        self.bypass_filter = control.setting('dmm.bypass_filter')
        
    def get_sources(self, media_type, imdb, added_seasonNum):
        import os
        from hashlib import sha256

        dmmProblemKey = f"{os.urandom(4).hex()}-none"
        solution = sha256(dmmProblemKey.encode('utf-8')).hexdigest()
        url = f'{self.base_link}/{media_type}?imdbId={imdb}{added_seasonNum}&dmmProblemKey={dmmProblemKey}&solution={solution}&onlyTrusted=false'

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'dnt': '1',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://debridmediamanager.com/movie/tt1630029',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        
        results = client.request(url, headers=headers, timeout=5)
        return results


    def sources(self, data, hostDict):
        sources = []
        if not data: return sources
        sources_append = sources.append
        try:
            aliases = data['aliases']
            year = data['year']
            imdb = data['imdb']
            if 'tvshowtitle' in data:
                title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
                episode_title = data['title']
                season = data['season']
                episode = data['episode']
                hdlr = 'S%02dE%02d' % (int(season), int(episode))
                years = None
                ############KODI-RD-IL###################
                media_type = 'tv'
                added_seasonNum = f"&seasonNum={str(season)}"
                #########################################
            else:
                title = data['title'].replace('&', 'and').replace('/', ' ').replace('$', 's')
                episode_title = None
                hdlr = year
                years = [str(int(year)-1), str(year), str(int(year)+1)]
                ############KODI-RD-IL###################
                media_type = 'movie'
                added_seasonNum = ''
                #########################################
                
            results = self.get_sources(media_type, imdb, added_seasonNum)
            try: files = jsloads(results)['results']
            except: return sources
            undesirables = source_utils.get_undesirables()
            check_foreign_audio = source_utils.check_foreign_audio()
        except:
            source_utils.scraper_error('DMM')
            return sources

        results_count = 0
        for file in files:
            if results_count > 785: break
            try:
                hash = file['hash']
                name = source_utils.clean_name(file['title'])
                size = float(file['fileSize']) / (1024)
                
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

                sources_append({'provider': 'dmm', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info,
                                            'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': size})
                results_count += 1
            except:
                source_utils.scraper_error('DMM')
        return sources

    def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
        sources = []
        if not data: return sources
        sources_append = sources.append
        try:
            title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
            aliases = data['aliases']
            imdb = data['imdb']
            year = data['year']
            season = data['season']
            ############KODI-RD-IL###################
            media_type = 'tv'
            added_seasonNum = f"&seasonNum={str(season)}"
            results = self.get_sources(media_type, imdb, added_seasonNum)
            #########################################
            try: files = jsloads(results)['results']
            except: return sources
            undesirables = source_utils.get_undesirables()
            check_foreign_audio = source_utils.check_foreign_audio()
        except:
            source_utils.scraper_error('DMM')
            return sources

        results_count = 0
        for file in files:
            if results_count > 785: break
            try:
                hash = file['hash']
                name = source_utils.clean_name(file['title'])
                size = float(file['fileSize']) / (1024)
                
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

                item = {'provider': 'dmm', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
                            'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': size, 'package': package}
                if search_series: item.update({'last_season': last_season})
                elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
                sources_append(item)
                results_count += 1
            except:
                source_utils.scraper_error('DMM')
        return sources