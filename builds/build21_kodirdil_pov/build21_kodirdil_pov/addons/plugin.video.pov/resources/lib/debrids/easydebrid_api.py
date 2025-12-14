import requests
from modules import kodi_utils
# logger = kodi_utils.logger

ls, get_setting = kodi_utils.local_string, kodi_utils.get_setting
ip_url = 'https://api.ipify.org'
base_url = 'https://easydebrid.com/api/v1'
timeout = 20.0
session = requests.Session()
session.mount('https://easydebrid.com', requests.adapters.HTTPAdapter(max_retries=1))

class EasyDebridAPI:
	icon = 'easydebrid.png'

	def __init__(self):
		self.token = get_setting('ed.token')
		session.headers['Authorization'] = 'Bearer %s' % self.token

	def _request(self, method, path, params=None, json=None, data=None):
		url = '%s/%s' % (base_url, path)
		try: response = session.request(method, url, params=params, json=json, data=data, timeout=timeout)
		except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
			return kodi_utils.notification('%s timeout' % self.__class__.__name__)
		if not response.ok: kodi_utils.logger(self.__class__.__name__, f"{response.reason}\n{response.url}")
		return response.json() if 'json' in response.headers.get('Content-Type', '') else response

	def _get(self, url, params=None):
		return self._request('get', url, params=params)

	def _post(self, url, params=None, json=None, data=None):
		return self._request('post', url, params=params, json=json, data=data)

	def days_remaining(self):
		from datetime import datetime
		try:
			account_info = self.account_info()
			expires = datetime.fromtimestamp(account_info['paid_until'])
			days = (expires - datetime.today()).days
		except: days = None
		return days

	def account_info(self):
		url = 'user/details'
		return self._get(url)

	def unrestrict_link(self, link):
		return link

	def check_single_magnet(self, hash_string):
		result = self.check_cache([hash_string])
		return hash_string in result

	def check_cache(self, hashes):
		data = {'urls': hashes}
		url = 'link/lookup'
		result = self._post(url, json=data)
		return [h for h, cached in zip(hashes, result['cached']) if cached]

	def instant_transfer(self, magnet):
		try: user_ip = requests.get(ip_url, timeout=2.0).text
		except: user_ip = ''
		if user_ip: session.headers['X-Forwarded-For'] = user_ip
		data = {'url': magnet}
		url = 'link/generate'
		return self._post(url, json=data)

	def create_transfer(self, magnet):
		data = {'url': magnet}
		url = 'link/request'
		result = self._post(url, json=data)
		return result.get('success', '')

	def parse_magnet_pack(self, magnet_url, info_hash):
		from modules.source_utils import supported_video_extensions
		try:
			extensions = supported_video_extensions()
			torrent = self.instant_transfer(magnet_url)
			torrent_files = torrent['files']
			torrent_files = [
				{'link': item['url'],
				 'size': item['size'],
				 'filename': item['filename']}
				for item in torrent_files
				if item['filename'].lower().endswith(tuple(extensions))
			]
			return torrent_files
		except Exception:
			return None

	def clear_cache(*args):
		try:
			if not kodi_utils.path_exists(kodi_utils.maincache_db): return True
			from caches.debrid_cache import DebridCache
			dbcon = kodi_utils.database_connect(kodi_utils.maincache_db)
			dbcur = dbcon.cursor()
			# USER CLOUD
			try:
#				dbcur.execute("""DELETE FROM maincache WHERE id = ?""", ('pov_ed_user_cloud',))
				kodi_utils.clear_property('pov_ed_user_cloud')
#				dbcon.commit()
				user_cloud_success = True
			except: user_cloud_success = False
			# HASH CACHED STATUS
			try:
				DebridCache().clear_debrid_results('ed')
				hash_cache_status_success = True
			except: hash_cache_status_success = False
		except: return False
		if False in (user_cloud_success, hash_cache_status_success): return False
		return True

