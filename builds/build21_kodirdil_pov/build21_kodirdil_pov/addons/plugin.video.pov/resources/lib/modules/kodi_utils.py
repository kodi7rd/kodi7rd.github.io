import json
import sqlite3 as database
from urllib.parse import urlencode, parse_qsl
import xbmc, xbmcgui, xbmcplugin, xbmcvfs
from xbmcaddon import Addon

window, dialog, progressDialog, progressDialogBG = xbmcgui.Window(10000), xbmcgui.Dialog(), xbmcgui.DialogProgress(), xbmcgui.DialogProgressBG()
player, xbmc_player, monitor, xbmc_monitor, execJSONRPC = xbmc.Player(), xbmc.Player, xbmc.Monitor(), xbmc.Monitor, xbmc.executeJSONRPC
get_infolabel, get_addoninfo, get_visibility = xbmc.getInfoLabel, Addon().getAddonInfo, xbmc.getCondVisibility
window_xml_info_action, window_xml_dialog = xbmcgui.ACTION_SHOW_INFO, xbmcgui.WindowXMLDialog
window_xml_closing_actions = (xbmcgui.ACTION_PARENT_DIR, xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_STOP, xbmcgui.ACTION_NAV_BACK)
window_xml_selection_actions = (xbmcgui.ACTION_SELECT_ITEM, xbmcgui.ACTION_MOUSE_START)
window_xml_context_actions = (xbmcgui.ACTION_CONTEXT_MENU, xbmcgui.ACTION_MOUSE_RIGHT_CLICK, xbmcgui.ACTION_MOUSE_LONG_CLICK)
window_xml_left_action, window_xml_right_action = xbmcgui.ACTION_MOVE_LEFT, xbmcgui.ACTION_MOVE_RIGHT
window_xml_up_action, window_xml_down_action = xbmcgui.ACTION_MOVE_UP, xbmcgui.ACTION_MOVE_DOWN

navigator_db   = 'special://profile/addon_data/plugin.video.pov/navigator.db'
watched_db     = 'special://profile/addon_data/plugin.video.pov/watched.db'
favourites_db  = 'special://profile/addon_data/plugin.video.pov/favourites.db'
views_db       = 'special://profile/addon_data/plugin.video.pov/views.db'
trakt_db       = 'special://profile/addon_data/plugin.video.pov/traktcache4.db'
mdbl_db        = 'special://profile/addon_data/plugin.video.pov/mdblcache.db'
maincache_db   = 'special://profile/addon_data/plugin.video.pov/maincache.db'
metacache_db   = 'special://profile/addon_data/plugin.video.pov/metacache.db'
debridcache_db = 'special://profile/addon_data/plugin.video.pov/debridcache.db'
external_db    = 'special://profile/addon_data/plugin.video.pov/providerscache2.db'
databases_path = 'special://profile/addon_data/plugin.video.pov/'
packages_path  = 'special://home/addons/packages/'

current_dbs           = ('settings.xml', 'debridcache.db', 'favourites.db', 'maincache.db', 'metacache.db', 'fenomundesirables.db',
						'navigator.db', 'providerscache2.db', 'traktcache4.db', 'mdblcache.db', 'views.db', 'watched.db', 'fenomcache.db')
movie_dict_removals   = ('tmdblogo', 'fanart_added', 'cast', 'poster', 'rootname', 'imdb_id', 'tmdb_id', 'tvdb_id', 'all_trailers',
						'fanart', 'banner', 'clearlogo', 'clearart', 'landscape', 'discart', 'original_title', 'english_title', 'extra_info',
						'alternative_titles', 'country_codes', 'fanarttv_fanart', 'fanarttv_poster', 'fanart2', 'poster2')
