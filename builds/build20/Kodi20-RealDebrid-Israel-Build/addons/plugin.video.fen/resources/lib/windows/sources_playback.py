# -*- coding: utf-8 -*-
from windows import BaseDialog
from modules.settings import get_art_provider, suppress_episode_plot, progress_flags_direction
from modules.kodi_utils import empty_poster, addon_fanart
# from modules.kodi_utils import logger

string = str
flag_total = 'TOTAL'
flag_properties = {0: ('SD', '720', '1080', '4K'), 1: ('4K', '1080', '720', 'SD')}
resume_timeout = 10000

class SourcesPlayback(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.meta = kwargs.get('meta')
		self.flags_direction = progress_flags_direction()
		self.is_canceled, self.skip_resolve, self.resume_choice = False, False, None
		self.meta_get = self.meta.get
		self.enable_scraper()

	def run(self):
		self.doModal()
		self.clearProperties()
		self.clear_modals()

	def onClick(self, controlID):
		self.resume_choice = controlID == 10

	def onAction(self, action):
		if action in self.closing_actions:
			self.is_canceled = True
		elif action == self.right_action and self.window_mode == 'resolver': self.skip_resolve = True

	def iscanceled(self):
		return self.is_canceled

	def skip_resolved(self):
		status = self.skip_resolve
		self.skip_resolve = False
		return status

	def reset_is_cancelled(self):
		self.is_canceled = False

	def enable_scraper(self):
		self.window_mode = 'scraper'
		self.set_scraper_properties()

	def enable_resolver(self):
		self.window_mode = 'resolver'
		self.set_resolver_properties()

	def enable_resume(self, text):
		self.window_mode = 'resume'
		self.set_resume_properties(text)

	def busy_spinner(self, toggle='true'):
		self.setProperty('enable_busy_spinner', toggle)

	def set_scraper_properties(self):
		flag_props = flag_properties[self.flags_direction]
		flag_highlight = self.get_setting('scraper_flag_identify_colour', 'FF7C7C7C')
		result_highlight = self.get_setting('scraper_result_identify_colour', 'FFFFFFFF')
		self.poster_main, self.poster_backup, self.fanart_main, self.fanart_backup, self.clearlogo_main, self.clearlogo_backup = get_art_provider()
		self.title, self.year, self.genre = self.meta_get('title'), string(self.meta_get('year')), self.meta_get('genre', '')
		self.poster = self.meta_get('custom_poster') or self.meta_get(self.poster_main) or self.meta_get(self.poster_backup) or empty_poster
		self.fanart = self.meta_get('custom_fanart') or self.meta_get(self.fanart_main) or self.meta_get(self.fanart_backup) or addon_fanart
		self.clearlogo = self.meta_get('custom_clearlogo') or self.meta_get(self.clearlogo_main) or self.meta_get(self.clearlogo_backup) or ''
		self.setProperty('window_mode', self.window_mode)
		self.setProperty('title', self.title)
		self.setProperty('fanart', self.fanart)
		self.setProperty('clearlogo', self.clearlogo)
		self.setProperty('year', self.year)
		self.setProperty('poster', self.poster)
		self.setProperty('genre', self.genre)
		self.setProperty('flag_0', flag_props[0])
		self.setProperty('flag_1', flag_props[1])
		self.setProperty('flag_2', flag_props[2])
		self.setProperty('flag_3', flag_props[3])
		self.setProperty('flag_total', flag_total)
		self.setProperty('flag_highlight', flag_highlight)
		self.setProperty('result_highlight', result_highlight)

	def set_resolver_properties(self):
		if self.meta_get('media_type') == 'movie': self.text = self.meta_get('plot')
		else:
			if suppress_episode_plot(): plot = self.meta_get('tvshow_plot') or '* Hidden to Prevent Spoilers *'
			else: plot = self.meta_get('plot', '') or self.meta_get('tvshow_plot', '')
			self.text = '[B]%02dx%02d - %s[/B][CR][CR]%s' % (self.meta_get('season'), self.meta_get('episode'), self.meta_get('ep_name', 'N/A').upper(), plot)
		self.setProperty('window_mode', self.window_mode)
		self.setProperty('text', self.text)

	def set_resume_properties(self, text):
		self.setProperty('window_mode', self.window_mode)
		self.set_label(2003, text)
		self.setFocusId(10)
		self.update_resumer()

	def update_scraper(self, results_sd, results_720p, results_1080p, results_4k, results_total, content='', percent=0):
		if self.flags_direction == 0:
			self.setProperty('results_0', string(results_sd))
			self.setProperty('results_1', string(results_720p))
			self.setProperty('results_2', string(results_1080p))
			self.setProperty('results_3', string(results_4k))
		else:
			self.setProperty('results_0', string(results_4k))
			self.setProperty('results_1', string(results_1080p))
			self.setProperty('results_2', string(results_720p))
			self.setProperty('results_3', string(results_sd))
		self.setProperty('results_total', string(results_total))
		self.setProperty('percent', string(percent))
		self.set_text(2001, content)

	def update_resolver(self, text='', percent=0):
		try: self.setProperty('percent', string(percent))
		except: pass
		if text: self.set_text(2002, '••••  %s  ••••[CR]••••  %s  ••••' % text)

	def update_resumer(self):
		count = 0
		while self.resume_choice is None:
			percent = int((float(count)/resume_timeout)*100)
			if percent >= 100: self.resume_choice = True
			self.setProperty('percent', string(percent))
			count += 100
			self.sleep(100)
