# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcaddon
# from modules.logger import logger

window = xbmcgui.Window(10000)

def check_for_update(skin_id):
	property_version = window.getProperty('%s.installed_version' % skin_id)
	installed_version = xbmcaddon.Addon(id=skin_id).getAddonInfo('version')
	if not property_version: return set_installed_version(skin_id, installed_version)
	if property_version == installed_version: return
	from modules.cpath_maker import remake_all_cpaths
	set_installed_version(skin_id, installed_version)
	xbmc.sleep(1000)
	remake_all_cpaths(silent=True)

def set_installed_version(skin_id, installed_version):
	window.setProperty('%s.installed_version' % skin_id, installed_version)