tvshow_dict_removals  = ('tmdblogo', 'fanart_added', 'cast', 'poster', 'rootname', 'imdb_id', 'tmdb_id', 'tvdb_id', 'all_trailers',
						'fanart', 'banner', 'clearlogo', 'clearart', 'landscape', 'discart', 'original_title', 'english_title', 'extra_info',
						'alternative_titles', 'country_codes', 'fanarttv_fanart', 'fanarttv_poster', 'fanart2', 'poster2',
						'total_episodes', 'total_seasons', 'total_aired_eps', 'season_summary', 'season_data')
episode_dict_removals = ('thumb', 'guest_stars', 'episode_type')
myvideos_db_paths     = {19: '119', 20: '121', 21: '131'}

def logger(heading, function):
	xbmc.log('>> %s <<: %s' % (heading, function), 1)

def database_connect(file, **kwargs):
	return database.connect(translate_path(file), **kwargs)

def media_path(*args):
	path = 'special://home/addons/plugin.video.pov/resources/skins/Default/media/'
	return '%s%s' % (path, '/'.join(args)) if args else path

def get_property(prop):
	return window.getProperty(prop)

def set_property(prop, value):
	return window.setProperty(prop, value)

def clear_property(prop):
	return window.clearProperty(prop)

def addon(addon_id='plugin.video.pov'):
	return Addon(id=addon_id)

def addon_installed(addon_id):
	return get_visibility('System.HasAddon(%s)' % addon_id)

def add_item(handle, url, listitem, isFolder):
	xbmcplugin.addDirectoryItem(handle, url, listitem, isFolder)

def add_items(handle, item_list):
	xbmcplugin.addDirectoryItems(handle, item_list)

def set_content(handle, content):
	xbmcplugin.setContent(handle, content)

def set_category(handle, category):
	xbmcplugin.setPluginCategory(handle, category)

def set_sort_method(handle, method):
	if method == 'episodes': sort_method = xbmcplugin.SORT_METHOD_EPISODE
	elif method == 'files': sort_method = xbmcplugin.SORT_METHOD_FILE
	elif method == 'label': sort_method = xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE#label
	else: sort_method = xbmcplugin.SORT_METHOD_UNSORTED
	xbmcplugin.addSortMethod(handle, sort_method)

def end_directory(handle, cacheToDisc=None):
	if cacheToDisc is None: cacheToDisc = get_property('pov_kodi_menu_cache') == 'true'
	xbmcplugin.endOfDirectory(handle, cacheToDisc=cacheToDisc)

def set_resolvedurl(handle, item):
	xbmcplugin.setResolvedUrl(handle, True, item)

def make_cast_list(cast=None):
	if not cast: return []
	return [xbmc.Actor(**actor) for actor in cast]

def make_playlist(_type='video'):
	return xbmc.PlayList(xbmc.PLAYLIST_VIDEO) if _type == 'video' else xbmc.PlayList(xbmc.PLAYLIST_MUSIC)

def convert_language(lang, format='long'):
	return xbmc.convertLanguage(lang, xbmc.ISO_639_2 if format == 'long' else xbmc.ISO_639_1)

def supported_media():
	return xbmc.getSupportedMedia('video')

def path_exists(path):
	return xbmcvfs.exists(path)

def make_directory(path):
	xbmcvfs.mkdir(path)

def make_directorys(path):
	xbmcvfs.mkdirs(path)

def open_file(file, mode='r'):
	return xbmcvfs.File(file, mode)

def copy_file(source, destination):
	return xbmcvfs.copy(source, destination)

def delete_file(_file):
	xbmcvfs.delete(_file)

def rename_file(old, new):
	xbmcvfs.rename(old, new)

def list_dirs(location):
	return xbmcvfs.listdir(location)

def make_listitem():
	return xbmcgui.ListItem(offscreen=True)

def local_string(string):
	try: _string = int(string)
	except: return string
	try: _string = str(Addon().getLocalizedString(_string))
	except: _string = Addon().getLocalizedString(_string)
	return _string or string

def translate_path(path):
	return xbmcvfs.translatePath(path)

def sleep(time):
	return xbmc.sleep(time)

def execute_builtin(command):
	return xbmc.executebuiltin(command)

