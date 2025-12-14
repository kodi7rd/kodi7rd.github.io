import re
import json
import time
from threading import Thread
from indexers import metadata
from fenom import sources as fenom_sources
from windows import open_window, create_window
from scrapers import external, folders
from modules.debrid import import_debrid, resolve_external_sources, resolve_internal_sources, debrid_enabled, debrid_type_enabled, debrid_valid_hosts
from modules import player, kodi_utils, settings
from modules.source_utils import internal_sources, internal_folders_import, scraper_names, get_cache_expiry, pack_enable_check, normalize
from modules.utils import string_to_float, safe_string, remove_accents, get_datetime, adjust_premiered_date
#from modules.kodi_utils import logger

POVPlayer, progressDialogBG, notification = player.POVPlayer, kodi_utils.progressDialogBG, kodi_utils.notification
show_busy_dialog, hide_busy_dialog, close_all_dialog = kodi_utils.show_busy_dialog, kodi_utils.hide_busy_dialog, kodi_utils.close_all_dialog
get_property, set_property, clear_property = kodi_utils.get_property, kodi_utils.set_property, kodi_utils.clear_property
ls, monitor, sleep, get_setting = kodi_utils.local_string, kodi_utils.monitor, kodi_utils.sleep, kodi_utils.get_setting
check_prescrape_sources, quality_filter, sort_to_top = settings.check_prescrape_sources, settings.quality_filter, settings.sort_to_top
results_xml_style, results_xml_window_number = settings.results_xml_style, settings.results_xml_window_number
cloud_scrapers, folder_scrapers = ('rd_cloud', 'pm_cloud', 'ad_cloud', 'tb_cloud', 'oc_cloud'), ('folder1', 'folder2', 'folder3', 'folder4', 'folder5')
default_internal_scrapers = ('easynews', 'rd_cloud', 'pm_cloud', 'ad_cloud', 'tb_cloud', 'oc_cloud', 'folders')
default_hosters_providers = ('Real-Debrid', 'Premiumize.me', 'AllDebrid')
quality_ranks = {'4K': 1, '1080p': 2, '720p': 3, 'SD': 4, 'SCR': 5, 'CAM': 5, 'TELE': 5}
av1_filter_key, hevc_filter_key, hdr_filter_key, dolby_vision_filter_key = '[B]AV1[/B]', '[B]HEVC[/B]', '[B]HDR[/B]', '[B]D/VISION[/B]'
dialog_format, main_line = '[COLOR %s][B]%s[/B][/COLOR] 4K: %s | 1080p: %s | 720p: %s | SD: %s | Total: %s', '%s[CR]%s[CR]%s'
remaining_format, season_str, show_str, nextep_str, nores_str = ls(32676), ls(32537), ls(32089), ls(32801), ls(32760)

