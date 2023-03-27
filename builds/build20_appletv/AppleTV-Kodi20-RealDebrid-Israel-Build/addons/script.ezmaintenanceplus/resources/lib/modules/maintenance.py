import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib
import re
import os

# Code to map the old translatePath
try:
    translatePath = xbmcvfs.translatePath
except AttributeError:
    translatePath = xbmc.translatePath

thumbnailPath = translatePath('special://thumbnails');
cachePath = os.path.join(translatePath('special://home'), 'cache')
tempPath = translatePath('special://temp')
addonPath = os.path.join(os.path.join(translatePath('special://home'), 'addons'),'script.ezmaintenance')

mediaPath = os.path.join(addonPath, 'media')
databasePath = translatePath('special://database')
THUMBS    =  translatePath(os.path.join('special://home/userdata/Thumbnails',''))

addon_id = 'script.ezmaintenanceplus'
fanart = translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
iconpath = translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
class cacheEntry:
    def __init__(self, namei, pathi):
        self.name = namei
        self.path = pathi

def clearCache(mode='verbose'):
    if os.path.exists(cachePath)==True:
        for root, dirs, files in os.walk(cachePath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:

                    for f in files:
                        try:
                            if (f == "xbmc.log" or f == "xbmc.old.log" or f == "kodi.log" or f == "kodi.old.log" or f == "archive_cache" or f == "commoncache.db" or f == "commoncache.socket" or f == "temp"): continue
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            if (d == "archive_cache" or d == "temp"): continue
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass

            else:
                pass
    if os.path.exists(tempPath)==True:
        for root, dirs, files in os.walk(tempPath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    try:
                        if (f == "xbmc.log" or f == "xbmc.old.log" or f == "kodi.log" or f == "kodi.old.log" or f == "archive_cache" or f == "commoncache.db" or f == "commoncache.socket" or f == "temp"): continue
                        os.unlink(os.path.join(root, f))
                    except:
                        pass
                for d in dirs:
                    try:
                        if (d == "archive_cache" or d == "temp"): continue
                        shutil.rmtree(os.path.join(root, d))
                    except:
                        pass

            else:
                pass
    if xbmc.getCondVisibility('system.platform.ATV2'):
        atv2_cache_a = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')

        for root, dirs, files in os.walk(atv2_cache_a):
            file_count = 0
            file_count += len(files)

            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
            else:
                pass
        atv2_cache_b = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')

        for root, dirs, files in os.walk(atv2_cache_b):
            file_count = 0
            file_count += len(files)

            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
            else:
                pass

    cacheEntries = []

    for entry in cacheEntries:
        clear_cache_path = translatePath(entry.path)
        if os.path.exists(clear_cache_path)==True:
            for root, dirs, files in os.walk(clear_cache_path):
                file_count = 0
                file_count += len(files)
                if file_count > 0:
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                else:
                    pass

    if mode == 'verbose': xbmc.executebuiltin('Notification(%s, %s, %s, %s)' % ('Maintenance' , 'Clean Completed' , '3000', iconpath))

def deleteThumbnails(mode='verbose'):

    if os.path.exists(thumbnailPath)==True:
            # dialog = xbmcgui.Dialog()
            # if dialog.yesno("Delete Thumbnails", "This option deletes all thumbnails" + '\n' + "Are you sure you want to do this?"):
                for root, dirs, files in os.walk(thumbnailPath):
                    file_count = 0
                    file_count += len(files)
                    if file_count > 0:
                        for f in files:
                            try:
                                os.unlink(os.path.join(root, f))
                            except:
                                pass


    if os.path.exists(THUMBS):
        try:
            for root, dirs, files in os.walk(THUMBS):
                file_count = 0
                file_count += len(files)
                # Count files and give option to delete
                if file_count > 0:
                    for f in files: os.unlink(os.path.join(root, f))
                    for d in dirs: shutil.rmtree(os.path.join(root, d))
        except:
            pass

    try:
        text13 = os.path.join(databasePath,"Textures13.db")
        os.unlink(text13)
    except:
        pass
    if mode == 'verbose': xbmc.executebuiltin('Notification(%s, %s, %s, %s)' % ('Maintenance' , 'Clean Thumbs Completed' , '3000', iconpath))

def purgePackages(mode='verbose'):

    purgePath = translatePath('special://home/addons/packages')
    dialog = xbmcgui.Dialog()
    for root, dirs, files in os.walk(purgePath):
        file_count = 0
        file_count += len(files)
    # if dialog.yesno("Delete Package Cache Files", "%d packages found."%file_count + '\n' + "Delete Them?"):
    for root, dirs, files in os.walk(purgePath):
        file_count = 0
        file_count += len(files)
        if file_count > 0:
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
            # dialog = xbmcgui.Dialog()
            # dialog.ok("Maintenance", "Deleting Packages all done")
    if mode == 'verbose': xbmc.executebuiltin('Notification(%s, %s, %s, %s)' % ('Maintenance' , 'Clean Packages Completed' , '3000', iconpath))
