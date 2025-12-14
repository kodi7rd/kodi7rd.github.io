import requests
from caches.main_cache import cache_object
from modules import kodi_utils
# logger = kodi_utils.logger

ls, get_setting, set_setting = kodi_utils.local_string, kodi_utils.get_setting, kodi_utils.set_setting
auth_url = 'https://app.real-debrid.com/oauth/v2/'
base_url = 'https://app.real-debrid.com/rest/1.0/'
timeout = 10.0
session = requests.Session()
session.mount('https://app.real-debrid.com', requests.adapters.HTTPAdapter(max_retries=1))

class RealDebridAPI:
	icon = 'realdebrid.png'

	def __init__(self):
		self.token = get_setting('rd.token')
		session.headers['Authorization'] = 'Bearer %s' % self.token

	def _request(self, method, path, data=None):
		url = base_url + path
		try: response = session.request(method, url, data=data, timeout=timeout)
		except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
			return kodi_utils.notification('%s timeout' % self.__class__.__name__)
		if response.status_code in (401,) and self.refresh_token() is True:
			response.request.headers['Authorization'] = 'Bearer %s' % self.token
			response = session.send(response.request, timeout=timeout)
		if not response.ok: kodi_utils.logger(self.__class__.__name__, f"{response.reason}\n{response.url}")
		return response.json() if len(response.content) else response

	def _get(self, path):
		return self._request('get', path)

	def _post(self, path, data=None):
		return self._request('post', path, data=data)

	def refresh_token(self):
		try:
			client_id, secret, refresh = get_setting('rd.client_id'), get_setting('rd.secret'), get_setting('rd.refresh')
			data = {'client_id': client_id, 'client_secret': secret, 'code': refresh, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}
			url = auth_url + 'token'
			response = requests.post(url, data=data).json()
			self.token, refresh = response['access_token'], response['refresh_token']
			set_setting('rd.token', self.token)
			set_setting('rd.refresh', refresh)
		except Exception as e: kodi_utils.logger('refresh_token error', str(e))
		else: return True
		return False

	def days_remaining(self):
#		import datetime, time
		try:
			account_info = self.account_info()
#			FormatDateTime = "%Y-%m-%dT%H:%M:%S.%fZ"
#			try: expires = datetime.datetime.strptime(account_info['expiration'], FormatDateTime)
#			except: expires = datetime.datetime(*(time.strptime(account_info['expiration'], FormatDateTime)[0:6]))
#			days = (expires - datetime.datetime.today()).days
			days = int(account_info['premium']/86400)
		except: days = None
		return days

	def account_info(self):
		url = 'user'
		return self._get(url)

	def torrent_info(self, file_id):
		url = 'torrents/info/%s' % file_id
		return self._get(url)

	def delete_torrent(self, folder_id):
		url = 'torrents/delete/%s' % folder_id
		result = self._request('delete', url)
		return True if not result is None and result.ok else False

	def delete_download(self, download_id):
		url = 'downloads/delete/%s' % download_id
		result = self._request('delete', url)
		return True if not result is None and result.ok else False

	def unrestrict_link(self, link):
		url = 'unrestrict/link'
		post_data = {'link': link}
		response = self._post(url, post_data)
		try: return response['download']
		except: return None

	def check_single_magnet(self, hash_string):
		cache_info = self.check_hash(hash_string)
		if not hash_string in cache_info: return False
		info = cache_info[hash_string]
		return True if isinstance(info, dict) and len(info.get('rd')) > 0 else False

	def check_hash(self, hash_string):
		url = 'torrents/instantAvailability/%s' % hash_string
		return self._get(url)

	def check_cache(self, hashes):
		hash_string = '/'.join(hashes)
		url = 'torrents/instantAvailability/%s' % hash_string
		return self._get(url)

	def add_torrent_select(self, torrent_id, file_ids):
		self.clear_cache()
		url = 'torrents/selectFiles/%s' % torrent_id
		post_data = {'files': file_ids}
		return self._post(url, post_data)

	def add_magnet(self, magnet):
		post_data = {'magnet': magnet}
		url = 'torrents/addMagnet'
		return self._post(url, post_data)

	def create_transfer(self, magnet):
		from modules.source_utils import supported_video_extensions
		try:
			extensions = supported_video_extensions()
			torrent = self.add_magnet(magnet)
			torrent_id = torrent['id']