class SourceSelect:
	nextep_params = []

	@classmethod
	def nextep_callback(cls, params):
		if not isinstance(params, dict): return
		cls.nextep_params.insert(0, params)

	@classmethod
	def fromparams(cls, params):
		cls.nextep_callback(params)
		while cls.nextep_params:
			try: cls().playback_prep(cls.nextep_params.pop())
			except: pass

	def __init__(self):
		self.params = {}
		self.clear_properties, self.filters_ignored, self.active_folders = True, False, False
		self.threads, self.providers, self.sources, self.internal_scraper_names = [], [], [], []
		self.prescrape_scrapers, self.prescrape_threads, self.prescrape_sources = [], [], []
		self.remove_scrapers = ['external']# needs to be mutable so leave as list.
		self.exclude_list = ['easynews', 'library']# needs to be mutable so leave as list.
		self.sourcesTotal = self.sources4K = self.sources1080p = self.sources720p = self.sourcesSD = 0
		self.prescrape, self.disabled_ignored = 'true', 'false'
		self.language = settings.get_language()
		self.progress_dialog = None

	def playback_prep(self, params=None):
		if self.clear_properties: self._clear_properties()
		if params: self.params = params
		params_get = self.params.get
		self.prescrape = params_get('prescrape', self.prescrape) == 'true'
		self.background = params_get('background', 'false') == 'true'
		if self.background: hide_busy_dialog()
		else: show_busy_dialog()
		if 'autoplay' in self.params: self.autoplay = params_get('autoplay', 'false') == 'true'
		else: self.autoplay = settings.auto_play(params_get('media_type'))
		self.disabled_ignored = params_get('disabled_ignored', self.disabled_ignored) == 'true'
		self.ignore_scrape_filters = params_get('ignore_scrape_filters', 'false') == 'true'
		self.from_library = params_get('library', 'False') == 'True'
		self.media_type = params_get('media_type')
		self.tmdb_id = params_get('tmdb_id')
		self.season = int(params_get('season')) if 'season' in self.params else ''
		self.episode = int(params_get('episode')) if 'episode' in self.params else ''
		self.custom_title = params_get('custom_title')
		self.custom_year = params_get('custom_year')
		self.custom_season = int(params_get('custom_season')) if 'custom_season' in self.params else None
		self.custom_episode = int(params_get('custom_episode')) if 'custom_episode' in self.params else None
		self.ep_name = params_get('ep_name')
		self.plot = params_get('plot')
		self.active_internal_scrapers = settings.active_internal_scrapers()
		self.active_external = 'external' in self.active_internal_scrapers
		self.provider_sort_ranks = settings.provider_sort_ranks()
		self.sleep_time = settings.display_sleep_time()
		self.scraper_settings = settings.scraping_settings()
		self.include_prerelease_results = settings.include_prerelease_results()
		self.ignore_results_filter = settings.ignore_results_filter()
		self.filter_av1 = settings.filter_status('av1')
		self.filter_hevc = settings.filter_status('hevc')
		self.filter_hdr = settings.filter_status('hdr')
		self.filter_dv = settings.filter_status('dv')
		self.hybrid_allowed = self.filter_hdr in (0, 2)
		self.sort_function = settings.results_sort_order()
		self.display_uncached_torrents = settings.display_uncached_torrents()
		self.quality_filter = self._quality_filter()
		self.load_action = get_setting('load_action') == '1'
		self.size_filter = int(get_setting('results.size_filter', '0'))
		self.include_unknown_size = get_setting('results.include.unknown.size') == 'true'
		self.include_3D_results = get_setting('include_3d_results') == 'true'
		self.stingers = 'true' if get_setting('stingers.enable') == 'true' else 'false'
		if self.media_type == 'episode' and self.autoplay:
			self.autoplay_exclude_premieres = get_setting('autoplay_exclude_premieres') == 'true'
		else: self.autoplay_exclude_premieres = False
		if get_setting('results.language_filter') == 'true': self.priority_language = get_setting('results.language')
		else: self.priority_language = None
		if 'meta' in self.params: self.meta = json.loads(params_get('meta'))
		else: self.meta = self._get_meta()
		self._update_meta()
		self._search_info()
		set_property('pov_playback_meta', json.dumps(self.meta))
		self.get_sources()

	def get_sources(self):
		results = []
		start_time = time.monotonic()
		self.prepare_internal_scrapers()
		if any(x in self.active_internal_scrapers for x in default_internal_scrapers) and self.prescrape:
			results = self.collect_prescrape_results()
			if results: results = self.process_results(results)
		if not results:
			self.prescrape = False
			if self.active_external:
				self.activate_debrid_info()
				self.activate_external_providers()
			self.orig_results = self.collect_results()
			results = self.process_results(self.orig_results)
		self.meta['scrape_time'] = time.monotonic() - start_time
		if not results: return self._process_post_results()
		self.play_source(results)

	def collect_results(self):
		self.sources.extend(self.prescrape_sources)
		if self.active_folders: self.append_folder_scrapers(self.providers)
		self.providers.extend(internal_sources(self.active_internal_scrapers))
		if self.providers:
			threads = (Thread(target=self.activate_providers, args=(i[0], i[1], False), name=i[2]) for i in self.providers)
			self.threads.extend(threads)
			[i.start() for i in self.threads]
		if self.active_external or self.background:
			if self.active_external:
				self.external_args = (
					self.external_providers,
					self.debrid_torrent_enabled,
					self.debrid_hoster_enabled,
					self.internal_scraper_names,
					self.prescrape_sources,
					self.display_uncached_torrents,
					self.progress_dialog,
					self.disabled_ignored
				)
				self.activate_providers('external', external, False)
			if self.providers: [i.join() for i in self.threads]
		else: self.scrapers_dialog('internal')
		self._kill_progress_dialog()
		return self.sources

	def collect_prescrape_results(self):
		if self.active_folders:
			if self.autoplay or check_prescrape_sources('folders'):
				self.append_folder_scrapers(self.prescrape_scrapers)
				self.remove_scrapers.append('folders')
		self.prescrape_scrapers.extend(internal_sources(self.active_internal_scrapers, True))
		if not self.prescrape_scrapers: return []
		threads = (Thread(target=self.activate_providers, args=(i[0], i[1], True), name=i[2]) for i in self.prescrape_scrapers)
		self.prescrape_threads.extend(threads)
		[i.start() for i in self.prescrape_threads]
		self.remove_scrapers.extend(i[2] for i in self.prescrape_scrapers)
		if self.background: [i.join() for i in self.prescrape_threads]
		else: self.scrapers_dialog('pre_scrape')
		self._kill_progress_dialog()
		return self.prescrape_sources

	def process_results(self, results):
		if self.prescrape: self.all_scrapers = self.active_internal_scrapers
		else: self.all_scrapers = list(set(self.active_internal_scrapers + self.remove_scrapers))
		if self.ignore_scrape_filters:
			self.filters_ignored = True
			results = self.sort_results(results)
			results = self._sort_first(results)
		else:
			results = self.filter_results(results)
			results = self.sort_results(results)
			results = self._special_filter(results, hevc_filter_key, self.filter_hevc)
			results = self._special_filter(results, hdr_filter_key, self.filter_hdr)
			results = self._special_filter(results, dolby_vision_filter_key, self.filter_dv)
			results = self._special_filter(results, av1_filter_key, self.filter_av1)
			results = self._sort_first(results)
		return results

	def filter_results(self, results):
		results = [i for i in results if i['quality'] in self.quality_filter]
		if not self.include_3D_results: results = [i for i in results if not '3D' in i['extraInfo']]
		if not self.size_filter: return results
		if self.size_filter == 1:
			duration = self.meta['duration'] or (2400 if self.media_type == 'episode' else 5400)
			max_size = ((0.125 * (0.90 * string_to_float(get_setting('results.size.speed', '20'), '20'))) * duration)/1000
		if self.size_filter == 2:
			max_size = string_to_float(get_setting('results.size.file', '10000'), '10000') / 1000
		if self.include_unknown_size: results = [i for i in results if i['scrape_provider'].startswith('folder') or i['size'] <= max_size]
		else: results = [i for i in results if i['scrape_provider'].startswith('folder') or 0.01 < i['size'] <= max_size]
		return results

	def sort_results(self, results):
		for item in results:
			provider, quality = item['scrape_provider'], item.get('quality', 'SD')
			account_type = item['debrid'].lower() if provider == 'external' else provider.lower()
			item['provider_rank'] = self._get_provider_rank(account_type)
			item['quality_rank'] = self._get_quality_rank(quality)
		results.sort(key=self.sort_function)
		if self.priority_language: results = self._sort_language_to_top(results)
		results = self._sort_uncached_torrents(results)
		clear_property('fs_filterless_search')
		return results

	def prepare_internal_scrapers(self):
		if self.active_external and len(self.active_internal_scrapers) == 1: return
		active_internal_scrapers = [i for i in self.active_internal_scrapers if not i in self.remove_scrapers]
		self.active_folders = 'folders' in active_internal_scrapers
		if self.active_folders:
			self.folder_info = self.get_folderscraper_info()
			self.internal_scraper_names = [i for i in active_internal_scrapers if not i == 'folders'] + [i[0] for i in self.folder_info]
			self.active_internal_scrapers = active_internal_scrapers
		else:
			self.folder_info = []
			self.internal_scraper_names = active_internal_scrapers[:]
			self.active_internal_scrapers = active_internal_scrapers

	def activate_providers(self, module_type, function, prescrape):
		sources = self._get_module(module_type, function).results(self.search_info)
		if not sources: return
		if prescrape: self.prescrape_sources.extend(sources)
		else: self.sources.extend(sources)

	def activate_debrid_info(self):
		self.debrid_enabled = debrid_enabled()
		self.debrid_torrent_enabled = debrid_type_enabled('torrent', self.debrid_enabled)
		self.debrid_hoster_enabled = debrid_valid_hosts(debrid_type_enabled('hoster', self.debrid_enabled))

	def activate_external_providers(self):
		if not self.debrid_torrent_enabled and not self.debrid_hoster_enabled:
			self._kill_progress_dialog()
			if len(self.active_internal_scrapers) == 1 and 'external' in self.active_internal_scrapers: notification(32854, 2000)
			self.active_external = False
		else:
			if not self.debrid_torrent_enabled: self.exclude_list.extend(scraper_names('torrents'))
			elif not self.debrid_hoster_enabled: self.exclude_list.extend(scraper_names('hosters'))
			external_providers = fenom_sources(ret_all=self.disabled_ignored)
			self.external_providers = [i for i in external_providers if not i[0] in self.exclude_list]
			if not self.season: return
			season_packs, show_packs = pack_enable_check(self.meta, self.season, self.episode)
			if not season_packs: return
			self.external_providers = [(i[0], i[1], '') for i in self.external_providers]
			pack_capable = [i for i in self.external_providers if i[1].pack_capable]
			if pack_capable:
				self.external_providers.extend([(i[0], i[1], season_str) for i in pack_capable])
			if pack_capable and show_packs:
				self.external_providers.extend([(i[0], i[1], show_str) for i in pack_capable])

	def play_source(self, results):
		if self.background: return self.play_execute_background(results)
		if self.autoplay: return self.play_file(results, autoplay=True)
		return self.display_results(results)

	def append_folder_scrapers(self, current_list):
		current_list.extend(internal_folders_import(self.folder_info))

	def get_folderscraper_info(self):
		folder_info = [(get_setting('%s.display_name' % i), i) for i in folder_scrapers]
		return [i for i in folder_info if not i[0] in (None, 'None', '')]

	def scrapers_dialog(self, scrape_type):
		def _scraperDialog():
			if not self.progress_dialog: self._make_progress_dialog()
			while not self.progress_dialog.iscanceled() or monitor.abortRequested():
				try:
					remaining_providers = [x.name for x in _threads if x.is_alive() is True]
					self._process_internal_results()
					s4k_label, s1080_label = total_format % self.sources4K, total_format % self.sources1080p
					s720_label, ssd_label, stotal_label = total_format % self.sources720p, total_format % self.sourcesSD, total_format % self.sourcesTotal
					try:
						current_time = time.monotonic()
						current_progress = current_time - start_time
						line2 = dialog_format % (int_dialog_hl, line2_inst, s4k_label, s1080_label, s720_label, ssd_label, stotal_label)
						line3 = remaining_format % ', '.join(remaining_providers).upper()
						percent = int((current_progress/float(timeout))*100)
						self.progress_dialog.update(main_line % (line1, line2, line3), percent)
						sleep(self.sleep_time)
						if len(remaining_providers) == 0: break
						if percent >= 100: break
					except: pass
				except: pass
		if scrape_type == 'internal': scraper_list, _threads, line1_inst, line2_inst = self.providers, self.threads, ls(32096), 'Int:'
		else: scraper_list, _threads, line1_inst, line2_inst = self.prescrape_scrapers, self.prescrape_threads, ' '.join([ls(32829), ls(32830)]), 'Pre:'
		self.internal_scrapers = self._get_active_scraper_names(scraper_list)
		if not self.internal_scrapers: return
		timeout = 25
		int_dialog_hl = get_setting('int_dialog_highlight') or 'dodgerblue'
		total_format = '[COLOR %s][B]%s[/B][/COLOR]' % (int_dialog_hl, '%s')
		line1 = '[COLOR %s][B]%s[/B][/COLOR]' % (int_dialog_hl, line1_inst)
		start_time = time.monotonic()
		end_time = start_time + timeout
		_scraperDialog()

	def display_results(self, results):
		window_style = results_xml_style()
		chosen_item = open_window(
			('windows.sources', 'SourceResults'),
			'sources_results.xml',
			window_style=window_style,
			window_id=results_xml_window_number(window_style),
			results=results,
			meta=self.meta,
			scraper_settings=self.scraper_settings,
			prescrape=self.prescrape,
			filters_ignored=self.filters_ignored
		)
		if not chosen_item: return self._kill_progress_dialog()
		action, chosen_item = chosen_item
		if action == 'play':
			self._kill_progress_dialog()
			return self.play_file(results, chosen_item)
		if action == 'perform_full_search' and self.prescrape:
			self.prescrape, self.clear_properties = False, False
			return self.playback_prep()

	def play_execute_background(self, results):
		background_url = self.play_file(results, autoplay=True, background=True)
		set_property('pov_background_url', background_url)

	def _get_active_scraper_names(self, scraper_list):
		return [i[2] for i in scraper_list]

	def _process_post_results(self):
		if self.ignore_results_filter and self.orig_results: return self._process_ignore_filters()
		return self._no_results()

	def _process_ignore_filters(self):
		if self.autoplay: notification(32686)
		self.autoplay = False
		self.filters_ignored = True
		results = self.sort_results(self.orig_results)
		results = self._sort_first(results)
		return self.play_source(results)

	def _no_results(self):
		hide_busy_dialog()
		if self.background: return notification('%s %s' % (nextep_str, nores_str), 5000)
		notification(32760, 2000)

	def _update_meta(self):
		if self.from_library: self.meta.update({'from_library': self.from_library, 'ep_name': self.ep_name, 'plot': self.plot or self.meta.get('plot')})
		self.meta.update({'media_type': self.media_type, 'season': self.season, 'episode': self.episode, 'stingers': self.stingers, 'background': self.background})
		if self.custom_title: self.meta['custom_title'] = self.custom_title
		if self.custom_year: self.meta['custom_year'] = self.custom_year

	def _search_info(self):
		title = metadata.get_title(self.meta, self.language)
		aliases = self._make_alias_dict(title, self.meta)
		year = self._get_search_year(self.meta)
		ep_name = self._get_ep_name(self.meta)
		expiry_times = get_cache_expiry(self.media_type, self.meta, self.season)
		self.search_info = {
			'media_type': self.media_type, 'tmdb_id': self.tmdb_id, 'imdb_id': self.meta.get('imdb_id'), 'tvdb_id': self.meta.get('tvdb_id'),
			'title': title, 'year': year, 'aliases': aliases, 'expiry_times': expiry_times, 'total_seasons': self.meta.get('total_seasons', ''),
			'ep_name': ep_name, 'season': self.custom_season or self.season, 'episode': self.custom_episode or self.episode
		}

	def _get_search_year(self, meta):
		if 'custom_year' in meta: return meta['custom_year']
		year = meta.get('year') or '0'
		if self.active_external and get_setting('search.enable.yearcheck', 'false') == 'true':
			from indexers.imdb_api import imdb_movie_year
			try: year = str(imdb_movie_year(meta.get('imdb_id')) or year)
			except: pass
		return year

	def _get_ep_name(self, meta):
		if self.media_type == 'episode':
			ep_name = meta.get('ep_name')
			try: ep_name = safe_string(remove_accents(ep_name))
			except: ep_name = safe_string(ep_name)
		else: ep_name = None
		return ep_name

	def _make_alias_dict(self, title, meta):
		aliases = []
		meta_title = meta['title']
		original_title = meta['original_title']
		alternative_titles = meta.get('alternative_titles', [])
		country_codes = set([i.replace('GB', 'UK') for i in meta.get('country_codes', [])])
		if meta_title not in alternative_titles: alternative_titles.append(meta_title)
		if original_title not in alternative_titles: alternative_titles.append(original_title)
		if alternative_titles: aliases = [{'title': i, 'country': ''} for i in alternative_titles]
		if country_codes: aliases.extend([{'title': '%s %s' % (title, i), 'country': ''} for i in country_codes])
		normalized = ({'title': normalize(i['title']), 'country': i['country']} for i in aliases)
		aliases.extend(i for i in normalized if not i in aliases)
		return aliases

	def _process_internal_results(self):
		for i in self.internal_scrapers:
			win_property = get_property('%s.internal_results' % i)
			if win_property in ('checked', '', None): continue
			try: sources = json.loads(win_property)
			except: continue
			set_property('%s.internal_results' % i, 'checked')
			self._sources_quality_count(sources)

	def _sources_quality_count(self, sources):
		for i in sources:
			quality = i['quality']
			if quality == '4K': self.sources4K += 1
			elif quality in ('1440p', '1080p'): self.sources1080p += 1
			elif quality in ('720p', 'HD'): self.sources720p += 1
			else: self.sourcesSD += 1
			self.sourcesTotal += 1

	def _quality_filter(self):
		setting = 'results_quality_%s' % self.media_type if not self.autoplay else 'autoplay_quality_%s' % self.media_type
		filter_list = quality_filter(setting)
		if self.include_prerelease_results and 'SD' in filter_list: filter_list += ['SCR', 'CAM', 'TELE']
		return filter_list

	def _get_quality_rank(self, quality):
		return quality_ranks[quality]

	def _get_provider_rank(self, account_type):
		return self.provider_sort_ranks[account_type] or 11

	def _sort_first(self, results):
		try:
			sort_first_scrapers = []
			if 'folders' in self.all_scrapers and sort_to_top('folders'): sort_first_scrapers.append('folders')
			sort_first_scrapers.extend([i for i in self.all_scrapers if i in cloud_scrapers and sort_to_top(i)])
			if not sort_first_scrapers: return results
			sort_first = [i for i in results if i['scrape_provider'] in sort_first_scrapers]
			sort_first.sort(key=lambda k: (self._sort_folder_to_top(k['scrape_provider']), k['quality_rank']))
			sort_last = [i for i in results if not i in sort_first]
			results = sort_first + sort_last
		except: pass
		return results

	def _sort_folder_to_top(self, provider):
		if provider == 'folders': return 0
		else: return 1

	def _sort_language_to_top(self, results):
		from xbmc import convertLanguage as cl, ISO_639_1, ISO_639_2
		try:
			language = self.priority_language, cl(self.priority_language, ISO_639_2), cl(self.priority_language, ISO_639_1)
			if self.priority_language == 'Spanish': language += 'latino', 'lat', 'esp'
			pattern = r'\b(%s)\b' % '|'.join(i for i in language if i)
			sort_first = [i for i in results if re.search(pattern, i.get('name_info', ''), re.I)]
			sort_last = [i for i in results if not i in sort_first]
			results = sort_first + sort_last
		except: pass
		return results

	def _sort_uncached_torrents(self, results):
		results.sort(key=lambda k: 'Unchecked' in k.get('cache_provider', ''), reverse=False)
		if self.display_uncached_torrents or get_property('fs_filterless_search') == 'true':
			results.sort(key=lambda k: 'Uncached' in k.get('cache_provider', ''), reverse=False)
			return results
