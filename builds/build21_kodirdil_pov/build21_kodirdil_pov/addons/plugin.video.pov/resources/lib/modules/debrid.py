import re
import json
import random
import requests
from threading import Thread
from debrids import alldebrid_api, premiumize_api, real_debrid_api, torbox_api, offcloud_api, easydebrid_api
from caches.debrid_cache import DebridCache
from modules.utils import clean_file_name, make_thread_list
from modules.settings import enabled_debrids_check
from modules import kodi_utils
# from modules.kodi_utils import logger

ls, get_setting, notification = kodi_utils.local_string, kodi_utils.get_setting, kodi_utils.notification
show_busy_dialog, hide_busy_dialog = kodi_utils.show_busy_dialog, kodi_utils.hide_busy_dialog
ok_dialog, confirm_dialog, select_dialog = kodi_utils.ok_dialog, kodi_utils.confirm_dialog, kodi_utils.select_dialog
plswait_str, checking_debrid_str, remaining_debrid_str = ls(32577), ls(32578), ls(32579)

debrid_list = (
	('Real-Debrid', 'rd', real_debrid_api.RealDebridAPI),
	('Premiumize.me', 'pm', premiumize_api.PremiumizeAPI),
	('AllDebrid', 'ad', alldebrid_api.AllDebridAPI),
	('TorBox', 'tb', torbox_api.TorBoxAPI),
	('Offcloud', 'oc', offcloud_api.OffcloudAPI),
	('EasyDebrid', 'ed', easydebrid_api.EasyDebridAPI)
)

def import_debrid(debrid_provider):
	cls = next((i[2] for i in debrid_list if i[0] == debrid_provider), None)
	return cls() if cls else cls

def debrid_enabled():
	return [i[0] for i in debrid_list if enabled_debrids_check(i[1])]

def debrid_type_enabled(debrid_type, enabled_debrids):
	return [i[0] for i in debrid_list if i[0] in enabled_debrids and get_setting('%s.%s.enabled' % (i[1], debrid_type)) == 'true']

def debrid_valid_hosts(enabled_debrids):
	def _get_hosts(api):
		debrid_hosts_append(api.get_hosts())
	if not enabled_debrids: return []
	debrid_hosts = []
	debrid_hosts_append = debrid_hosts.append
	debrids = (import_debrid(i[0]) for i in debrid_list if i[0] in enabled_debrids)
	threads = list(make_thread_list(_get_hosts, debrids, Thread))
	[i.join() for i in threads]
	return debrid_hosts

def unchecked_magnet_status(params):
	params['provider'] = params['provider'].replace('Unchecked ', '').replace('Uncached ', '')
	show_busy_dialog()
	api = import_debrid(params['provider'])
	result = api.parse_magnet_pack(params['url'], params['info_hash'])
	hide_busy_dialog()
	if not result: return ok_dialog(text='%s Not Cached' % params['provider'], top_space=True)
	torrent_id = next((i['torrent_id'] for i in result if 'torrent_id' in i), None)
	if torrent_id: Thread(target=api.delete_torrent, args=(torrent_id,)).start()
	ok_dialog(text='%s Cached' % params['provider'], top_space=True)

def manual_add_nzb_to_cloud(params):
	params['provider'] = params['provider'].replace('Unchecked ', '').replace('Uncached ', '')
	if not confirm_dialog(text=ls(32831) % params['provider'].upper()): return
	show_busy_dialog()
	api = import_debrid(params['provider'])
	api.clear_cache()
	result = api.create_transfer(params['url'], params['name'])
	hide_busy_dialog()
	if result: notification(32576)
	else: notification(32575)

def manual_add_magnet_to_cloud(params):
	params['provider'] = params['provider'].replace('Unchecked ', '').replace('Uncached ', '')
	if not confirm_dialog(text=ls(32831) % params['provider'].upper()): return
	show_busy_dialog()
	api = import_debrid(params['provider'])
	api.clear_cache()
	result = api.create_transfer(params['url'])
	hide_busy_dialog()
	if result: notification(32576)
	else: notification(32575)

def resolve_internal_sources(scrape_provider, item_id, url_dl, direct_debrid_link=False):
	try:
		if scrape_provider == 'easynews':
			from debrids.easynews import resolve_easynews
			url = resolve_easynews({'url_dl': url_dl, 'play': 'false'})
		elif scrape_provider == 'rd_cloud':
			if direct_debrid_link: url = url_dl
			else: url = real_debrid_api.RealDebridAPI().unrestrict_link(item_id)
		elif scrape_provider == 'pm_cloud':
			details = premiumize_api.PremiumizeAPI().get_item_details(item_id)
			url = details['link']
			if url.startswith('/'): url = 'https' + url
		elif scrape_provider == 'ad_cloud':
			if direct_debrid_link: url = url_dl
			else: url = alldebrid_api.AllDebridAPI().unrestrict_link(item_id)
		elif scrape_provider == 'tb_cloud':
			if direct_debrid_link == 'usenet': function = 'unrestrict_usenet'
			elif direct_debrid_link == 'webdl': function = 'unrestrict_webdl'
			else: function = 'unrestrict_link'
			function = getattr(torbox_api.TorBoxAPI(), function)
			url = function(item_id)
		elif scrape_provider == 'folders':
			if url_dl.endswith('.strm'):
				with kodi_utils.open_file(url_dl) as f: url = f.read()
			else: url = url_dl
		else: url = url_dl
		return url
	except Exception as e:
		kodi_utils.logger('resolve_internal_sources exception', str(e))