def get_kodi_version():
	return int(get_infolabel('System.BuildVersion')[0:2])

def skin_location():
	return 'vop.oediv.nigulp/snodda/emoh//:laiceps'[::-1]

def current_skin():
	return xbmc.getSkinDir()

def current_window_id():
	return xbmcgui.Window(xbmcgui.getCurrentWindowId())

def get_video_database_path():
	return 'special://profile/Database/MyVideos%s.db' % myvideos_db_paths[get_kodi_version()]

def show_busy_dialog():
	return execute_builtin('ActivateWindow(busydialognocancel)')

def hide_busy_dialog():
	execute_builtin('Dialog.Close(busydialognocancel)')
	execute_builtin('Dialog.Close(busydialog)')

def close_all_dialog():
	execute_builtin('Dialog.Close(all,true)')

def container_content():
	return get_infolabel('Container.Content')

def external_browse():
	return 'pov' not in get_infolabel('Container.PluginName')

def widget_refresh():
	return execute_builtin('UpdateLibrary(video,special://skin/foo)')

def container_refresh():
	return execute_builtin('Container.Refresh')

def ok_dialog(heading='POV', text='', highlight='dodgerblue', ok_label=local_string(32839), top_space=False):
#	from windows import open_window
	if isinstance(heading, int): heading = local_string(heading)
	if isinstance(text, int): text = local_string(text)
	if not text: text = '[CR]%s' % local_string(32760)
	elif top_space: text = '[CR]%s' % text
	kwargs = {'heading': heading, 'text': text, 'highlight': highlight, 'ok_label': ok_label}
#	return open_window(('windows.select_ok', 'OK'), 'select_ok.xml', **kwargs)
	return dialog.ok(heading, text)

def confirm_dialog(heading='POV', text='', highlight='dodgerblue', ok_label=local_string(32839), cancel_label=local_string(32840), top_space=False, default_control=11):
#	from windows import open_window
	if isinstance(heading, int): heading = local_string(heading)
	if isinstance(text, int): text = local_string(text)
	if isinstance(ok_label, int): ok_label = local_string(ok_label)
	if isinstance(cancel_label, int): cancel_label = local_string(cancel_label)
	if not text: text = '[CR]%s' % local_string(32580)
	elif top_space: text = '[CR]%s' % text
	kwargs = {'heading': heading, 'text': text, 'highlight': highlight, 'ok_label': ok_label, 'cancel_label': cancel_label, 'default_control': default_control}
#	return open_window(('windows.select_ok', 'YesNo'), 'select_ok.xml', **kwargs)
	return dialog.yesno(heading, text, cancel_label, ok_label)

def select_dialog(function_list, **kwargs):
	from windows import open_window
	selection = open_window(('windows.select_ok', 'Select'), 'select.xml', **kwargs)
	if selection in ([], None): return None
	if kwargs.get('multi_choice', 'false') == 'true': return [function_list[i] for i in selection]
	return function_list[selection]

def show_text(heading, text=None, file=None, font_size='small', kodi_log=False):
	from windows import open_window
	if isinstance(heading, int): heading = local_string(heading)
	heading = heading.replace('[B]', '').replace('[/B]', '')
	if file:
		with open_file(file) as f: text = f.readBytes().decode('utf-8-sig')
	if kodi_log and confirm_dialog(text=local_string(32855), ok_label=local_string(32824), cancel_label=local_string(32828), top_space=True):
		lines = []
		for line in text.splitlines(keepends=True):
			if line[0].isdigit(): lines += [line]
			else: lines[-1] += line
		text = ''.join(i for i in reversed(lines) if any(x in i.lower() for x in ('exception', 'error')))
	return open_window(('windows.textviewer', 'TextViewer'), 'textviewer.xml', heading=heading, text=text, font_size=font_size)

def notification(line1, time=3000, icon=None, sound=False):
	if isinstance(line1, int): line1 = local_string(line1)
	icon = icon or get_addoninfo('icon')
	dialog.notification('POV', line1, icon, time, sound)

