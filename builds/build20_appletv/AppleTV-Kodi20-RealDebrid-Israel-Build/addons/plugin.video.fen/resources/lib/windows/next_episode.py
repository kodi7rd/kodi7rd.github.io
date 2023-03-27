# -*- coding: utf-8 -*-
from windows import BaseDialog
from modules.kodi_utils import Thread, empty_poster
from modules.settings import get_art_provider
from modules.kodi_utils import logger

button_actions = {'autoplay_nextep': {10: 'close', 11: 'play', 12: 'cancel'}, 'autoscrape_nextep': {10: 'play', 11: 'close', 12: 'cancel'}}

class NextEpisode(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.closed = False
		self.meta = kwargs.get('meta')
		self.selected = kwargs.get('default_action', 'cancel')
		self.play_type = kwargs.get('play_type', 'autoplay_nextep')
		self.focus_button = kwargs.get('focus_button', 10)
		self.poster_main, self.poster_backup, self.fanart_main, self.fanart_backup, self.clearlogo_main, self.clearlogo_backup = get_art_provider()
		self.set_properties()

	def onInit(self):
		self.setFocusId(self.focus_button)
		self.monitor()

	def run(self):
		self.doModal()
		self.clearProperties()
		self.clear_modals()
		return self.selected

	def onAction(self, action):
		if action in self.closing_actions:
			self.selected = 'close'
			self.closed = True
			self.close()

	def onClick(self, controlID):
		self.selected = button_actions[self.play_type][controlID]
		self.closed = True
		self.close()

	def set_properties(self):
		self.setProperty('play_type', self.play_type)
		self.setProperty('title', self.meta['title'])
		self.setProperty('poster', self.original_poster())
		self.setProperty('fanart', self.original_fanart())
		self.setProperty('clearlogo', self.original_clearlogo())
		self.setProperty('next_ep_title', self.meta['title'])
		self.setProperty('next_ep_season', '%02d' % self.meta['season'])
		self.setProperty('next_ep_episode', '%02d' % self.meta['episode'])
		self.setProperty('next_ep_ep_name', self.meta['ep_name'])

	def original_poster(self):
		return self.meta.get('custom_poster') or self.meta.get(self.poster_main) or self.meta.get(self.poster_backup) or empty_poster

	def original_fanart(self):
		return self.meta.get('custom_fanart') or self.meta.get(self.fanart_main) or self.meta.get(self.fanart_backup) or ''

	def original_clearlogo(self):
		return self.meta.get('custom_clearlogo') or self.meta.get(self.clearlogo_main) or self.meta.get(self.clearlogo_backup) or ''

	def monitor(self):
		try: progress_bar = self.get_control(5000)
		except: progress_bar = None
		total_time = self.player.getTotalTime()
		total_remaining = total_time - self.player.getTime()
		while self.player.isPlaying():
			try:
				if self.closed: break
				current_time = self.player.getTime()
				remaining = round(total_time - current_time)
				current_point = (remaining / float(total_remaining)) * 100
				if progress_bar: progress_bar.setPercent(current_point)
				self.sleep(1000)
			except: pass
		self.close()