def resolve_external_sources(source, store_to_cloud, title, season, episode):
	from modules.source_utils import supported_video_extensions, seas_ep_filter, extras_filter
	try:
		extensions = supported_video_extensions()
		extras_filtering_list = tuple(i for i in extras_filter() if not i in title.lower())
		if source['debrid'] in ('Real-Debrid', 'AllDebrid'): args = source['url'], source['hash'], True
		else: args = source['url'], source['hash']
		api = import_debrid(source['debrid'])
		files = api.parse_magnet_pack(*args)
		selected_files = []
		selected_files_append = selected_files.append
		for i in files or selected_files:
			torrent_id, filename = i.get('torrent_id'), i['filename'].lower()
			if filename.endswith('.m2ts'): raise Exception('_m2ts_check failed')
			if not filename.endswith(tuple(extensions)): continue
			if season and not seas_ep_filter(season, episode, filename): continue
			elif any(x in filename for x in extras_filtering_list): continue
			selected_files_append(i)
		if not selected_files: raise Exception('selected_files failed')
		if not season: selected_files.sort(key=lambda k: k['size'], reverse=True)
		file_key = next((i['link'] for i in selected_files), None)
		if source['debrid'] in ('Premiumize.me',): file_url = api.add_headers_to_url(file_key)
		else: file_url = api.unrestrict_link(file_key)
		if source['debrid'] in ('Premiumize.me',):
			if store_to_cloud: Thread(target=api.create_transfer, args=(source['url'],)).start()
		if source['debrid'] in ('Real-Debrid', 'AllDebrid', 'TorBox'):
			if not store_to_cloud: Thread(target=api.delete_torrent, args=(torrent_id,)).start()
		return file_url
	except Exception as e:
		kodi_utils.logger('resolve_external_sources exception', f"{e}\n{json.dumps(source, indent=2)}")
		if files and torrent_id: Thread(target=api.delete_torrent, args=(torrent_id,)).start()

def debrid_packs(debrid_provider, name, magnet_url, info_hash, highlight=None, download=False):
	debrid_provider = debrid_provider.replace('Unchecked ', '')
	show_busy_dialog()
	api = import_debrid(debrid_provider)
	pack_choices = api.parse_magnet_pack(magnet_url, info_hash)
	hide_busy_dialog()
	if not pack_choices: return None if download else notification(32574)
	pack_choices.sort(key=lambda k: k['filename'].lower())
	icon = kodi_utils.media_path(api.icon)
	for item in pack_choices: item.update({
		'icon': icon,
		'line1': clean_file_name(item['filename']),
		'line2': '%s: %.2f GB' % (ls(32584), float(item['size'])/1073741824)
	})
	if download: return pack_choices
	kwargs = {'enumerate': 'true', 'multi_line': 'true'}
	kwargs.update({'items': json.dumps(pack_choices), 'heading': name, 'highlight': highlight})
	chosen_result = select_dialog(pack_choices, **kwargs)
	if chosen_result is None: return
	url_dl = chosen_result['link']
	if debrid_provider == 'Premiumize.me': link = api.add_headers_to_url(url_dl)
	else: link = api.unrestrict_link(url_dl)
	url_params = {'mode': 'media_play', 'url': link, 'media_type': 'video'}
	return kodi_utils.execute_builtin('RunPlugin(%s)' % kodi_utils.build_url(url_params))

def mfn_check_cache(imdb, season, episode, collector):
	if str(season).isdigit(): url = 'series/%s:%s:%s.json' % (imdb, season, episode)
	else: url = 'movie/%s.json' % (imdb)
	params = (
		'D-T2iZoymNCCD1T5c2sX5u8tIZVcgcFWlCsCJ72rCmrU2mDdmvgieM-lvX-bp4h_ExG1IpHLObtgmLCC'
		'k_QbhNTZz32wbhNmYO1HLaefzqGoYjcIhiUH-MWgL-dMxyrTPR2fo2--HtvH0V5KpEi6vPfjKKGBmpe3'
		'wRD0c_QsSxlcQ'
	)
	url = 'https://mediafusion.elfhosted.com/%s/stream/%s' % (params, url)
	pattern = re.compile(r'\b\w{40}\b')
	try:
		results = requests.get(url, timeout=7.05)
		files = results.json()['streams']
		collector.extend(pattern.findall(file['url'])[-1] for file in files if '⚡' in file['name'] and 'url' in file)
	except Exception as e: kodi_utils.logger('mfn error', str(e))

