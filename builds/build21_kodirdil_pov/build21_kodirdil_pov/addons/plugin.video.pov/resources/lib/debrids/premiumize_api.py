import requests
from caches.main_cache import cache_object
from modules import kodi_utils
# logger = kodi_utils.logger

ls, get_setting = kodi_utils.local_string, kodi_utils.get_setting
user_agent = 'POV/%s' % kodi_utils.get_addoninfo('version')
client_id = '663882072'
base_url = 'https://www.premiumize.me/api/'
timeout = 10.0
session = requests.Session()
session.mount('https://www.premiumize.me', requests.adapters.HTTPAdapter(max_retries=1))

class PremiumizeAPI:
	icon = 'premiumize.png'

	def __init__(self):
		self.token = get_setting('pm.token')
		session.headers.update(self.headers())

	def _request(self, method, path, data=None):
		url = base_url + path
		try: response = session.request(method, url, data=data, timeout=timeout)
		except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
			return kodi_utils.notification('%s timeout' % self.__class__.__name__)
		if not response.ok: kodi_utils.logger(self.__class__.__name__, f"{response.reason}\n{response.url}")
		return response.json() if 'json' in response.headers.get('Content-Type', '') else response

	def _get(self, path):
		return self._request('get', path)

	def _post(self, path, data=None):
		return self._request('post', path, data=data)

	def add_headers_to_url(self, url):
		return url + '|' + kodi_utils.urlencode(self.headers())

	def headers(self):
		return {'User-Agent': user_agent, 'Authorization': 'Bearer %s' % self.token}

	def days_remaining(self):
		import datetime
		try:
			account_info = self.account_info()
			expires = datetime.datetime.fromtimestamp(account_info['premium_until'])
			days = (expires - datetime.datetime.today()).days
		except: days = None
		return days

	def account_info(self):
		url = 'account/info'
		response = self._get(url)
		return response

	def item_listall(self):
		url = 'item/listall'
		return self._get(url)

	def delete_torrent(self, transfer_id):
		return self.delete_object('transfer', transfer_id)

	def unrestrict_link(self, link):
		data = {'src': link}
		url = 'transfer/directdl'
		response = self._post(url, data)
		try: return self.add_headers_to_url(response['content'][0]['link'])
		except: return None

	def check_single_magnet(self, hash_string):
		cache_info = self.check_cache([hash_string])
		return hash_string in cache_info

	def check_cache(self, hashes):
		data = {'items[]': hashes}
		url = 'cache/check'
		response = self._post(url, data)
		return [h for h, cached in zip(hashes, response['response']) if cached]

	def instant_transfer(self, magnet):
		data = {'src': magnet}
		url = 'transfer/directdl'
		return self._post(url, data)

	def create_transfer(self, magnet):
		data = {'src': magnet, 'folder_id': 0}
		url = 'transfer/create'
		response = self._post(url, data)
		return response.get('id', '')

	def parse_magnet_pack(self, magnet_url, info_hash):
		from modules.source_utils import supported_video_extensions
		try:
			extensions = supported_video_extensions()
			torrent = self.instant_transfer(magnet_url)
			torrent_files = torrent['content']
			torrent_files = [
				{'link': item['link'],
				 'size': item['size'],
				 'filename': item['path'].split('/')[-1]}
				for item in torrent_files
				if item['path'].lower().endswith(tuple(extensions))
			]
			return torrent_files
		except Exception:
			return None

	def zip_folder(self, folder_id):
		url = 'zip/generate'
		data = {'folders[]': folder_id}
		response = self._post(url, data)
		return response

	def download_link_magnet_zip(self, magnet_url, info_hash):
		try:
#			result = self.create_transfer(magnet_url)
#			if not 'status' in result or result['status'] != 'success': return None
#			transfer_id = result['id']
			transfer_id = self.create_transfer(magnet_url)
			if not transfer_id: return None
			transfers = self.downloads()['transfers']
			folder_id = [i['folder_id'] for i in transfers if i['id'] == transfer_id][0]
			result = self.zip_folder(folder_id)
			if result['status'] == 'success':
				return result['location']
			else: return None
		except:
			pass

	def rename_cache_item(self, file_type, file_id, new_name):
		if file_type == 'folder': url = 'folder/rename'
		else: url = 'item/rename'
		data = {'id': file_id , 'name': new_name}
		response = self._post(url, data)
		return True if not response is None and response['status'] == 'success' else False

	def delete_object(self, object_type, object_id):
		data = {'id': object_id}
		url = '%s/delete' % object_type
		response = self._post(url, data)
		return True if not response is None and response['status'] == 'success' else False

	def get_item_details(self, item_id):
		string = 'pov_pm_item_details_%s' % item_id
		url = 'item/details'
		data = {'id': item_id}
		args = [url, data]
		return cache_object(self._post, string, args, False, 24)

	def get_hosts(self):
		string = 'pov_pm_valid_hosts'
		url = 'services/list'
		hosts_dict = {'Premiumize.me': []}
		hosts = []
		append = hosts.append
		try:
			result = cache_object(self._get, string, url, False, 168)
			for x in result['directdl']:
				for alias in result['aliases'][x]: append(alias)
			hosts_dict['Premiumize.me'] = list(set(hosts))
		except: pass
		return hosts_dict

	def downloads(self):
		string = 'pov_pm_downloads'
		url = 'transfer/list'
		return cache_object(self._get, string, url, False, 0.5)

	def user_cloud(self, folder_id=None):
		if folder_id:
			string = 'pov_pm_user_cloud_%s' % folder_id
			url = 'folder/list?id=%s' % folder_id
		else:
			string = 'pov_pm_user_cloud_root'
			url = 'folder/list'
		return cache_object(self._get, string, url, False, 0.5)

	def clear_cache(*args):
		from modules.kodi_utils import clear_property, path_exists, database_connect, maincache_db
		try:
			if not path_exists(maincache_db): return True
			from caches.debrid_cache import DebridCache
			dbcon = database_connect(maincache_db)
			dbcur = dbcon.cursor()
			# USER CLOUD
			try:
				dbcur.execute("""SELECT id FROM maincache WHERE id LIKE ?""", ('pov_pm_user_cloud%',))
				user_cloud_cache = [str(i[0]) for i in dbcur.fetchall()]
				if user_cloud_cache:
					dbcur.execute("""DELETE FROM maincache WHERE id LIKE ?""", ('pov_pm_user_cloud%',))
					for i in user_cloud_cache: clear_property(i)
					dbcon.commit()
				user_cloud_success = True
			except: user_cloud_success = False
			# DOWNLOAD LINKS
			try:
				dbcur.execute("""DELETE FROM maincache WHERE id = ?""", ('pov_pm_downloads',))
				clear_property('pov_pm_downloads')
				dbcon.commit()
				download_links_success = True
			except: download_links_success = False
			# HOSTERS
			try:
				dbcur.execute("""DELETE FROM maincache WHERE id = ?""", ('pov_pm_valid_hosts',))
				clear_property('pov_pm_valid_hosts')
				dbcon.commit()
				dbcon.close()
				hoster_links_success = True
			except: hoster_links_success = False
			# HASH CACHED STATUS
			try:
				DebridCache().clear_debrid_results('pm')
				hash_cache_status_success = True
			except: hash_cache_status_success = False
		except: return False
		if False in (user_cloud_success, download_links_success, hoster_links_success, hash_cache_status_success): return False
		return True

