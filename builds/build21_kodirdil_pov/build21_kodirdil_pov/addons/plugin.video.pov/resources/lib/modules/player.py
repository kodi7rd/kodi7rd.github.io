import sys
import json
from threading import Thread
from caches import watched_cache as ws
from windows import open_window
from modules import kodi_utils, settings
from modules.meta_lists import language_choices
from modules.utils import sec2time, make_title_slug
# from modules.kodi_utils import logger

KODI_VERSION, make_cast_list = kodi_utils.get_kodi_version(), kodi_utils.make_cast_list
ls, get_setting, notification = kodi_utils.local_string, kodi_utils.get_setting, kodi_utils.notification
fanart_empty = kodi_utils.get_addoninfo('fanart')
poster_empty = kodi_utils.media_path('box_office.png')

class POVPlayer(kodi_utils.xbmc_player):
	def __init__(self):
		kodi_utils.xbmc_player.__init__(self)
		self.set_resume, self.set_watched = 5, 90
		self.playback_event, self.progress_media = None, None
		self.media_marked, self.nextep_info_gathered = False, False
		self.subs_searched, self.stingers_checked = False, False
		self.nextep_started, self.play_random_continual = False, False
		self.autoplay_next_episode = False
		self.autoplay_nextep = settings.autoplay_next_episode()
		self.autoscrape_next_episode = False
		self.autoscrape_nextep = settings.autoscrape_next_episode()
		self.volume_check = get_setting('volumecheck.enabled', 'false') == 'true'
		self.stinger_check = int(get_setting('stingers.threshold', '30'))

	def run(self, url=None, progress_media=None):
		if not url: return
		try:
			self.meta = json.loads(kodi_utils.get_property('pov_playback_meta'))
			kodi_utils.clear_property('pov_playback_meta')
			self.meta_get = self.meta.get
			self.tmdb_id, self.imdb_id, self.tvdb_id = self.meta_get('tmdb_id'), self.meta_get('imdb_id'), self.meta_get('tvdb_id')
			self.media_type, self.title, self.year = self.meta_get('media_type'), self.meta_get('title'), self.meta_get('year')
			self.season, self.episode = self.meta_get('season', ''), self.meta_get('episode', '')
			background = self.meta_get('background', False) is True
			library_item = True if 'from_library' in self.meta else False
			if 'random' in self.meta or 'random_continual' in self.meta: bookmark = 0
			elif library_item: bookmark = self.bookmarkLibrary()
			else: bookmark = self.bookmarkPOV()
			if bookmark == 'cancel': return
			self.meta.update({'url': url, 'bookmark': bookmark})
			listitem = self._make_listitem()
			if not library_item: listitem.setProperty('StartPercent', str(bookmark))
			try:
				trakt_ids = {'tmdb': self.tmdb_id, 'imdb': self.imdb_id, 'slug': make_title_slug(self.title)}
				if self.media_type == 'episode': trakt_ids['tvdb'] = self.tvdb_id
				kodi_utils.clear_property('script.trakt.ids')
				kodi_utils.set_property('script.trakt.ids', json.dumps(trakt_ids))
			except: pass
			self.playback_event = False
			if library_item and not background:
				listitem.setPath(url)
				listitem.setProperty('IsPlayable', 'true')
				kodi_utils.set_resolvedurl(int(sys.argv[1]), listitem)
			else: self.play(url, listitem)
			if self.media_type == 'episode':
				self.play_random_continual = 'random_continual' in self.meta
				if not self.play_random_continual and self.autoplay_nextep: self.autoplay_next_episode = 'random' not in self.meta
				if not self.play_random_continual and self.autoscrape_nextep: self.autoscrape_next_episode = 'random' not in self.meta
				if not self.play_random_continual and self.autoplay_nextep and self.autoscrape_nextep: self.autoscrape_next_episode = False
			while not self.playback_event: kodi_utils.sleep(100)
			if callable(progress_media): progress_media()
			kodi_utils.close_all_dialog()
			if self.volume_check: kodi_utils.volume_checker(get_setting('volumecheck.percent', '100'))
			kodi_utils.sleep(1000)
			while self.isPlayingVideo():
				try:
					kodi_utils.sleep(1000)
					self.total_time, self.curr_time = self.getTotalTime(), self.getTime()
					self.current_point = round(float(self.curr_time/self.total_time * 100), 1)
					if self.media_type == 'movie' and not self.stingers_checked:
						if self.curr_time > self.stinger_check: self.run_stingers()
					if self.current_point >= self.set_watched and not self.media_marked:
						self.media_watched_marker()
					if self.play_random_continual:
						if not self.nextep_info_gathered: self.info_next_ep()
						self.remaining_time = round(self.total_time - self.curr_time)
						if self.remaining_time <= self.start_prep:
							if not self.nextep_started: self.run_random_continual()
					if self.autoplay_next_episode:
						if not self.nextep_info_gathered: self.info_next_ep()
						self.remaining_time = round(self.total_time - self.curr_time)
						if self.remaining_time <= self.start_prep:
							if not self.nextep_started and self.autoplay_nextep: self.run_next_ep()
					if self.autoscrape_next_episode:
						if not self.nextep_info_gathered: self.info_next_ep()
						self.remaining_time = round(self.total_time - self.curr_time)
						if self.remaining_time <= self.autoscrape_next_window_time:
							if not self.nextep_started and self.autoscrape_nextep: self.run_scrape_next_ep()
				except: pass
				if not self.subs_searched: self.run_subtitles()
			if not self.media_marked: self.media_watched_marker()
			ws.clear_local_bookmarks()
		except: pass

	def _make_listitem(self):
		listitem = kodi_utils.make_listitem()
		try:
			duration, plot, genre, trailer = self.meta_get('duration'), self.meta_get('plot'), self.meta_get('genre'), self.meta_get('trailer')
			rating, votes, premiered, studio = self.meta_get('rating'), self.meta_get('votes'), self.meta_get('premiered'), self.meta_get('studio')
			poster_main, poster_backup, fanart_main, fanart_backup = settings.get_art_provider()
			poster = self.meta_get(poster_main) or self.meta_get(poster_backup) or poster_empty
			fanart = self.meta_get(fanart_main) or self.meta_get(fanart_backup) or fanart_empty
			clearlogo = self.meta_get('clearlogo') or self.meta_get('tmdblogo') or ''
			if self.media_type == 'movie':
				if KODI_VERSION < 20:
					listitem.setCast(self.meta_get('cast', []))
					listitem.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': str(self.tmdb_id)})
					listitem.setInfo('video', {'mediatype': 'movie', 'trailer': trailer, 'title': self.title, 'size': '0', 'duration': duration,
						'plot': plot, 'premiered': premiered, 'studio': studio, 'year': self.year, 'genre': genre, 'tagline': self.meta_get('tagline'),
						'imdbnumber': self.imdb_id, 'director': self.meta_get('director'), 'writer': self.meta_get('writer'), 'rating': rating, 'votes': votes})
				else:
					videoinfo = infoTagger(listitem, self.meta)
					videoinfo.setCast(make_cast_list(self.meta_get('cast', [])))
					videoinfo.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': str(self.tmdb_id)})
					videoinfo.setMediaType('movie')
			else:
				if KODI_VERSION < 20:
					listitem.setCast(self.meta_get('cast', []))
					listitem.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': str(self.tmdb_id), 'tvdb': str(self.tvdb_id)})
					listitem.setInfo('video', {'mediatype': 'episode', 'trailer': trailer, 'title': self.meta_get('ep_name'), 'size': '0', 'duration': duration,
						'plot': plot, 'premiered': premiered, 'studio': studio, 'year': self.year, 'genre': genre, 'tvshowtitle': self.title,
						'imdbnumber': self.imdb_id, 'season': self.season, 'episode': self.episode, 'rating': rating, 'votes': votes})
				else:
					videoinfo = infoTagger(listitem, self.meta)
					videoinfo.setCast(make_cast_list(self.meta_get('cast', [])))
					videoinfo.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': str(self.tmdb_id), 'tvdb': str(self.tvdb_id)})
					videoinfo.setMediaType('episode')
			if settings.get_fanart_data():
				banner, clearart, landscape = self.meta_get('banner'), self.meta_get('clearart'), self.meta_get('landscape')
			else: banner, clearart, landscape = '', '', ''
			listitem.setArt({'poster': poster, 'fanart': fanart, 'icon': poster, 'banner': banner, 'clearart': clearart, 'clearlogo': clearlogo, 'landscape': landscape,
							'tvshow.clearart': clearart, 'tvshow.clearlogo': clearlogo, 'tvshow.landscape': landscape, 'tvshow.banner': banner})
		except: pass
		return listitem

	def bookmarkPOV(self):
		bookmark = 0
		watched_indicators = settings.watched_indicators()
		try: resume_point, curr_time, resume_id = ws.detect_bookmark(ws.get_bookmarks(watched_indicators, self.media_type), self.tmdb_id, self.season, self.episode)
		except: resume_point, curr_time = 0, 0
		resume_check = float(resume_point)
		if resume_check > 0:
			percent = str(resume_point)
			raw_time = float(curr_time)
			if watched_indicators == 1: resume_point = '%s%%' % str(percent)
			else: resume_point = sec2time(raw_time, n_msec=0)
			bookmark = self.getResumeStatus(resume_point, percent, bookmark)
			if bookmark == 0: ws.erase_bookmark(self.media_type, self.tmdb_id, self.season, self.episode)
		return bookmark

	def bookmarkLibrary(self):
		bookmark = 0
		try: curr_time = ws.get_bookmark_kodi_library(self.media_type, self.tmdb_id, self.season, self.episode)
		except: curr_time = 0.0
		if curr_time > 0:
			self.kodi_library_resumed = False
			resume_point = sec2time(curr_time, n_msec=0)
			bookmark = self.getResumeStatus(resume_point, curr_time, bookmark)
			if bookmark == 0: ws.erase_bookmark(self.media_type, self.tmdb_id, self.season, self.episode)
		return bookmark

	def getResumeStatus(self, resume_point, percent, bookmark):
		if settings.auto_resume(self.media_type): return percent
		choice = open_window(
			('windows.sources', 'ProgressMedia'),
			'progress_media.xml',
			meta=self.meta,
			text=ls(32790) % resume_point,
			enable_buttons=True,
			true_button=ls(32832),
			false_button=ls(32833),
			focus_button=10,
			percent=percent
		)
		return percent if choice is True else bookmark if choice is False else 'cancel'

	def media_watched_marker(self):
		self.media_marked = True
		try:
			if self.current_point >= self.set_watched:
				if self.media_type == 'movie': watched_function, watched_params = ws.mark_as_watched_unwatched_movie, {
					'mode': 'mark_as_watched_unwatched_movie', 'action': 'mark_as_watched', 'refresh': 'false', 'from_playback': 'true',
					'tmdb_id': self.tmdb_id, 'title': self.title, 'year': self.year
				}
				else: watched_function, watched_params = ws.mark_as_watched_unwatched_episode, {
					'mode': 'mark_as_watched_unwatched_episode', 'action': 'mark_as_watched', 'refresh': 'false', 'from_playback': 'true',
					'tmdb_id': self.tmdb_id, 'title': self.title, 'year': self.year, 'tvdb_id': self.tvdb_id, 'season': self.season, 'episode': self.episode
				}
				Thread(target=self.run_media_watched, args=(watched_function, watched_params)).start()
			else:
				kodi_utils.clear_property('pov_background_url')
				kodi_utils.clear_property('pov_total_autoplays')
				if not self.current_point >= self.set_resume: return
				ws.set_bookmark(self.media_type, self.tmdb_id, self.curr_time, self.total_time, self.title, self.season, self.episode)
		except: pass

	def run_media_watched(self, function, params):
		try:
			function(params)
			kodi_utils.sleep(1000)
		except: pass

	def run_scrape_next_ep(self):
		self.nextep_started = True
		try:
			from modules.episode_tools import execute_scrape_nextep
			execute_scrape_nextep(self.meta)
		except: pass

	def run_next_ep(self):
		self.nextep_started = True
		try:
			from modules.episode_tools import execute_nextep
			Thread(target=execute_nextep, args=(self.meta, self.nextep_settings)).start()
		except: pass

	def run_random_continual(self):
		self.nextep_started = True
		try:
			from modules.episode_tools import execute_nextep
			Thread(target=execute_nextep, args=(self.meta, self.nextep_settings)).start()
		except: pass

	def run_subtitles(self):
		self.subs_searched = True
		try:
			poster = self.meta.get('poster') or poster_empty
			season = self.season if self.media_type == 'episode' else None
			episode = self.episode if self.media_type == 'episode' else None
			Thread(target=Subtitles().get, args=(self.title, self.imdb_id, season, episode, poster)).start()
		except: pass

	def run_stingers(self):
		self.stingers_checked = True
		try:
			poster = self.meta.get('poster') or poster_empty
			if not self.meta.get('stingers', '') == 'true': return
			Thread(target=get_stingers, args=(self.tmdb_id, poster)).start()
		except: pass

	def info_next_ep(self):
		self.nextep_info_gathered = True
		try:
			self.nextep_settings = settings.autoplay_next_settings()
			if not self.nextep_settings['run_popup']:
				window_time = round(0.02 * self.total_time)
				self.nextep_settings['window_time'] = window_time
			elif self.nextep_settings['timer_method'] == 'percentage':
				percentage = self.nextep_settings['window_percentage']
				window_time = round((percentage/100) * self.total_time)
				self.nextep_settings['window_time'] = window_time
			else:
				window_time = self.nextep_settings['window_time']
			threshold_check = window_time + 21
			self.start_prep = self.nextep_settings['scraper_time'] + threshold_check
			self.nextep_settings.update({'threshold_check': threshold_check, 'start_prep': self.start_prep})
			self.autoscrape_next_window_time = self.nextep_settings['autoscrape_next_window_time']
		except: pass

	def onAVStarted(self):
		self.playback_event = True

	def onPlayBackStarted(self):
		try: kodi_utils.hide_busy_dialog()
		except: pass

	def onPlayBackStopped(self):
		self.playback_event = 'stop'

