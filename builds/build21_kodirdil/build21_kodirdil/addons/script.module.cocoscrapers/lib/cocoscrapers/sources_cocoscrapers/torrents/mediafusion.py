# created by Venom for Fenomscrapers (updated 3-02-2022) modified by umbrella_dev 10-8-24
"""
	Cocoscrapers Project
"""

from json import dumps as jsdumps
import base64, re, requests
from cocoscrapers.modules import source_utils, cache
from cocoscrapers.modules.control import homeWindow, sleep
from cocoscrapers.modules import log_utils
session = requests.Session()


class source:
	priority = 2
	pack_capable = True
	hasMovies = True
	hasEpisodes = True
	def __init__(self):
		self.language = ['en']
		#self.base_link = 'https://mediafusion.elfhosted.com'
		self.manifest = '/eJwB8AEP_vTC0-41NtYccYs7wZ6l1qeUToHNnQsAey_kuyGCAppcyY1b_JgPiJL_zMEUp8S1FLMb55AUklkc4UG8frNbiX2UfYRzFX4uwFcJaaj3nTmJp4chEvKy2QRhVuo2CZ36tLh9p7EhN0GIA-vW-WFRrarkaklb6xn9mdL4GtBI8PkWsF1hYuX5mW492hZHV6CjIFkUiik4i8IYTkW3oGZnfl-0p7p4GExfDnvbCBONdHuj6M_N5cqwbQD1SiU5VZ6n_h2ABOpGRytAcjzj86RkTGFvcO-flBrkQURCMh3Bl01MDO--B0Bo9DKFBgtdEww13nlI2seJp3OoTUwOc2JAqyYM_IBMKkJCyROvXrfHG-mQ_5kAqHIawgHkQU3F9GgotHbX9g8FaCFWyNR0psNTfJfNAmdSqpXWKlfAvxdwLGIK-rWxKayDCFOD0oAMQYVCG7Km43PYGXRHktz4zeeSOY34q7shmHHV3_XIgb0X04Bf4DQuo25kbawU8ez6kuu_0niSK0gfZh3HgEl6SyM70aEme91EEgu4cyKp5ateGwgRMz9ZmGAmVLYP6uKwF_XXJS6xalaY-R9X6ukUjkAquj-zTTM-VCRa8bF0_m8QZoXlupIq1U4gVDvdRCFqsyVJPX_Q_PoK-TvNYF2eMZY2CMXo8vCt'
		self.base_link = 'https://mediafusion.elfhosted.com'+self.manifest
		self.movieSearch_link = '/stream/movie/%s.json'
		self.tvSearch_link = '/stream/series/%s:%s:%s.json'
		self.min_seeders = 0
# Currently supports BITSEARCH(+), EZTV(+), ThePirateBay(+), TheRARBG(+), YTS(+)

	def _get_files(self, url):
		if self.get_pack_files: return []
		results = session.get(url, timeout=10)
		files = results.json()['streams']
		return files

	def sources(self, data, hostDict):
		self.get_pack_files = False
		sources = []
		if not data:
			homeWindow.clearProperty('cocoscrapers.mediafusion.performing_single_scrape')
			return sources
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
				homeWindow.setProperty('cocoscrapers.mediafusion.performing_single_scrape', 'true')
				season = data['season']
				episode = data['episode']
				hdlr = 'S%02dE%02d' % (int(season), int(episode))
				url = '%s%s' % (self.base_link, self.tvSearch_link % (imdb, season, episode))
				files = cache.get(self._get_files, 10, url)
			else:
				url = '%s%s' % (self.base_link, self.movieSearch_link % (imdb))
				hdlr = year
				files = self._get_files(url)
			log_utils.log('mediafusion sources url = %s' % url)
			homeWindow.clearProperty('cocoscrapers.mediafusion.performing_single_scrape')
			_INFO = re.compile(r'💾.*')
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			homeWindow.clearProperty('cocoscrapers.mediafusion.performing_single_scrape')
			source_utils.scraper_error('MEDIAFUSION')
			return sources
		for file in files:
			try:
				if 'tvshowtitle' in data:
					hash = file['url'].split('info_hash=')[1]
					hash = hash.split('&season=')[0]
				else:
					hash = file['url'].split('info_hash=')[1]
				log_utils.log('mediafusion hash: %s' % hash)
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

				append({'provider': 'mediafusion', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
							'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			except:
				homeWindow.clearProperty('cocoscrapers.mediafusion.performing_single_scrape')
				source_utils.scraper_error('MEDIAFUSION')
		return sources

	def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
		self.get_pack_files = True
		sources = []
		if not data: return sources
		count, finished_single_scrape = 0, False
		sleep(2000)
		while count < 10000 and not finished_single_scrape:
			finished_single_scrape = homeWindow.getProperty('cocoscrapers.mediafusion.performing_single_scrape') != 'true'
			sleep(100)
			count += 100
		if not finished_single_scrape: return sources
		sleep(1000)
		sources_append = sources.append
		try:
			title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
			aliases = data['aliases']
			imdb = data['imdb']
			year = data['year']
			season = data['season']
			url = '%s%s' % (self.base_link, self.tvSearch_link % (imdb, season, data['episode']))
			files = cache.get(self._get_files, 10, url)
			_INFO = re.compile(r'💾.*') # _INFO = re.compile(r'👤.*')
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			source_utils.scraper_error('MEDIAFUSION')
			return sources
		log_title = 'Series' if search_series else 'Season'
		for file in files:
			try:
				file['url'].split('info_hash=')[1]
				file_title = file['description']
				file_info = [x for x in file['title'].split('\n') if _INFO.match(x)][0]

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

				item = {'provider': 'mediafusion', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
							'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': package}
				if search_series: item.update({'last_season': last_season})
				elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
				sources_append(item)
			except:
				source_utils.scraper_error('MEDIAFUSION')
		return sources