#			info = self.torrent_info(torrent_id)
#			files = info['files']
#			torrent_keys = [str(item['id']) for item in files if item['path'].lower().endswith(tuple(extensions))]
#			torrent_keys = ','.join(torrent_keys)
#			self.add_torrent_select(torrent_id, torrent_keys)
			self.add_torrent_select(torrent_id, 'all')
			return torrent_id
		except:
			self.delete_torrent(torrent_id)
			return ''

	def parse_magnet_pack(self, magnet_url, info_hash, errors=False):
		from modules.source_utils import supported_video_extensions
		try:
			extensions = supported_video_extensions()
			torrent_id = self.create_transfer(magnet_url)
			for key in ['ended'] * 3:
				kodi_utils.sleep(500)
				torrent_info = self.torrent_info(torrent_id)
				if key in torrent_info: break
			else: raise Exception('real debrid uncached magnet')
			torrent_files = (i for i in torrent_info['files'] if i['selected'])
			torrent_files = [
				{'link': link,
				 'size': item['bytes'],
				 'torrent_id': torrent_id,
				 'filename': item['path'].replace('/', '')}
				for item, link in zip(torrent_files, torrent_info['links'])
				if item['path'].lower().endswith(tuple(extensions))
			]
			return torrent_files
		except Exception as e:
			if torrent_id: self.delete_torrent(torrent_id)
			if errors: raise

	def get_hosts(self):
		string = 'pov_rd_valid_hosts'
		url = 'hosts/domains'
		hosts_dict = {'Real-Debrid': []}
		try:
			result = cache_object(self._get, string, url, False, 48)
			hosts_dict['Real-Debrid'] = result
		except: pass
		return hosts_dict

	def downloads(self):
		string = 'pov_rd_downloads'
		url = 'downloads?limit=500'
		return cache_object(self._get, string, url, False, 0.5)

	def user_cloud(self, completed=True):
		string = 'pov_rd_user_cloud'
		url = 'torrents?limit=500'
		result = cache_object(self._get, string, url, False, 0.5)
		if completed: result = [i for i in result if i.get('ended')]
		return result

	def user_cloud_info(self, file_id):
		string = 'pov_rd_user_cloud_info_%s' % file_id
		url = 'torrents/info/%s' % file_id
		return cache_object(self._get, string, url, False, 2)

	def clear_cache(*args):
		from modules.kodi_utils import clear_property, path_exists, database_connect, maincache_db
		try:
			if not path_exists(maincache_db): return True
			from caches.debrid_cache import DebridCache
			dbcon = database_connect(maincache_db)
			dbcur = dbcon.cursor()
			# USER CLOUD
			try:
				dbcur.execute("""SELECT id FROM maincache WHERE id LIKE ?""", ('pov_rd_user_cloud%',))
				user_cloud_cache = [str(i[0]) for i in dbcur.fetchall()]
				if user_cloud_cache:
					dbcur.execute("""DELETE FROM maincache WHERE id LIKE ?""", ('pov_rd_user_cloud%',))
					for i in user_cloud_cache: clear_property(i)
					dbcon.commit()
				user_cloud_success = True
			except: user_cloud_success = False
			# DOWNLOAD LINKS
			try:
				dbcur.execute("""DELETE FROM maincache WHERE id = ?""", ('pov_rd_downloads',))
				clear_property('pov_rd_downloads')
				dbcon.commit()
				download_links_success = True
			except: download_links_success = False
			# HOSTERS
			try:
				dbcur.execute("""DELETE FROM maincache WHERE id = ?""", ('pov_rd_valid_hosts',))
				clear_property('pov_rd_valid_hosts')
				dbcon.commit()
				dbcon.close()
				hoster_links_success = True
			except: hoster_links_success = False
			# HASH CACHED STATUS
			try:
				DebridCache().clear_debrid_results('rd')
				hash_cache_status_success = True
			except: hash_cache_status_success = False
		except: return False
		if False in (user_cloud_success, download_links_success, hoster_links_success, hash_cache_status_success): return False
		return True