class Subtitles(kodi_utils.xbmc_player):
	def __init__(self):
		kodi_utils.xbmc_player.__init__(self)
		self.language_dict = language_choices
		self.auto_enable = get_setting('subtitles.auto_enable')
		self.subs_action = {'0': 'auto', '1': 'select', '2': 'off'}[get_setting('subtitles.subs_action', '2')]
		self.language1 = self.language_dict[get_setting('subtitles.language')]

	def get(self, query, imdb_id, season, episode, poster):
		def _video_file_subs():
			try: available_sub_language = self.getSubtitles()
			except: available_sub_language = ''
			if not available_sub_language == self.language1: return False
			if self.auto_enable == 'true': self.showSubtitles(True)
			notification(32852, icon=poster)
			return True
		def _downloaded_subs():
			files = kodi_utils.list_dirs(subtitle_path)[1]
			final_match = next((i for i in files if i == search_filename), None)
			if not final_match: return False
			subtitle = '%s%s' % (subtitle_path, final_match)
			notification(32792, icon=poster)
			return subtitle
		def _searched_subs():
			search_language = kodi_utils.convert_language(self.language1, format='short')
			result = subtitles.search(imdb_id, search_language, season, episode)
			if not result: return notification(32793, icon=poster)
			result.sort(key=lambda k: k['isHearingImpaired'], reverse=False)
			if self.subs_action == 'select' and len(result) > 1:
				try: video_path = self.getPlayingFile()
				except: video_path = ''
				if '|' in video_path: video_path = video_path.split('|')[0]
				video_path = os.path.basename(video_path)
				for i in result:
					line1 = '%s (%s%s | %s)'% (i['display'], i['source'], ' | SDH' if i['isHearingImpaired'] else '', i['encoding'])
					i.update({'line1': line1, 'line2': '[B]%s[/B]' % i['media'].upper(), 'icon': poster})
				kwargs = {'enumerate': 'true', 'multi_choice': 'false', 'multi_line': 'true'}
				kwargs.update({'items': json.dumps(result), 'heading': '%s - %s' % (ls(32246).upper(), video_path)})
				self.pause()
				chosen_sub = kodi_utils.select_dialog(result, **kwargs)
				self.pause()
			else: chosen_sub = next(iter(result), None)
			if not chosen_sub: return notification(32736, icon=poster)
			try: lang = kodi_utils.convert_language(chosen_sub['language'])
			except: lang = chosen_sub['language']
			final_filename = sub_filename + '_%s.%s' % (lang, chosen_sub['format'])
			final_path = '%s%s' % (subtitle_path, final_filename)
			response = subtitles.download(chosen_sub['url'])
			if isinstance(response, str): return kodi_utils.notification('Subtitles Error: %s' % response)
			try:
				if not 'utf-8' in response.encoding.lower():
					import codecs
					content = codecs.decode(response.content, encoding='utf-8')
				else: content = response.text
			except: content = response.content
			with kodi_utils.open_file(final_path, 'w') as file: file.write(content)
			kodi_utils.sleep(1000)
			return final_path
		if not self.subs_action in ('auto', 'select'): return
		import os
		from indexers import subtitles
		kodi_utils.sleep(2500)
		subtitle_path = 'special://temp/'
		sub_filename = 'POVSubs_%s_%s_%s' % (imdb_id, season, episode) if season else 'POVSubs_%s' % imdb_id
		search_filename = sub_filename + '_%s.srt' % self.language1
		subtitle = _video_file_subs()
		if subtitle: return
		subtitle = _downloaded_subs()
		if subtitle: return self.setSubtitles(subtitle)
		subtitle = _searched_subs()
		if subtitle: return self.setSubtitles(subtitle)

