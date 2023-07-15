# -*- coding: utf-8 -*-
from xbmcgui import Window
from xbmc import sleep
from xbmcaddon import Addon

# from modules.logger import logger

window = Window(10000)


def check_for_update(skin_id):
    property_version = window.getProperty("%s.installed_version" % skin_id)
    installed_version = Addon(id=skin_id).getAddonInfo("version")
    if not property_version:
        return set_installed_version(skin_id, installed_version)
    if property_version == installed_version:
        return
    from modules.cpath_maker import remake_all_cpaths, starting_widgets
    from modules.search_utils import remake_all_spaths

    set_installed_version(skin_id, installed_version)
    sleep(1000)
    remake_all_cpaths(silent=True)
    remake_all_spaths()
    starting_widgets()


def set_installed_version(skin_id, installed_version):
    window.setProperty("%s.installed_version" % skin_id, installed_version)