#		uncached = [i for i in results if 'Uncached' in i.get('cache_provider', '')]
#		cached = [i for i in results if not i in uncached]
#		return cached + uncached
		return [i for i in results if not 'Uncached' in i.get('cache_provider', '')]

	def _special_filter(self, results, key, enable_setting):
		if enable_setting == 1:
			if key == dolby_vision_filter_key and self.hybrid_allowed:
				results = [i for i in results if all(x in i['extraInfo'] for x in (key, hdr_filter_key)) or not key in i['extraInfo']]
			else: results = [i for i in results if not key in i['extraInfo']]
		elif enable_setting == 2 and self.autoplay:
			priority_list = [i for i in results if key in i['extraInfo']]
			remainder_list = [i for i in results if not i in priority_list]
			results = priority_list + remainder_list
		elif enable_setting == 3:
			priority_list = lambda k: key in k['extraInfo'] and not 'Uncached' in k.get('cache_provider', '')
			results.sort(key=priority_list, reverse=True)
		return results

	def _get_meta(self):
		meta_user_info, adjust_hours, current_date = settings.metadata_user_info(), settings.date_offset(), get_datetime()
		if self.media_type == 'episode':
			meta = metadata.tvshow_meta('tmdb_id', self.tmdb_id, meta_user_info, current_date)
			try:
				episodes_data = metadata.season_episodes_meta(self.season, meta, meta_user_info)
				ep_data = [i for i in episodes_data if i['episode'] == int(self.episode)][0]
				meta.update({
					'media_type': 'episode', 'season': ep_data['season'], 'episode': ep_data['episode'],
					'premiered': ep_data['premiered'], 'ep_name': ep_data['title'], 'plot': ep_data['plot']
				})
				if self.custom_season and self.custom_episode: meta.update({'custom_season': self.custom_season, 'custom_episode': self.custom_episode})
				if self.background or any(i in meta for i in ('random', 'random_continual')): return meta
				if self.autoplay_exclude_premieres and int(self.episode) == 1 and all(
					current_date >= adjust_premiered_date(i['premiered'], adjust_hours)[0] if 'premiered' in i and i['premiered'] else False
					for i in episodes_data
				): self.autoplay = False
			except: pass
		else: meta = metadata.movie_meta('tmdb_id', self.tmdb_id, meta_user_info, current_date)
		return meta

	def _get_module(self, module_type, function):
		if module_type == 'external': module = function.External(*self.external_args)
		elif module_type == 'folders': module = function[0](*function[1])
		else: module = function()
		return module

	def _clear_properties(self):
		for item in default_internal_scrapers: clear_property('%s.internal_results' % item)
		for item in self.get_folderscraper_info(): clear_property('%s.internal_results' % item[0])

	def _make_progress_dialog(self):
		self.progress_dialog = create_window(('windows.sources', 'ProgressMedia'), 'progress_media.xml', meta=self.meta)
		Thread(target=self.progress_dialog.run).start()

	def _kill_progress_dialog(self):
		try: self.progress_dialog.close()
		except: close_all_dialog()
		try: del self.progress_dialog
		except: pass
		self.progress_dialog = None

	def play_file(self, results, source=None, autoplay=False, background=False):
		def _process():
			for count, item in enumerate(items, 1):
				if not background:
					try:
						if monitor.abortRequested(): break
						elif self.progress_dialog and self.progress_dialog.iscanceled(): break
						percent = int(((total_items := len(items))-count)/total_items*100)
						name = item['name'].replace('.', ' ').replace('-', ' ').upper()
						line1 = item.get('scrape_provider'), item.get('cache_provider'), item.get('provider')
						line1 = ' | '.join(i for i in line1 if i and i != 'external').upper()
						line2 = ' | '.join(i for i in (item.get('size_label', ''), item.get('extraInfo', '')) if i)
						if self.progress_dialog: self.progress_dialog.update(main_line % (line1, line2, name), percent)
						else: progressDialogBG.update(percent, name)
					except: pass
				link = self.resolve_sources(item, self.meta)
				if not link is None: yield link
		try:
			self._kill_progress_dialog()
			if autoplay:
				items = [i for i in results if not 'Uncached' in i.get('cache_provider', '')]
				if self.filters_ignored: notification(32686)
			else:
				source_index = results.index(source) if source in results else -1
				items = [i for i in results[source_index + 1:] if not 'Uncached' in i.get('cache_provider', '')][:40]
				items.insert(0, source)
			if background: return 'true' if items else 'false'
			if not self.load_action:
				progressDialogBG.create('POV', 'POV loading...')
				progress_media = None
			else:
				self._make_progress_dialog()
				progress_media = self._kill_progress_dialog
			url = next(_process(), None)
			if not self.load_action: progressDialogBG.close()
			if not url: self._kill_progress_dialog()
			return POVPlayer().run(url, progress_media)
		except: pass

	def resolve_sources(self, item, meta):
		try:
			if item.get('scrape_provider') in ('external',):
				if meta['media_type'] == 'episode':
					title = meta.get('ep_name') or str(self.ep_name)
					season = meta.get('custom_season') or meta.get('season')
					episode = meta.get('custom_episode') or meta.get('episode')
				else: title, season, episode = metadata.get_title(meta, self.language), None, None
				if not item['url'].startswith('magnet'):
					store_to_cloud = settings.store_resolved_usenet_to_cloud(item['debrid'])
					api = import_debrid(item['debrid'])
					return api.resolve_nzb(item['url'], item['hash'], store_to_cloud, title, season, episode)
				store_to_cloud = settings.store_resolved_torrent_to_cloud(item['debrid'])
				return resolve_external_sources(item, store_to_cloud, title, season, episode)
			if item.get('scrape_provider') in default_internal_scrapers:
				return resolve_internal_sources(
					item['scrape_provider'], item['id'], item['url_dl'], item.get('direct_debrid_link', False)
				)
			if item.get('debrid') in default_hosters_providers and not item['source'].lower() == 'torrent':
				api = import_debrid(item['debrid'])
				return api.unrestrict_link(item['url'])
			return item['url']
		except: pass

