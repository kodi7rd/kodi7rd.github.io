# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcvfs
import json
import sqlite3 as database
from threading import Thread
from modules import xmls
# from modules.logger import logger

dialog = xbmcgui.Dialog()
window = xbmcgui.Window(10000)
max_widgets = 10

settings_path = xbmcvfs.translatePath('special://profile/addon_data/script.FENtastic.helper/')
database_path = xbmcvfs.translatePath('special://profile/addon_data/script.FENtastic.helper/cpath_cache.db')
movies_widgets_xml, tvshows_widgets_xml = 'script-FENtastic-widget_movies', 'script-FENtastic-widget_tvshows'
movies_categories_top_xml, tvshows_categories_top_xml = 'script-FENtastic-widget_movie_category_top', 'script-FENtastic-widget_tvshow_category_top'
movies_categories_bottom_xml, tvshows_categories_bottom_xml = 'script-FENtastic-widget_movie_category_bottom', 'script-FENtastic-widget_tvshow_category_bottom'
movies_main_menu_xml, tvshows_main_menu_xml = 'script-FENtastic-main_menu_movies', 'script-FENtastic-main_menu_tvshows'

default_xmls = {'movie.widget': (movies_widgets_xml, xmls.default_widget, 'MovieWidgets'),
				'tvshow.widget': (tvshows_widgets_xml, xmls.default_widget, 'TVShowWidgets'),
				'movie.category_top_widget': (movies_categories_top_xml, xmls.default_category_top_widget, 'MovieCategoryWidgetTop'),
				'movie.category_bottom_widget': ( movies_categories_bottom_xml, xmls.default_category_bottom_widget, 'MovieCategoryWidgetBottom'),
				'tvshow.category_top_widget': (tvshows_categories_top_xml, xmls.default_category_top_widget, 'TVShowCategoryWidgetTop'),
				'tvshow.category_bottom_widget': (tvshows_categories_bottom_xml, xmls.default_category_bottom_widget, 'TVShowCategoryWidgetBottom'),
				'movie.main_menu': (movies_main_menu_xml, xmls.default_main_menu, 'MoviesMainMenu'),
				'tvshow.main_menu': (tvshows_main_menu_xml, xmls.default_main_menu, 'TVShowsMainMenu')
				}

