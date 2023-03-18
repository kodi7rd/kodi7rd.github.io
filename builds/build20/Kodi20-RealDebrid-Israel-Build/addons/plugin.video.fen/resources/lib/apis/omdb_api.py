# -*- coding: utf-8 -*-
from xml.dom.minidom import parseString as mdParse
from caches.main_cache import cache_object
from modules.kodi_utils import make_session
# from modules.kodi_utils import logger

EXPIRY_1_WEEK = 168
url = 'http://www.omdbapi.com/?apikey=%s&i=%s&tomatoes=True&r=xml'
cache_string = 'imdb_ratings_by_omdb_%s'
session = make_session('http://www.omdbapi.com/')

class OMDbAPI:
	def fetch_info(self, imdb_id, api_key):
		if not imdb_id or not api_key: return {}
		self.api_key = api_key
		string = cache_string % imdb_id
		return cache_object(self.process_result, string, imdb_id, json=False, expiration=EXPIRY_1_WEEK)

	def process_result(self, imdb_id):
		data = {}
		self.result = self.get_result(imdb_id)
		if not self.result: return {}
		self.result_get = self.result.get
		metascore_rating, tomatometer_rating, tomatousermeter_rating = self.process_rating('metascore'), self.process_rating('tomatoMeter'), self.process_rating('tomatoUserMeter')
		imdb_rating, tomato_image = self.process_rating('imdbRating'), self.process_rating('tomatoImage')
		metascore_icon, imdb_icon, tmdb_icon = 'metacritic.png', 'imdb.png', 'tmdb.png'
		if tomato_image: tomatometer_icon = 'rtcertified.png' if tomato_image == 'certified' else 'rtfresh.png' if tomato_image == 'fresh' else 'rtrotten.png'
		elif tomatometer_rating: tomatometer_icon = 'rtfresh.png' if int(tomatometer_rating) > 59 else 'rtrotten.png'
		else: tomatometer_icon = 'rtrotten.png'
		if tomatousermeter_rating: tomatousermeter_icon = 'popcorn.png' if int(tomatousermeter_rating) > 59 else 'popcorn_spilt.png'
		else: tomatousermeter_icon = 'popcorn_spilt.png'		
		data = {
				'metascore': {'rating': '%s%%' %  metascore_rating, 'icon': metascore_icon},
				'tomatometer': {'rating': '%s%%' % tomatometer_rating, 'icon': tomatometer_icon},
				'tomatousermeter': {'rating': '%s%%' % tomatousermeter_rating, 'icon': tomatousermeter_icon},
				'imdb': {'rating': imdb_rating, 'icon': imdb_icon},
				'tmdb': {'rating': '', 'icon': tmdb_icon},
				}
		return data

	def get_result(self, imdb_id):
		try:
			result = session.get(url % (self.api_key, imdb_id)).text
			response_test = dict(mdParse(result).getElementsByTagName('root')[0].attributes.items())
			if not response_test.get('response', 'False') == 'True': return None
		except: return None
		return dict(mdParse(result).getElementsByTagName('movie')[0].attributes.items())

	def process_rating(self, rating_name):
		return self.result_get(rating_name, '').replace('N/A', '')

fetch_ratings_info = OMDbAPI().fetch_info

def refresh_omdb_meta_data(imdb_id):
	from modules.kodi_utils import path_exists, clear_property, database, maincache_db
	try:
		if not path_exists(maincache_db): return
		insert = cache_string % imdb_id
		dbcon = database.connect(maincache_db, timeout=40.0, isolation_level=None)
		dbcur = dbcon.cursor()
		dbcur.execute('''PRAGMA synchronous = OFF''')
		dbcur.execute('''PRAGMA journal_mode = OFF''')
		dbcur.execute("SELECT id FROM maincache WHERE id LIKE ?", (insert,))
		omdb_results = [str(i[0]) for i in dbcur.fetchall()]
		if not omdb_results: return
		dbcur.execute("DELETE FROM maincache WHERE id == ?", (insert,))
		for i in omdb_results: clear_property(i)
	except: pass