def choose_view(view_type, content):
	from sys import argv
	__handle__ = int(argv[1])
	label = local_string(32547)
	fanart = get_addoninfo('fanart')
	icon = media_path('settings.png')
	params_url = build_url({'mode': 'set_view', 'view_type': view_type})
	listitem = make_listitem()
	listitem.setLabel(label)
	listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
	add_item(__handle__, params_url, listitem, False)
	set_content(__handle__, content)
	end_directory(__handle__)
	set_view_mode(view_type, content)

def set_view(view_type):
	view_id = str(current_window_id().getFocusId())
	dbcon = database_connect(views_db, isolation_level=None)
	dbcur = dbcon.cursor()
	dbcur.execute("""PRAGMA synchronous = OFF""")
	dbcur.execute("""PRAGMA journal_mode = OFF""")
	dbcur.execute("""INSERT OR REPLACE INTO views VALUES (?, ?)""", (view_type, view_id))
	set_view_property(view_type, view_id)
	notification(get_infolabel('Container.Viewmode').upper(), 1500)

def set_view_property(view_type, view_id):
	set_property('pov_%s' % view_type, view_id)

def set_view_properties():
	dbcon = database_connect(views_db, isolation_level=None)
	dbcur = dbcon.cursor()
	dbcur.execute("""PRAGMA synchronous = OFF""")
	dbcur.execute("""PRAGMA journal_mode = OFF""")
	dbcur.execute("""SELECT * FROM views""")
	view_ids = dbcur.fetchall()
	for item in view_ids: set_property('pov_%s' % item[0], item[1])

def set_view_mode(view_type, content='files'):
	if external_browse(): return
	view_id = get_property('pov_%s' % view_type)
	hold = 0
	if not view_id:
		try:
			dbcon = database_connect(views_db, isolation_level=None)
			dbcur = dbcon.cursor()
			dbcur.execute("""SELECT view_id FROM views WHERE view_type = ?""", (str(view_type),))
			view_id = dbcur.fetchone()[0]
		except: return
	try:
		sleep(100)
		while not container_content() == content:
			hold += 1
			if hold < 5000: sleep(1)
			else: return
		if view_id: execute_builtin('Container.SetViewMode(%s)' % view_id)
	except: return

def clear_view(view_type):
	if not confirm_dialog(): return
	try:
		dbcon = database_connect(views_db, isolation_level=None)
		dbcur = dbcon.cursor()
		dbcur.execute("""PRAGMA synchronous = OFF""")
		dbcur.execute("""PRAGMA journal_mode = OFF""")
		dbcur.execute("""SELECT view_type FROM views""")
		for item in dbcur.fetchall():
			dbcur.execute("""DELETE FROM views WHERE view_type = ?""", (item[0],))
			clear_property('pov_%s' % item[0])
		dbcon = database_connect('special://profile/Database/ViewModes6.db')
		dbcur = dbcon.cursor()
		dbcur.execute("""DELETE FROM view WHERE path LIKE 'plugin://plugin.video.pov/%'""")
		dbcur.connection.commit()
		dbcur.connection.close()
	except: return notification(32574, 1500)
	notification(32576, 1500)

def build_url(url_params):
	return f"{'/vop.oediv.nigulp//:nigulp'[::-1]}?{urlencode(url_params)}"

def add_dir(__handle__, url_params, list_name, iconImage=None, fanartImage=None, isFolder=True):
	if 'new_page' in url_params: list_name = f"{list_name} >> {url_params['new_page']} <<"
	fanart = fanartImage or get_addoninfo('fanart')
	icon = iconImage or media_path('item_next.png')
	url = build_url(url_params)
	listitem = make_listitem()
	listitem.setLabel(list_name)
	listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
	add_item(__handle__, url, listitem, isFolder)

def remove_meta_keys(dict_item, dict_removals):
	for k in dict_removals: dict_item.pop(k, None)
	return dict_item