class CPaths:
	def __init__(self, cpath_setting):
		self.cpath_setting = cpath_setting
		self.refresh_cpaths = False
		self.last_cpath = None
		self.connect_database()
		self.media_type = 'movie' if 'movie' in self.cpath_setting else 'tvshow'
		self.cpath_lookup = "'%s%s'" % (self.cpath_setting, '%')
		self.set_main_include()

	def set_main_include(self):
		if 'category_top' in self.cpath_setting: self.main_include = 'MovieCategoryWidgetTop' if self.media_type == 'movie' else 'TVShowCategoryWidgetTop'
		elif 'category_bottom' in self.cpath_setting: self.main_include = 'MovieCategoryWidgetBottom' if self.media_type == 'movie' else 'TVShowCategoryWidgetBottom'
		else: self.main_include = 'MovieWidgets' if self.media_type == 'movie' else 'TVShowWidgets'

	def connect_database(self):
		if not xbmcvfs.exists(settings_path): xbmcvfs.mkdir(settings_path)
		self.dbcon = database.connect(database_path, timeout=20)
		self.dbcon.execute("""CREATE TABLE IF NOT EXISTS custom_paths
					(cpath_setting text unique, cpath_path text, cpath_header text, cpath_type text, cpath_label text)""")
		self.dbcur = self.dbcon.cursor()

	def add_cpath_to_database(self, cpath_setting, cpath_path, cpath_header, cpath_type, cpath_label):
		self.refresh_cpaths = True
		self.dbcur.execute("""INSERT OR REPLACE INTO custom_paths VALUES (?, ?, ?, ?, ?)""",
							(cpath_setting, cpath_path, cpath_header, cpath_type, cpath_label))
		self.dbcon.commit()

	def remove_cpath_from_database(self, cpath_setting):
		self.refresh_cpaths = True
		self.dbcur.execute('DELETE FROM custom_paths WHERE cpath_setting = ?', (cpath_setting,))
		self.dbcon.commit()

	def fetch_current_cpaths(self):
		current_cpaths = self.dbcur.execute(
			"""SELECT * FROM custom_paths WHERE cpath_setting LIKE %s""" % self.cpath_lookup).fetchall()
		try: current_cpaths.sort(key=lambda k: k[0])
		except: pass
		return current_cpaths

	def make_media_xml(self, active_cpaths):
		if not self.refresh_cpaths: return
		if not active_cpaths: return
		if 'category_top' in active_cpaths[0][0]:
			item = active_cpaths[0]
			xml_file = 'special://skin/xml/%s.xml' % (movies_categories_top_xml if self.media_type == 'movie' else tvshows_categories_top_xml)
			list_id = '19009' if self.media_type == 'movie' else '22009'
			final_format = xmls.category_top_xml.format(main_include=self.main_include, cpath_path=item[1], cpath_header=item[2], cpath_list_id=list_id)
			if not '&amp;' in final_format: final_format = final_format.replace('&', '&amp;')
		elif 'category_bottom' in active_cpaths[0][0]:
			item = active_cpaths[0]
			xml_file = 'special://skin/xml/%s.xml' % (movies_categories_bottom_xml if self.media_type == 'movie' else tvshows_categories_bottom_xml)
			list_id = '19025' if self.media_type == 'movie' else '22025'
			final_format = xmls.category_bottom_xml.format(main_include=self.main_include, cpath_path=item[1], cpath_header=item[2], cpath_list_id=list_id)
			if not '&amp;' in final_format: final_format = final_format.replace('&', '&amp;')
		elif 'main_menu' in active_cpaths[0][0]:
			item = active_cpaths[0]
			xml_file = 'special://skin/xml/%s.xml' % (movies_main_menu_xml if self.media_type == 'movie' else tvshows_main_menu_xml)
			main_menu_xml = xmls.main_menu_movies_xml if self.media_type == 'movie' else xmls.main_menu_tvshows_xml
			final_format = main_menu_xml.format(main_menu_path=item[1])
			if not '&amp;' in final_format: final_format = final_format.replace('&', '&amp;')
		else:
			xml_file = 'special://skin/xml/%s.xml' % (movies_widgets_xml if self.media_type == 'movie' else tvshows_widgets_xml)
			list_id = 19010 if self.media_type == 'movie' else 22010
			final_format = xmls.media_xml_start.format(main_include=self.main_include)
			if not active_cpaths: active_cpaths = [('', '', '', 'WidgetListPoster', '')]
			for item in active_cpaths:
				body = xmls.media_xml_body.format(cpath_type=item[3], cpath_path=item[1], cpath_header=item[2], cpath_list_id=list_id)
				if not '&amp;' in body: final_format += body.replace('&', '&amp;')
				list_id += 1
			final_format += xmls.media_xml_end
		with xbmcvfs.File(xml_file, 'w') as f: f.write(final_format)
		Thread(target=self.reload_skin).start()

	def manage_widgets(self):
		active_cpaths = self.fetch_current_cpaths()
		display_cpath_list = []
		display_cpath_list_append = display_cpath_list.append
		for count, item in enumerate(active_cpaths, 1):
			cpath_setting = item[0]
			name = 'Widget %s : %s' % (count, item[4])
			display_cpath_list_append((name, cpath_setting, True))
		len_display_cpaths = len(display_cpath_list)
		if len_display_cpaths < max_widgets:
			cpaths_number = len_display_cpaths + 1
			cpath_setting = '%s.%s' % (self.cpath_setting, cpaths_number)
			name = 'Widget %s :' % cpaths_number
			display_cpath_list_append((name, cpath_setting, False))
		hide_busy_dialog()
		choice = dialog.select('Choose Widget', [i[0] for i in display_cpath_list])
		if choice == -1: return self.make_media_xml(active_cpaths)
		self.chosen_cpath = display_cpath_list[choice]
		self.last_cpath = self.chosen_cpath[2]
		self.cpath_maker()
		return self.manage_widgets()

	def manage_category_top_widget(self):
		cpath_path, cpath_header = self.cpath_maker()
		if cpath_path is None: return
		self.add_cpath_to_database(self.cpath_setting, cpath_path, cpath_header, '', '')
		self.make_media_xml([(self.cpath_setting, cpath_path, cpath_header, '', '')])

	def manage_category_bottom_widget(self):
		cpath_path, cpath_header = self.cpath_maker()
		if cpath_path is None: return
		self.add_cpath_to_database(self.cpath_setting, cpath_path, cpath_header, '', '')
		self.make_media_xml([(self.cpath_setting, cpath_path, cpath_header, '', '')])

	def manage_main_menu_path(self):
		cpath_path = self.cpath_maker()
		if not cpath_path: return
		self.add_cpath_to_database(self.cpath_setting, cpath_path, '', '', '')
		self.make_media_xml([(self.cpath_setting, cpath_path, '', '', '')])
	
	def reload_skin(self):
		if window.getProperty('fen.clear_path_refresh') == 'true': return
		window.setProperty('fen.clear_path_refresh', 'true')
		while xbmcgui.getCurrentWindowId() == 10035: xbmc.sleep(500)
		window.setProperty('fen.clear_path_refresh', '')
		xbmc.sleep(200)
		xbmc.executebuiltin('ReloadSkin()')

	def clean_header(self, header):
		return header.replace('[B]', '').replace('[/B]', '').replace(' >>', '')

	def cpath_maker(self, header=None, path=None):
		show_busy_dialog()
		if header: header = self.clean_header(header)
		if path: folders = [('Use [B]%s[/B] As Path' % header, 'set_path')]
		else:
			folders = [('Clear Current Path', 'clear_path')] if self.last_cpath else []
			path = 'addons://sources/video'
		result = files_get_directory(path)
		if result:
			folders.extend([('%s >>' % i['label'], i['file']) for i in result if i['file'].startswith('plugin://') and i['filetype'] == 'directory'])
			hide_busy_dialog()
			choice = dialog.select('Choose Path', [i[0] for i in folders])
			if choice == -1:
				if 'main_menu' in self.cpath_setting: return None
				else: return None, None
			choice = folders[choice]			
			if choice[1] == 'set_path':
				if 'main_menu' in self.cpath_setting: return path
				header = dialog.input('Label', defaultt=header)
				if not header: return None, None
				if 'category_top' in self.cpath_setting: return path, header
				if 'category_bottom' in self.cpath_setting: return path, header
				types = (('Poster', 'WidgetListPoster'), ('Landscape', 'WidgetListLandscape'), ('Episode', 'WidgetListEpisodes'))
				choice = dialog.select('Choose Type', [i[0] for i in types])
				if choice == -1: return
				_type = types[choice][1]
				label_type = types[choice][0]
				setting_label = '%s | %s' % (header, label_type)
				self.add_cpath_to_database(self.chosen_cpath[1], path, header, _type, setting_label)
			elif choice[1] == 'clear_path':
				if 'category_top' in self.cpath_setting or 'main_menu' in self.cpath_setting: self.remove_cpath_from_database(self.cpath_setting)
				if 'category_bottom' in self.cpath_setting or 'main_menu' in self.cpath_setting: self.remove_cpath_from_database(self.cpath_setting)
				else: self.remove_cpath_from_database(self.chosen_cpath[1])
			else: return self.cpath_maker(choice[0], choice[1])
		else: hide_busy_dialog()
		try: dialog.close()
		except: pass

	def remake_cpaths(self):
		self.refresh_cpaths = True
		current_cpaths = self.fetch_current_cpaths()
		if current_cpaths: self.make_media_xml(current_cpaths)
		else: self.make_default_xml()

	def make_default_xml(self):
		item = default_xmls[self.cpath_setting]
		final_format = item[1].format(includes_type=item[2])
		xml_file = 'special://skin/xml/%s.xml' % item[0]
		with xbmcvfs.File(xml_file, 'w') as f: f.write(final_format)
		Thread(target=self.reload_skin).start()


def remake_all_cpaths(silent=False):
	for item in ('movie.widget', 'tvshow.widget', 'movie.category_top_widget', 'movie.category_bottom_widget', 'tvshow.category_top_widget', 'tvshow.category_bottom_widget', 'movie.main_menu', 'tvshow.main_menu'): CPaths(item).remake_cpaths()
	if not silent: xbmcgui.Dialog().ok('FENtastic', 'Menus and Widgets Remade')

def files_get_directory(directory, properties=['title', 'file', 'thumbnail']):
	command = {'jsonrpc': '2.0', 'id': 0, 'method': 'Files.GetDirectory', 'params': {'directory': directory, 'media': 'files', 'properties': properties}}
	result = get_jsonrpc(command)
	return result.get('files', None)

def get_jsonrpc(request):
	response = xbmc.executeJSONRPC(json.dumps(request))
	result = json.loads(response)
	return result.get('result', None)

def show_busy_dialog():
	return xbmc.executebuiltin('ActivateWindow(busydialognocancel)')

def hide_busy_dialog():
	xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
	xbmc.executebuiltin('Dialog.Close(busydialog)')