def trz_check_cache(imdb, season, episode, collector):
	if str(season).isdigit(): url = 'series/%s:%s:%s.json' % (imdb, season, episode)
	else: url = 'movie/%s.json' % (imdb)
	params = 'eyJzdG9yZXMiOlt7ImMiOiJhZCIsInQiOiJzdGF0aWNEZW1vQXBpa2V5UHJlbSJ9XSwiY2FjaGVkIjp0cnVlfQ=='
	url = 'https://stremthru.elfhosted.com/stremio/torz/%s/stream/%s' % (params, url)
	pattern = re.compile(r'\b\w{40}\b')
	try:
		results = requests.get(url, timeout=7.05)
		files = results.json()['streams']
		collector.extend(pattern.findall(file['url'])[-1] for file in files if '⚡' in file['name'] and 'url' in file)
	except Exception as e: kodi_utils.logger('tor error', str(e))

def tio_check_cache(imdb, season, episode, collector):
	from fenom import client
	if str(season).isdigit(): url = 'series/%s:%s:%s.json' % (imdb, season, episode)
	else: url = 'movie/%s.json' % (imdb)
	params = 'debridoptions=nodownloadlinks,nocatalog|realdebrid=T2iZoymNCCD1T5c2sX5u8tIZVcgcFWlCsCJ72rCmrU2mDdmvgieM'
	url = 'https://torrentio.strem.fun/%s/stream/%s' % (params, url)
	headers = {'User-Agent': client.randomagent(), 'Accept': 'application/json'}
	pattern = re.compile(r'\b\w{40}\b')
	try:
		results = requests.get(url, headers=headers, timeout=7.05)
		files = results.json()['streams']
		collector.extend(pattern.findall(file['url'])[-1] for file in files if '+' in file['name'] and 'url' in file)
	except Exception as e: kodi_utils.logger('tio error', str(e))

def dmm_check_cache(unchecked_hashes_chunk, imdb, collector): # DMM API Allows max 100 hashes per request.
	""" do not thread multiple calls, abusing the api will get it turned off
		100 sample size should be enough """
	from fenom import client
	from fenom.providers.torrents.dmm import get_secret
	unchecked_hashes_chunk = [i for i in unchecked_hashes_chunk if len(i) == 40]
	if len(unchecked_hashes_chunk) > 100: unchecked_hashes_chunk = random.sample(unchecked_hashes_chunk, 100)
	url = 'https://debridmediamanager.com/api/availability/check'
	headers = {'User-Agent': client.randomagent(), 'Accept-Encoding': 'gzip, deflate, br', 'Accept': '*/*'}
	dmmProblemKey, solution = get_secret()
	data = {'dmmProblemKey': dmmProblemKey, 'solution': solution, 'imdbId': imdb, 'hashes': unchecked_hashes_chunk}
	try:
		results = requests.post(url, headers=headers, json=data, timeout=7.05)
		files = results.json()['available']
		collector.extend(file['hash'] for file in files if 'hash' in file)
	except Exception as e: kodi_utils.logger('dmm error', str(e))

class DebridCheck:
	hash_list = []
	cached_hashes = []

	@classmethod
	def set_cached_hashes(cls, hash_list):
		cls.hash_list = hash_list
		cls.cached_hashes = DebridCache().get_many(hash_list) or []

	def __init__(self, *args, meta):
		self.completed = False
		self.cached_list, self.hashes_to_cache = [], []
		self.imdb, self.season, self.episode = meta.get('imdb_id'), meta.get('season'), meta.get('episode')
		self.name, self.debrid, self.function = args
		self.thread = Thread(target=self.cache_check, name=self.name)

	def cache_write(self):
		DebridCache().set_many(self.hashes_to_cache, self.debrid)

	def external_check_cache(self, unchecked_hashes):
		checked_hashes = []
		if self.debrid == 'ad': threads = (
			Thread(target=mfn_check_cache, args=(self.imdb, self.season, self.episode, checked_hashes)),
			Thread(target=trz_check_cache, args=(self.imdb, self.season, self.episode, checked_hashes))
		)
		else: threads = (
			Thread(target=tio_check_cache, args=(self.imdb, self.season, self.episode, checked_hashes)),
			Thread(target=dmm_check_cache, args=(unchecked_hashes, self.imdb, checked_hashes))
		)
		for i in threads: i.start()
		for i in threads: i.join()
		return list(set(checked_hashes))

	def cache_check(self):
		try:
			self.cached_list = [
				i[0] for i in self.cached_hashes if i[1] == self.debrid and i[2] == 'True'
			]
			unchecked_filter = {h[0] for h in self.cached_hashes if h[1] == self.debrid}
			unchecked_hashes = [i for i in self.hash_list if not i in unchecked_filter]
			if not unchecked_hashes: return
			if self.debrid in ('rd', 'ad'): checked_hashes = self.external_check_cache(unchecked_hashes)
			else: checked_hashes = self.function().check_cache(unchecked_hashes)
			if not checked_hashes: return
			cached_append = self.cached_list.append
			process_append = self.hashes_to_cache.append
			try:
				for h in unchecked_hashes:
					cached = 'False'
					if h in checked_hashes:
						cached_append(h)
						cached = 'True'
					process_append((h, cached))
			except:
				for i in unchecked_hashes: process_append((i, 'False'))
			if self.hashes_to_cache: Thread(target=self.cache_write).start()
		finally: self.completed = True