def volume_checker(volume_setting):
	# 0% == -60db, 100% == 0db
	try:
		if get_visibility('Player.Muted'): return
		from modules.utils import string_alphanum_to_num
		max_volume = int(min(int(volume_setting), 100))
		current_volume_db = int(string_alphanum_to_num(get_infolabel('Player.Volume').split('.')[0]))
		current_volume_percent = int(100 - ((float(current_volume_db)/60)*100))
		if current_volume_percent > max_volume: execute_builtin('SetVolume(%d)' % int(max_volume))
	except: pass

def focus_index(index, sleep_time=100):
	sleep(sleep_time)
	current_window = current_window_id()
	focus_id = current_window.getFocusId()
	try: current_window.getControl(focus_id).selectItem(index)
	except: pass

def clean_settings_window_properties():
	clear_property('pov_settings')
	notification(32576, 1500)

def fetch_kodi_imagecache(image):
	result = None
	try:
		dbcon = database_connect('special://profile/Database/Textures13.db')
		dbcur = dbcon.cursor()
		dbcur.execute("""SELECT cachedurl FROM texture WHERE url = ?""", (image,))
		result = dbcur.fetchone()[0]
	except: pass
	return result

def set_setting(setting_id, value):
	Addon().setSetting(setting_id, value)

def get_setting(setting_id, fallback=None):
	try: settings_dict = json.loads(get_property('pov_settings'))
	except: settings_dict = make_settings_dict()
	if settings_dict is None: settings_dict = get_setting_fallback(setting_id)
	value = settings_dict.get(setting_id, '')
	if fallback is None: return value
	if value == '': return fallback
	return value

def get_setting_fallback(setting_id):
	return {setting_id: Addon().getSetting(setting_id)}

def make_settings_dict():
	import xml.etree.ElementTree as ET
	settings_dict = None
	try:
		profile_dir = 'special://profile/addon_data/plugin.video.pov/'
		if not path_exists(profile_dir): make_directorys(profile_dir)
		settings_xml = profile_dir + 'settings.xml'
		root = ET.parse(translate_path(settings_xml)).getroot()
		settings_dict = {}
		for item in root:
			setting_id = item.get('id')
			setting_value = item.text
			if setting_value is None: setting_value = ''
			dict_item = {setting_id: setting_value}
			settings_dict.update(dict_item)
		set_property('pov_settings', json.dumps(settings_dict))
	except: pass
	return settings_dict

def toggle_jump_to():
	from modules.settings import nav_jump_use_alphabet
	(setting, new_action) = ('0', local_string(32022)) if nav_jump_use_alphabet() else ('1', local_string(32023))
	set_setting('nav_jump', setting)
	container_refresh()
	notification(local_string(32851) % new_action)

def toggle_language_invoker():
	import xml.etree.ElementTree as ET
	close_all_dialog()
	sleep(100)
	current_addon_setting = get_setting('reuse_language_invoker', 'true')
	new_value = 'false' if current_addon_setting == 'true' else 'true'
	if not confirm_dialog(text=local_string(32979) % (current_addon_setting.upper(), new_value.upper())): return
	if new_value == 'true' and not confirm_dialog(text=32980, top_space=True): return
	addon_xml = translate_path('special://home/addons/plugin.video.pov/addon.xml')
	tree = ET.parse(addon_xml)
	root = tree.getroot()
	item = next(root.iter('reuselanguageinvoker'), None)
	if item is None: return notification(32574, 1500)
	item.text = new_value
	tree.write(addon_xml)
	set_setting('reuse_language_invoker', new_value)
	ok_dialog(text=32981, top_space=True)
	execute_builtin('LoadProfile(%s)' % get_infolabel('system.profilename'))

