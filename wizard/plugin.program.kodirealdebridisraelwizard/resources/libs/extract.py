################################################################################
#      Copyright (C) 2019 drinfernoo                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import xbmc
import xbmcgui

import sys
try:  # Python 3
    import zipfile
except ImportError:  # Python 2
    from resources.libs import zipfile

from resources.libs.common.config import CONFIG
from resources.libs.common import logging
from resources.libs.common import tools
from resources.libs.common import custom_save_data_config
from resources.libs import install


                       
########################################################################################################################################################

# KODI RD ISRAEL - Custom Save Data Config
# try:

    # is_first_install = 'true' if CONFIG.get_setting('installed') in ('false', 'ignored') else 'false'

    # logging.log("################################", level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: IS FIRST INSTALL: " + is_first_install, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPTRAKT: " + CONFIG.KEEPTRAKT, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPDEBRID: " + CONFIG.KEEPDEBRID, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPLOGIN: " + CONFIG.KEEPLOGIN, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPFENDATA: " + CONFIG.KEEPFENDATA, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPTWILIGHTDATA: " + CONFIG.KEEPTWILIGHTDATA, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPFENTASTICDATA: " + CONFIG.KEEPFENTASTICDATA, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPFAVS: " + CONFIG.KEEPFAVS, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPSOURCES: " + CONFIG.KEEPSOURCES, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPADVANCED: " + CONFIG.KEEPADVANCED, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPPROFILES: " + CONFIG.KEEPPROFILES, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPPLAYERCORE: " + CONFIG.KEEPPLAYERCORE, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPGUISETTINGS: " + CONFIG.KEEPGUISETTINGS, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPREPOS: " + CONFIG.KEEPREPOS, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPSUPER: " + CONFIG.KEEPSUPER, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPWHITELIST: " + CONFIG.KEEPWHITELIST, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY BEFORE: CONFIG.KEEPADDONS33DB: " + CONFIG.KEEPADDONS33DB, level=xbmc.LOGINFO)

    # Delete whitelist.txt if CONFIG.KEEPWHITELIST is false to avoid addons deletion.
    # if CONFIG.KEEPWHITELIST == 'false':
        # custom_save_data_config.delete_addons_whitelist_file()
        
    # Set variables value from JSON file + addons whitelist, only if NOT first install.    
    # if CONFIG.USE_GITHUB_CUSTOM_SAVE_DATA_CONFIG == 'true':
        # logging.log("CONFIG.USE_GITHUB_CUSTOM_SAVE_DATA_CONFIG is: " + CONFIG.USE_GITHUB_CUSTOM_SAVE_DATA_CONFIG + ". Checking if not first install..", level=xbmc.LOGINFO)
        
        # if is_first_install == 'true':
            # logging.log("Looks like first install. Skipping custom_save_data_config..", level=xbmc.LOGINFO)
        # else:
            # logging.log("Not first install. Starting custom_save_data_config..", level=xbmc.LOGINFO)
            # custom_save_data_config.main()
            
    # else:
        # logging.log("CONFIG.USE_GITHUB_CUSTOM_SAVE_DATA_CONFIG is: " + CONFIG.USE_GITHUB_CUSTOM_SAVE_DATA_CONFIG + ". Skipping..", level=xbmc.LOGINFO)

    # logging.log("################################", level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: IS FIRST INSTALL: " + is_first_install, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPTRAKT: " + CONFIG.KEEPTRAKT, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPDEBRID: " + CONFIG.KEEPDEBRID, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPLOGIN: " + CONFIG.KEEPLOGIN, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPFENDATA: " + CONFIG.KEEPFENDATA, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPTWILIGHTDATA: " + CONFIG.KEEPTWILIGHTDATA, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPFENTASTICDATA: " + CONFIG.KEEPFENTASTICDATA, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPFAVS: " + CONFIG.KEEPFAVS, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPSOURCES: " + CONFIG.KEEPSOURCES, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPADVANCED: " + CONFIG.KEEPADVANCED, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPPROFILES: " + CONFIG.KEEPPROFILES, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPPLAYERCORE: " + CONFIG.KEEPPLAYERCORE, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPGUISETTINGS: " + CONFIG.KEEPGUISETTINGS, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPREPOS: " + CONFIG.KEEPREPOS, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPSUPER: " + CONFIG.KEEPSUPER, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPWHITELIST: " + CONFIG.KEEPWHITELIST, level=xbmc.LOGINFO)
    # logging.log("EXTRACT.PY AFTER: CONFIG.KEEPADDONS33DB: " + CONFIG.KEEPADDONS33DB, level=xbmc.LOGINFO)
    # logging.log("################################", level=xbmc.LOGINFO)
    
# except Exception: 
    # pass
    
########################################################################################################################################################


def all(_in, _out, ignore=None, title=None, progress_dialog_bg=False):
    #####################################################
    # KODI-RD-IL
    # progress_dialog = xbmcgui.DialogProgress()
    progress_dialog = xbmcgui.DialogProgressBG() if progress_dialog_bg else xbmcgui.DialogProgress()
    #####################################################
    progress_dialog.create(CONFIG.ADDONTITLE, "Extracting Content")
    
    # return all_with_progress(_in, _out, progress_dialog, ignore, title)
    return all_with_progress(_in, _out, progress_dialog, ignore, title, progress_dialog_bg)


