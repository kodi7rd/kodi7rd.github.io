# -*- coding: utf-8 -*-
from xml.dom.minidom import parseString as mdParse
from caches.main_cache import cache_object
from modules.kodi_utils import make_session
# from modules.kodi_utils import logger

EXPIRY_1_WEEK = 168
url = 'http://www.omdbapi.com/?apikey=%s&i=%s&tomatoes=True&r=xml'
cache_string = 'omdb_ratings_%s'
session = make_session('http://www.omdbapi.com/')

class OMDbAPI:
	def fetch_info(self, imdb_id, api_key):
		if not imdb_id or not api_key: return {}
		self.api_key = api_key
		string = cache_string % imdb_id
		return cache_object(self.process_result, string, imdb_id, json=False, expiration=EXPIRY_1_WEEK)

	def process_result(self, imdb_id):
		data = {}
		try:
			try:
				result = session.get(url % (self.api_key, imdb_id)).text
				response_test = dict(mdParse(result).getElementsByTagName('root')[0].attributes.items())
				if not response_test.get('response', 'False') == 'True': return {}
			except: return {}
			self.result = dict(mdParse(result).getElementsByTagName('movie')[0].attributes.items())
			data = {
					'metascore_rating': self.process_rating('metascore'),
					'tomatometer_rating': self.process_rating('tomatoMeter'),
					'tomatousermeter_rating': self.process_rating('tomatoUserMeter'),
					'imdb_rating': self.process_rating('imdbRating'),
					'awards': self.process_rating('awards'),
					'tomato_consensus': self.process_rating('tomatoConsensus'),
					'tomato_image': self.process_rating('tomatoImage')
					}
		except: pass
		return data

	def process_rating(self, rating_name):
		return self.result.get(rating_name, '').replace('N/A', '')

fetch_ratings_info = OMDbAPI().fetch_info