def open_settings(query, addon='plugin.video.pov'):
	hide_busy_dialog()
	if query:
		try:
			button, control = 100, 80
			menu, function = query.split('.')
			execute_builtin('Addon.OpenSettings(%s)' % addon)
			execute_builtin('SetFocus(%i)' % (int(menu) - button))
			execute_builtin('SetFocus(%i)' % (int(function) - control))
		except: execute_builtin('Addon.OpenSettings(%s)' % addon)
	else: execute_builtin('Addon.OpenSettings(%s)' % addon)

def clean_settings():
	import xml.etree.ElementTree as ET
	def _make_content(dict_object):
		content = '<settings version="2">'
		for item in dict_object:
			_id = item['id']
			if _id in active_settings:
				if 'default' in item and 'value' in item: content += '\n    <setting id="%s" default="%s">%s</setting>' % (_id, item['default'], item['value'])
				elif 'default' in item: content += '\n    <setting id="%s" default="%s"></setting>' % (_id, item['default'])
				elif 'value' in item: content += '\n    <setting id="%s">%s</setting>' % (_id, item['value'])
				else: content += '\n    <setting id="%s"></setting>'
			else: removed_append(item)
		content += '\n</settings>'
		return content
#	progressDialog.create('POV', '')
	addon_ids = ['plugin.video.pov']
	addon_settings = 'special://home/addons/%s/resources/settings.xml'
	addon_data_settings = 'special://profile/addon_data/%s/settings.xml'
	addon_names = ['POV']
	addon_data_settings_xmls = [addon_data_settings % i for i in addon_ids]
	addon_settings_xmls = [addon_settings % i for i in addon_ids]
	params = list(zip(addon_names, addon_data_settings_xmls, addon_settings_xmls))
	for count, (name, profile_xml, default_xml) in enumerate(params, 1):
		try:
#			if progressDialog.iscanceled(): break
			removed_settings = []
			active_settings = []
			current_user_settings = []
			removed_append = removed_settings.append
			active_append = active_settings.append
			current_append = current_user_settings.append
			root = ET.parse(translate_path(default_xml)).getroot()
			for item in root.findall('./category/setting'):
				setting_id = item.get('id')
				if setting_id: active_append(setting_id)
			settings_xml = profile_xml
			root = ET.parse(translate_path(settings_xml)).getroot()
			for item in root:
				dict_item = {}
				setting_id = item.get('id')
				setting_default = item.get('default')
				setting_value = item.text
				dict_item['id'] = setting_id
				if setting_value: dict_item['value'] = setting_value
				if setting_default: dict_item['default'] = setting_default
				current_append(dict_item)
			new_content = _make_content(current_user_settings)
			with open_file(settings_xml, 'w') as xml_file: xml_file.write(new_content)
			percent = int(count / len(params) * 100)
			line2 = local_string(32812) % name
			line3 = local_string(32813) % len(removed_settings)
#			progressDialog.update(percent, '[CR]%s[CR]%s' % (line2, line3))
#			sleep(500)
		except: notification(32574, 1500)
		notification(line3, 1500) if removed_settings else notification(32576, 1500)
#	progressDialog.close()

def upload_logfile():
	# Thanks 123Venom
	log_file, url = 'special://logpath/kodi.log', 'https://paste.kodi.tv/'
	if not path_exists(log_file): return ok_dialog(text='Error. Log File Not Found.', top_space=True)
	if not confirm_dialog(): return
	import requests
	show_busy_dialog()
	try:
		with open_file(log_file) as f: text = f.read().encode('utf-8', errors='ignore')
		response = requests.post('%s%s' % (url, 'documents'), data=text, timeout=10.0).json()
		if 'key' in response: ok_dialog(text=url + response['key'], top_space=True)
		else: ok_dialog(text='Error. Log Upload Failed')
	except: notification(32574, 1500)
	hide_busy_dialog()

def timeIt(func):
	# Thanks to 123Venom
	import time
	fnc_name = func.__name__
	def wrap(*args, **kwargs):
		started_at = time.perf_counter()
		result = func(*args, **kwargs)
		logger('%s.%s' % (__name__ , fnc_name), (time.perf_counter() - started_at))
		return result
	return wrap