# def all_with_progress(_in, _out, dp, ignore, title):
def all_with_progress(_in, _out, dp, ignore, title, progress_dialog_bg):
    from resources.libs import whitelist

    count = 0
    errors = 0
    error = ''
    update = 0
    size = 0
    excludes = []

    try:
        zin = zipfile.ZipFile(_in,  'r', allowZip64=True)
    except Exception as e:
        errors += 1
        error += '%s\n' % e
        logging.log('Error Checking Zip: {0}'.format(str(e)), level=xbmc.LOGERROR)
        return update, errors, error

    white_list = whitelist.whitelist('read')
    for item in white_list:
        try:
            name, id, fold = item
        except:
            pass
        excludes.append(fold)

    nFiles = float(len(zin.namelist()))
    zipsize = tools.convert_size(sum([item.file_size for item in zin.infolist()]))

    zipit = str(_in).replace('\\', '/').split('/')
    title = title if title else zipit[-1].replace('.zip', '')

    for item in zin.infolist():
        
        try:
            str(item.filename).encode('ascii')
        except UnicodeDecodeError:
            logging.log("[ASCII Check] Illegal character found in file: {0}".format(item.filename))
            continue
        except UnicodeEncodeError:
            logging.log("[ASCII Check] Illegal character found in file: {0}".format(item.filename))
            continue
            
        count += 1
        prog = int(count / nFiles * 100)
        size += item.file_size
        file = str(item.filename).split('/')
        skip = False
        
        line1 = '{0} [COLOR {1}][B][Errors:{2}][/B][/COLOR]'.format(title,
                                                                    CONFIG.COLOR2,
                                                                    errors)
        line2 = '[COLOR {0}][B]File:[/B][/COLOR] [COLOR {1}]{2}/{3}[/COLOR] '.format(CONFIG.COLOR2,
                                                                                     CONFIG.COLOR1,
                                                                                     count,
                                                                                     int(nFiles))
        line2 += '[COLOR {0}][B]Size:[/B][/COLOR] [COLOR {1}]{2}/{3}[/COLOR]'.format(CONFIG.COLOR2,
                                                                                     CONFIG.COLOR1,
                                                                                     tools.convert_size(size),
                                                                                     zipsize)
        line3 = '[COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, item.filename)
        
        if item.filename == 'userdata/sources.xml' and CONFIG.KEEPSOURCES == 'true':
            skip = True
        elif item.filename == 'userdata/favourites.xml' and CONFIG.KEEPFAVS == 'true':
            skip = True
        elif item.filename == 'userdata/profiles.xml' and CONFIG.KEEPPROFILES == 'true':
            skip = True
        elif item.filename == 'userdata/guisettings.xml' and CONFIG.KEEPGUISETTINGS == 'true':
            skip = True
        elif item.filename == 'userdata/playercorefactory.xml' and CONFIG.KEEPPLAYERCORE == 'true':
            skip = True
        elif item.filename == 'userdata/advancedsettings.xml' and CONFIG.KEEPADVANCED == 'true':
            skip = True
        # KODI RD ISRAEL - Skip Addons33.db if CONFIG.KEEPADDONS33DB is enabled.
        elif item.filename == 'userdata/Database/Addons33.db' and CONFIG.KEEPADDONS33DB == 'true':
            logging.log("KODI RD ISRAEL - EXTRACT.PY: Skipping Addons33.db - CONFIG.KEEPADDONS33DB is: {0}".format(CONFIG.KEEPADDONS33DB))
            skip = True
        elif file[0] == 'addons' and file[1] in excludes:
            skip = True
        elif file[0] == 'userdata' and file[1] == 'addon_data' and file[2] in excludes:
            skip = True
        elif file[-1] in CONFIG.LOGFILES:
            skip = True
        elif file[-1] in CONFIG.EXCLUDE_FILES:
            skip = True
        elif file[-1].endswith('.csv'):
            skip = True
        elif not str(item.filename).find('plugin.program.super.favourites') == -1 and CONFIG.KEEPSUPER == 'true':
            skip = True
        elif not str(item.filename).find(CONFIG.ADDON_ID) == -1 and ignore is None:
            skip = True
        if skip:
            logging.log("Skipping: {0}".format(item.filename))
        else:
            try:
                zin.extract(item, _out)
            except Exception as e:
                errormsg = "[COLOR {0}]File:[/COLOR] [COLOR {1}]{2}[/COLOR]\n".format(CONFIG.COLOR2,
                                                                                      CONFIG.COLOR1,
                                                                                      file[-1])
                errormsg += "[COLOR {0}]Folder:[/COLOR] [COLOR {1}]{2}[/COLOR]\n".format(CONFIG.COLOR2,
                                                                                         CONFIG.COLOR1,
                                                                                         item.filename.replace(file[-1], ''))
                errormsg += "[COLOR {0}]Error:[/COLOR] [COLOR {1}]{2}[/COLOR]\n\n".format(CONFIG.COLOR2,
                                                                                          CONFIG.COLOR1,
                                                                                          str(e).replace('\\\\', '\\')
                                                                                          .replace("'{0}'"
                                                                                          .format(item.filename), ''))
                errors += 1
                error += errormsg
                logging.log('Error Extracting: {0}({1})'.format(item.filename, str(e)), level=xbmc.LOGERROR)
                pass
        dp.update(prog, line1 + '\n' + line2 + '\n' + line3)
    #####################################################
    # KODI-RD-IL
        if not progress_dialog_bg:
            if dp.iscanceled():
                break
            
    if not progress_dialog_bg:
        if dp.iscanceled():
            dp.close()
            logging.log_notify(CONFIG.ADDONTITLE,
                               "[COLOR {0}]Extract Cancelled[/COLOR]".format(CONFIG.COLOR2))
            sys.exit()
    #####################################################
        
    # KODI_RD_ISRAEL    
    install.restore_fentasticdata()
    
    return prog, errors, error