def get_stingers(tmdb_id, poster):
	if not tmdb_id: return
	from indexers.tmdb_api import movie_keywords
	stingers = {'duringcreditsstinger': 'During Credit Scene', 'aftercreditsstinger': 'After Credit Scene'}
	keywords = movie_keywords(tmdb_id) or []
	keywords = [str(i['name']) for i in keywords]
	if all((i in keywords for i in stingers.keys())): stinger = 'Dual Credit Scenes'
	else: stinger = next((v for k, v in stingers.items() if k in keywords), None)
	if stinger: notification(stinger, time=6000, icon=poster)

def infoTagger(listitem, meta=None):
	infotag = listitem.getVideoInfoTag(offscreen=True)
	if not meta: return infotag
	for key, val in (
		('country', 'setCountries'), ('director', 'setDirectors'),
		('duration', 'setDuration'), ('genre', 'setGenres'),
		('imdbnumber', 'setIMDBNumber'), ('mediatype', 'setMediaType'),
		('mpaa', 'setMpaa'), ('original_title', 'setOriginalTitle'),
		('playcount', 'setPlaycount'), ('plot', 'setPlot'),
		('premiered', 'setFirstAired' if 'episode' in meta else 'setPremiered'),
		('rating', 'setRating'), ('studio', 'setStudios'),
		('tagline', 'setTagLine'), ('title', 'setTitle'),
		('trailer', 'setTrailer'), ('votes', 'setVotes'),
		('writer', 'setWriters'), ('year', 'setYear'),
		# tvshow exclusive
		('air_date', 'setPremiered'), ('aired', 'setFirstAired'),
		('ep_name', 'setTitle'), ('episode', 'setEpisode'), ('season', 'setSeason'),
		('status', 'setTvShowStatus'), ('tvshowtitle', 'setTvShowTitle')
	):
		try:
			if not key in meta or not (arg := meta[key]): continue
			if   key in {'director', 'genre', 'studio', 'writer'}: arg = arg.split(', ')
			elif key in {'episode', 'season', 'year'}: arg = int(arg)
			func = getattr(infotag, val)
			func(arg)
		except: pass
	return infotag

