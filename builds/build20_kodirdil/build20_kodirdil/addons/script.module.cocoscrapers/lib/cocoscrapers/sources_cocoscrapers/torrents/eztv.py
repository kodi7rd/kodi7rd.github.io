# -*- coding: utf-8 -*-
# modified by CocoJoe for CocoScrapers (updated 12-12-2023)
"""
	CocoScrapers Project
"""

from math import ceil
from json import loads as jsloads
import re
from urllib.parse import quote_plus, unquote_plus
from cocoscrapers.modules import client
from cocoscrapers.modules import source_utils
from cocoscrapers.modules import workers

class source:
	priority = 6
	pack_capable = False
	hasMovies = False
	hasEpisodes = True
	def __init__(self):
		self.language = ['en']
		self.base_link = 'https://eztvx.to/api/get-torrents?imdb_id=%s&limit=100&page=%s'
		self.min_seeders = 0
		self.results = []

	def get_extra_pages(self, url):
		result = client.request(url, timeout=5)
		try:
			files = jsloads(result)['torrents']
			self.results.extend(files)
		except: return

	def sources(self, data, hostDict):
		sources = []
		if not data: return sources
		sources_append = sources.append
		try:
			title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
			aliases = data['aliases']
			episode_title = data['title']
			year = data['year']
			imdb = data['imdb'].replace('tt', '')
			season = data['season']
			episode = data['episode']
			hdlr = 'S%02dE%02d' % (int(season), int(episode))

			base_url = self.base_link % (imdb, '%s')

			result = client.request(base_url % 1, timeout=5)
			try: result = jsloads(result)
			except: return sources
			self.results.extend(result['torrents'])

			total_pages = ceil(result['torrents_count']/float(result['limit']))
			if total_pages > 1:
				threads = []
				append = threads.append
				all_pages = range(2, total_pages + 1)
				for page_no in all_pages:
					append(workers.Thread(self.get_extra_pages, base_url % page_no))
				[i.start() for i in threads]
				[i.join() for i in threads]
			
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		
		except:
			source_utils.scraper_error('EZTV')
			return sources

		for file in self.results:
			try:
				hash = file['hash']
				if len(hash) != 40: # eztv has some base32 encoded hashes
					hash = source_utils.base32_to_hex(hash, 'EZTV')
				
				name = file['filename']
				name = source_utils.clean_name(name)
				
				url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)

				if not source_utils.check_title(title, aliases, name, hdlr, year): continue
				name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
				if source_utils.remove_lang(name_info, check_foreign_audio): continue
				if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

				seeders = file['seeds']

				quality, info = source_utils.get_release_quality(name_info, url)

				size = '%sgb' % round(float(file['size_bytes'])/1073741824, 2)
				try:
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)
				
				sources_append({'provider': 'eztv', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
								'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			
			except:
				source_utils.scraper_error('EZTV')
		return sources
