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

import os

from resources.libs import check
from resources.libs import db
from resources.libs import extract
from resources.libs import install
from resources.libs import skin
from resources.libs.common import logging
from resources.libs.common import tools
from resources.libs.common.config import CONFIG
from resources.libs.downloader import Downloader


class Wizard:

    def __init__(self):
        tools.ensure_folders(CONFIG.PACKAGES)
        
        self.dialog = xbmcgui.Dialog()
        self.dialogProgress = xbmcgui.DialogProgress()

    def _prompt_for_wipe(self):
        # Should we wipe first?
        if self.dialog.yesno(CONFIG.ADDONTITLE,
                           "[COLOR {0}]Do you wish to restore your".format(CONFIG.COLOR2) +'\n' + "Kodi configuration to default settings" + '\n' + "Before installing the build backup?[/COLOR]",
                           nolabel='[B][COLOR red]No[/COLOR][/B]',
                           yeslabel='[B][COLOR springgreen]Yes[/COLOR][/B]'):
            install.wipe()

    def build(self, name, over=False):
        # if action == 'normal':
            # if CONFIG.KEEPTRAKT == 'true':
                # from resources.libs import traktit
                # traktit.auto_update('all')
                # CONFIG.set_setting('traktnextsave', tools.get_date(days=3, formatted=True))
            # if CONFIG.KEEPDEBRID == 'true':
                # from resources.libs import debridit
                # debridit.auto_update('all')
                # CONFIG.set_setting('debridnextsave', tools.get_date(days=3, formatted=True))
            # if CONFIG.KEEPLOGIN == 'true':
                # from resources.libs import loginit
                # loginit.auto_update('all')
                # CONFIG.set_setting('loginnextsave', tools.get_date(days=3, formatted=True))

        temp_kodiv = int(CONFIG.KODIV)
        buildv = int(float(check.check_build(name, 'kodi')))

        if not temp_kodiv == buildv:
            warning = True
        else:
            warning = False

        if warning:
            yes_pressed = self.dialog.yesno("{0} - [COLOR red]WARNING!![/COLOR]".format(CONFIG.ADDONTITLE), '[COLOR {0}]There is a chance that the skin will not appear correctly'.format(CONFIG.COLOR2) + '\n' + 'When installing a {0} build on a Kodi {1} install'.format(check.check_build(name, 'kodi'), CONFIG.KODIV) + '\n' + 'Would you still like to install: [COLOR {0}]{1} v{2}[/COLOR]?[/COLOR]'.format(CONFIG.COLOR1, name, check.check_build(name, 'version')), nolabel='[B][COLOR red]No, Cancel[/COLOR][/B]', yeslabel='[B][COLOR springgreen]Yes, Install[/COLOR][/B]')
        else:
            if over:
                yes_pressed = 1
            else:
                yes_pressed = self.dialog.yesno(CONFIG.ADDONTITLE, '[COLOR {0}]האם ברצונך להוריד ולהתקין את '.format(CONFIG.COLOR2) + '[COLOR {0}]{1} v{2}[/COLOR]?[/COLOR]'.format(CONFIG.COLOR1, name, check.check_build(name,'version')), nolabel='[B][COLOR red]ביטול[/COLOR][/B]', yeslabel='[B][COLOR springgreen]התקנה[/COLOR][/B]')
        if yes_pressed:
            CONFIG.clear_setting('build')
            buildzip = check.check_build(name, 'url')
            zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

            self.dialogProgress.create(CONFIG.ADDONTITLE, '[COLOR {0}][B]Downloading:[/B][/COLOR] [COLOR {1}]{2} v{3}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name, check.check_build(name, 'version')) + '\n' + 'Please Wait')

            lib = os.path.join(CONFIG.MYBUILDS, '{0}.zip'.format(zipname))
            
            try:
                os.remove(lib)
            except:
                pass

            Downloader().download(buildzip, lib)
            xbmc.sleep(500)
            
            if os.path.getsize(lib) == 0:
                try:
                    os.remove(lib)
                except:
                    pass
                    
                return
                
            install.wipe()
                
            skin.look_and_feel_data('save')
            
            title = '[COLOR {0}][B]Installing:[/B][/COLOR] [COLOR {1}]{2} v{3}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name, check.check_build(name, 'version'))
            self.dialogProgress.update(0, title + '\n' + 'Please Wait')
            percent, errors, error = extract.all(lib, CONFIG.HOME, title=title)
            
            skin.skin_to_default('Build Install')

            if int(float(percent)) > 0:
                db.fix_metas()
                CONFIG.set_setting('buildname', name)
                CONFIG.set_setting('buildversion', check.check_build(name, 'version'))
                CONFIG.set_setting('buildtheme', '')
                CONFIG.set_setting('latestversion', check.check_build(name, 'version'))
                CONFIG.set_setting('nextbuildcheck', tools.get_date(days=CONFIG.UPDATECHECK, formatted=True))
                CONFIG.set_setting('installed', 'true')
                CONFIG.set_setting('extract', percent)
                CONFIG.set_setting('errors', errors)
                logging.log('INSTALLED {0}: [ERRORS:{1}]'.format(percent, errors))

                # try:
                    # os.remove(lib)
                # except:
                    # pass

                if int(float(errors)) > 0:
                    yes_pressed = self.dialog.yesno(CONFIG.ADDONTITLE,
                                       '[COLOR {0}][COLOR {1}]{2} v{3}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name, check.check_build(name, 'version')) +'\n' + 'Completed: [COLOR {0}]{1}{2}[/COLOR] [Errors:[COLOR {3}]{4}[/COLOR]]'.format(CONFIG.COLOR1, percent, '%', CONFIG.COLOR1, errors) + '\n' + 'Would you like to view the errors?[/COLOR]',
                                       nolabel='[B][COLOR red]No Thanks[/COLOR][/B]',
                                       yeslabel='[B][COLOR springgreen]View Errors[/COLOR][/B]')
                    if yes_pressed:
                        from resources.libs.gui import window
                        window.show_text_box("Viewing Build Install Errors", error)
                self.dialogProgress.close()

                from resources.libs.gui.build_menu import BuildMenu
                themecount = BuildMenu().theme_count(name)

                if themecount > 0:
                    self.theme(name)

                db.addon_database(CONFIG.ADDON_ID, 1)
                # db.force_check_updates(over=True)
                # if os.path.exists(os.path.join(CONFIG.USERDATA, '.enableall')):
                    # CONFIG.set_setting('enable_all', 'true')
                
                #########################################################################################################
                # KODI-RD-IL
                # Enable all addons in build's ZIP file.
                installed = db.grab_addons(lib)
                db.addon_database(installed, 1, True)
                try:
                    os.remove(lib)
                except:
                    pass
                
                from resources.libs.gui import window
                note_id, msg = window.split_notify(CONFIG.QUICK_UPDATE_NOTIFICATION_URL)
                if note_id:
                    # Don't show the quick update notification window after build install (first build launch notification window will show), no quick update will be installed (wizard's noteid == latest noteid from URL)
                    CONFIG.set_setting('quick_update_notedismiss', 'true')
                    CONFIG.set_setting('quick_update_noteid', note_id)
                # Show first build launch notification window
                CONFIG.set_setting('notedismiss', 'false')
                # Show first build launch build skin switch notification window
                CONFIG.set_setting('build_skin_switch_notifcation_dismiss', 'false')
                #########################################################################################################

                # self.dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}]התקנת הבילד הסתיימה. לחץ אישור/OK כדי לסגור את קודי. לאחר מכן, הפעל אותו מחדש.[/COLOR]".format(CONFIG.COLOR2))
                # tools.kill_kodi(over=True)
                self.force_close_kodi_in_5_seconds(dialog_header="התקנת הבילד הסתיימה בהצלחה")
            else:
                from resources.libs.gui import window
                window.show_text_box("Viewing Build Install Errors", error)
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]התקנת בילד: בוטלה![/COLOR]'.format(CONFIG.COLOR2))

    def gui(self, name, over=False):
        if name == CONFIG.get_setting('buildname'):
            if over:
                yes_pressed = 1
            else:
                yes_pressed = self.dialog.yesno(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]האם ברצונך לבצע עדכון מהיר עבור:'.format(CONFIG.COLOR2) + '\n' + '[COLOR {0}]{1}[/COLOR]?[/COLOR]'.format(CONFIG.COLOR1, name),
                                   nolabel='[B][COLOR red]ביטול[/COLOR][/B]',
                                   yeslabel='[B][COLOR springgreen]עדכון מהיר[/COLOR][/B]')
        else:
            yes_pressed = self.dialog.yesno("{0} - [COLOR red]!שים לב[/COLOR]".format(CONFIG.ADDONTITLE),
                               "[COLOR {0}][COLOR {1}]{2}[/COLOR] - הבילד עדיין לא מותקן".format(CONFIG.COLOR2, CONFIG.COLOR1, name) + '\n' + "יש קודם כל לבצע התקנה מלאה של הבילד![/COLOR]",
                               nolabel='[B][COLOR red]ביטול[/COLOR][/B]',
                               yeslabel='[B][COLOR springgreen]המשך בכל זאת[/COLOR][/B]')
        if yes_pressed:
            guizip = check.check_build(name, 'gui')
            zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

            response = tools.open_url(guizip, check=True)
            if not response:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]לא קיים עדכון![/COLOR]'.format(CONFIG.COLOR2))
                return

            self.dialogProgress.create(CONFIG.ADDONTITLE, '[COLOR {0}][B]Downloading GuiFix:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name))

            lib = os.path.join(CONFIG.PACKAGES, '{0}_guisettings.zip'.format(zipname))
            
            try:
                os.remove(lib)
            except:
                pass

            Downloader().download(guizip, lib)
            xbmc.sleep(500)
            
            if os.path.getsize(lib) == 0:
                try:
                    os.remove(lib)
                except:
                    pass
                    
                return
            
            title = '[COLOR {0}][B]Installing:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name)
            self.dialogProgress.update(0, title + '\n' + 'Please Wait')
            extract.all(lib, CONFIG.HOME, title=title)
            self.dialogProgress.close()
            skin.skin_to_default('Build Install')
            skin.look_and_feel_data('save')
            installed = db.grab_addons(lib)
            db.addon_database(installed, 1, True)

            self.dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}]עדכון מהיר הסתיים. לחץ אישור/OK כדי לסגור את קודי. לאחר מכן, הפעל אותו מחדש.[/COLOR]".format(CONFIG.COLOR2))
            tools.kill_kodi(over=True)
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]עדכון מהיר: בוטל![/COLOR]'.format(CONFIG.COLOR2))
                               
    #####################################################
    # KODI-RD-IL
    def quick_update(self, name, auto_quick_update="false"):

        auto_quick_update = True if auto_quick_update=="true" else False
        
        if name == CONFIG.get_setting('buildname'):
            if auto_quick_update:
                yes_pressed = 1
            else:
                yes_pressed = self.dialog.yesno(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]האם ברצונך לבצע עדכון מהיר עבור:'.format(CONFIG.COLOR2) + '\n' + '[COLOR {0}]{1}[/COLOR]?[/COLOR]'.format(CONFIG.COLOR1, name),
                                   nolabel='[B][COLOR red]ביטול[/COLOR][/B]',
                                   yeslabel='[B][COLOR springgreen]עדכון מהיר[/COLOR][/B]')
        else:
            yes_pressed = self.dialog.yesno("{0} - [COLOR red]!שים לב[/COLOR]".format(CONFIG.ADDONTITLE),
                               "[COLOR {0}][COLOR {1}]{2}[/COLOR] - הבילד עדיין לא מותקן".format(CONFIG.COLOR2, CONFIG.COLOR1, name) + '\n' + "יש קודם כל לבצע התקנה מלאה של הבילד![/COLOR]",
                               nolabel='[B][COLOR red]ביטול[/COLOR][/B]',
                               yeslabel='[B][COLOR springgreen]המשך בכל זאת[/COLOR][/B]')
        if yes_pressed:
            guizip = check.check_build(name, 'gui')
            zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

            response = tools.open_url(guizip, check=True)
            if not response:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]לא קיים עדכון מהיר![/COLOR]'.format(CONFIG.COLOR2))
                return False

            self.dialogProgress.create(CONFIG.ADDONTITLE, '[COLOR {0}][B]מוריד עדכון מהיר עבור:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name))
            xbmc.sleep(2500)
            self.dialogProgress.close()

            lib = os.path.join(CONFIG.PACKAGES, '{0}_quick_update.zip'.format(zipname))
            
            try:
                os.remove(lib)
            except:
                pass

            Downloader().download(guizip, lib)
            xbmc.sleep(500)
            
            if os.path.getsize(lib) == 0:
                try:
                    os.remove(lib)
                except:
                    pass
                    
                return False
            
            title = '[COLOR {0}][B]Installing:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name)
            extract.all(lib, CONFIG.HOME, title=title)
            # skin.skin_to_default('Build Install')
            # skin.look_and_feel_data('save')
            installed = db.grab_addons(lib)
            db.addon_database(installed, 1, True)
                               
            if not auto_quick_update:
                CONFIG.set_setting('quick_update_notedismiss', 'false')
                self.force_close_kodi_in_5_seconds(dialog_header="עדכון מהיר הסתיים בהצלחה")
                
            return True

            # self.dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}]עדכון מהיר הסתיים. לחץ אישור/OK כדי לסגור את קודי. לאחר מכן, הפעל אותו מחדש.[/COLOR]".format(CONFIG.COLOR2))
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]עדכון מהיר: בוטל![/COLOR]'.format(CONFIG.COLOR2))
            return False
    #####################################################

    #####################################################
    # KODI-RD-IL
    def force_close_kodi_in_5_seconds(self, dialog_header):
        self.dialogProgress.create(f"[COLOR yellow][B]{dialog_header}[/B][/COLOR]", "[B]קודי ייסגר בעוד 5 שניות[/B]")
        for s in range(5, -1, -1):
            self.dialogProgress.update(int((5 - s) / 5.0 * 100), f"[B]קודי ייסגר בעוד {s} שניות[/B]")
            xbmc.sleep(1000)
        self.restart_kodi()
    #####################################################

    #####################################################
    # KODI-RD-IL
    def restart_kodi(self):
        # if tools.platform() == 'windows':
            # try:
                # import subprocess, xbmcvfs
                # kodi_root_path = xbmcvfs.translatePath('special://xbmc/')
                # kodi_full_path = [os.path.join(kodi_root_path, 'kodi.exe')]
                # KODI-RD-IL Custom Windows software - AppData stored in C:\Kodi + Real Debrid Israel\portable_data
                # if "Kodi + Real Debrid Israel" in kodi_root_path:
                    # kodi_full_path.append('-p')
                # subprocess.Popen(kodi_full_path, shell=True)
            # except:
                # pass
        tools.kill_kodi(over=True)
    #####################################################



    def theme(self, name, theme='', over=False):
        installtheme = False

        if not theme:
            themefile = check.check_build(name, 'theme')

            response = tools.open_url(themefile, check=True)
            if response:
                from resources.libs.gui.build_menu import BuildMenu
                themes = BuildMenu().theme_count(name, False)
                if len(themes) > 0:
                    if self.dialog.yesno(CONFIG.ADDONTITLE, "[COLOR {0}]The Build [COLOR {1}]{2}[/COLOR] comes with [COLOR {3}]{4}[/COLOR] different themes".format(CONFIG.COLOR2, CONFIG.COLOR1, name, CONFIG.COLOR1, len(themes)) + '\n' + "Would you like to install one now?[/COLOR]",
                                    yeslabel="[B][COLOR springgreen]Install Theme[/COLOR][/B]",
                                    nolabel="[B][COLOR red]Cancel Themes[/COLOR][/B]"):
                        logging.log("Theme List: {0}".format(str(themes)))
                        ret = self.dialog.select(CONFIG.ADDONTITLE, themes)
                        logging.log("Theme install selected: {0}".format(ret))
                        if not ret == -1:
                            theme = themes[ret]
                            installtheme = True
                        else:
                            logging.log_notify(CONFIG.ADDONTITLE,
                                               '[COLOR {0}]Theme Install: Cancelled![/COLOR]'.format(CONFIG.COLOR2))
                            return
                    else:
                        logging.log_notify(CONFIG.ADDONTITLE,
                                           '[COLOR {0}]Theme Install: Cancelled![/COLOR]'.format(CONFIG.COLOR2))
                        return
            else:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]Theme Install: None Found![/COLOR]'.format(CONFIG.COLOR2))
        else:
            installtheme = self.dialog.yesno(CONFIG.ADDONTITLE, '[COLOR {0}]Would you like to install the theme:'.format(CONFIG.COLOR2) +' \n' + '[COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, theme) + '\n' + 'for [COLOR {0}]{1} v{2}[/COLOR]?[/COLOR]'.format(CONFIG.COLOR1, name, check.check_build(name,'version')),yeslabel="[B][COLOR springgreen]Install Theme[/COLOR][/B]", nolabel="[B][COLOR red]Cancel Themes[/COLOR][/B]")
                                        
        if installtheme:
            themezip = check.check_theme(name, theme, 'url')
            zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

            response = tools.open_url(themezip, check=True)
            if not response:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]Theme Install: Invalid Zip Url![/COLOR]'.format(CONFIG.COLOR2))
                return False

            self.dialogProgress.create(CONFIG.ADDONTITLE, '[COLOR {0}][B]Downloading:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, zipname) +' \n' + 'Please Wait')

            lib = os.path.join(CONFIG.PACKAGES, '{0}.zip'.format(zipname))
            
            try:
                os.remove(lib)
            except:
                pass

            Downloader().download(themezip, lib)
            xbmc.sleep(500)
            
            if os.path.getsize(lib) == 0:
                try:
                    os.remove(lib)
                except:
                    pass
                    
                return
            
            self.dialogProgress.update(0, '\n' + "Installing {0}".format(name))

            test1 = False
            test2 = False
            
            from resources.libs import skin
            from resources.libs import test
            test1 = test.test_theme(lib) if CONFIG.SKIN not in skin.DEFAULT_SKINS else False
            test2 = test.test_gui(lib) if CONFIG.SKIN not in skin.DEFAULT_SKINS else False

            if test1:
                skin.look_and_feel_data('save')
                swap = skin.skin_to_default('Theme Install')

                if not swap:
                    return False

                xbmc.sleep(500)

            title = '[COLOR {0}][B]Installing Theme:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, theme)
            self.dialogProgress.update(0, title + '\n' + 'Please Wait')
            percent, errors, error = extract.all(lib, CONFIG.HOME, title=title)
            CONFIG.set_setting('buildtheme', theme)
            logging.log('INSTALLED {0}: [ERRORS:{1}]'.format(percent, errors))
            self.dialogProgress.close()

            db.force_check_updates(over=True)
            installed = db.grab_addons(lib)
            db.addon_database(installed, 1, True)

            if test2:
                skin.look_and_feel_data('save')
                skin.skin_to_default("Theme Install")
                gotoskin = CONFIG.get_setting('defaultskin')
                skin.switch_to_skin(gotoskin, "Theme Installer")
                skin.look_and_feel_data('restore')
            elif test1:
                skin.look_and_feel_data('save')
                skin.skin_to_default("Theme Install")
                gotoskin = CONFIG.get_setting('defaultskin')
                skin.switch_to_skin(gotoskin, "Theme Installer")
                skin.look_and_feel_data('restore')
            else:
                xbmc.executebuiltin("ReloadSkin()")
                xbmc.sleep(1000)
                xbmc.executebuiltin("Container.Refresh()")
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]Theme Install: Cancelled![/COLOR]'.format(CONFIG.COLOR2))


def wizard(action, name, url):
    cls = Wizard()

    if action in ['fresh', 'normal']:
        cls.build(action, name)
    elif action == 'gui':
        cls.gui(name)
    elif action == 'theme':
        cls.theme(name, url)



#########################################################################################################
# KODI-RD-IL - BUILD SKIN SWITCH
def update_favourites_xml_file(gotoskin):
    try:
        import xbmcvfs
        source_favourites_xml = xbmcvfs.translatePath(f"special://home/media/builds_favourites_xml/{gotoskin}/favourites.xml")
        destination_favourites_xml = xbmcvfs.translatePath("special://userdata/favourites.xml")
        from shutil import copyfile
        copyfile(source_favourites_xml,destination_favourites_xml)
        return True
    except Exception as e:
        logging.log_notify(CONFIG.ADDONTITLE,
                           '[COLOR {0}]שגיאה בהגדרת מסך הבית![/COLOR]'.format(CONFIG.COLOR2))
        logging.log(f"DEBUG | update_favourites_xml_file | Exception: {str(e)}")
        return False
    

def switch_skin_in_gui_settings(gotoskin):
    try:
        import xbmcvfs
        guisettings_file_path = xbmcvfs.translatePath("special://userdata/guisettings.xml")
        import xml.etree.ElementTree as ET
        tree = ET.parse(guisettings_file_path)
        root = tree.getroot()
        # Find the setting with id="lookandfeel.skin"
        for setting in root.iter('setting'):
            if setting.get('id') == 'lookandfeel.skin':
                # Remove default attribute, if present
                if 'default' in setting.attrib:
                    del setting.attrib['default']
                # Change the value to gotoskin
                setting.text = gotoskin
        # Write the modified tree back to the file
        tree.write(guisettings_file_path)
        return True
    except Exception as e:
        logging.log_notify(CONFIG.ADDONTITLE,
                           '[COLOR {0}]שגיאה בהחלפת סקין![/COLOR]'.format(CONFIG.COLOR2))
        logging.log(f"DEBUG | switch_skin_in_gui_settings | Exception: {str(e)}")
        return False
        
def build_switch_skin():

    if not CONFIG.get_setting('buildname'):
        logging.log_notify(CONFIG.ADDONTITLE,
                           '[COLOR {0}]לא מותקן בילד![/COLOR]'.format(CONFIG.COLOR2))
        return


    from resources.libs.gui import window   
    msg = f"הסקינים הקיימים בבילד:\n1. סקין Estuary\n2. סקין FENtastic"
    window.show_notification_with_extra_image(msg, 888, CONFIG.BUILD_SKIN_SWITCH_IMAGE_URL)

    skin_mapping = {
        'סקין Estuary - מראה פשוט עם כפתורים': 'skin.estuary',
        'סקין FENtastic - יפהפה': 'skin.fentastic'
    }
        
    # Get the name of the current active skin   
    current_skin_name = next((skin_name for skin_name, skin_addon_name in skin_mapping.items() if skin_addon_name in CONFIG.SKIN))

    # Filter out the current active skin from the list
    skins_list = [skin_name for skin_name, skin_addon_name in skin_mapping.items() if skin_addon_name not in CONFIG.SKIN]

    # Create a dialog window
    dialog = xbmcgui.Dialog()
    gotoskin_index_number = dialog.select(f"[B]סקין נוכחי: [COLOR gold]{current_skin_name}[/COLOR][/B]", skins_list)    
    
    if gotoskin_index_number == -1:  # User cancelled the menu
        return
        
    selected_skin = skins_list[gotoskin_index_number]
    gotoskin = skin_mapping[selected_skin]
        
    yes_pressed = dialog.yesno(CONFIG.ADDONTITLE,
                       '[B][COLOR {0}]האם ברצונך להחליף סקין ל:'.format(CONFIG.COLOR2) + '\n' + '[COLOR {0}]{1}[/COLOR]?[/COLOR][/B]'.format(CONFIG.COLOR1, selected_skin),
                       nolabel='[B][COLOR red]ביטול[/COLOR][/B]',
                       yeslabel='[B][COLOR springgreen]החלף סקין[/COLOR][/B]')

    if yes_pressed:
        dialogProgress = xbmcgui.DialogProgress()
        dialog_text = '[COLOR {0}][B]מחליף סקין ומגדיר את מסך הבית של:[/B][/COLOR]\n[COLOR {1}][B]{2}[/B][/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, selected_skin)
        dialogProgress.create(CONFIG.ADDONTITLE, dialog_text)
        for s in range(3, -1, -1):
            dialogProgress.update(int((3 - s) / 3.0 * 100), dialog_text)
            xbmc.sleep(1000)
            
        # guisettings.xml | Configure lookandfeel.skin setting
        if not switch_skin_in_gui_settings(gotoskin): return
        
        xbmc.sleep(500)
        
        # favourites.xml | Switch to selected build's skin favourites.xml 
        if not update_favourites_xml_file(gotoskin): return
        
        dialogProgress.close()
        Wizard().force_close_kodi_in_5_seconds(dialog_header="סקין הוחלף בהצלחה!")
    else:
        return
            
##########################################
# KODI-RD-IL - WINDOWS + ANDROID
def check_if_running_custom_kodi(kodi_custom_path):
    import xbmcvfs
    kodi_root_path = xbmcvfs.translatePath('special://xbmc/')
    if kodi_custom_path in kodi_root_path:
        return True
    return False
    
# KODI-RD-IL - ANDROID
def check_if_app_installed(app_package_id):
    import xbmcvfs
    apps = xbmcvfs.listdir('androidapp://sources/apps/')[1]
    return app_package_id in apps
    
def open_google_play_store_on_specific_app(app_package_id):
    app      = 'com.android.vending'
    intent   = 'android.intent.action.VIEW'
    dataType = ''
    dataURI  = f'https://play.google.com/store/apps/details?id={app_package_id}'
    xbmc.executebuiltin(f'StartAndroidActivity("{app}", "{intent}", "{dataType}", "{dataURI}")')

# KODI-RD-IL - ANDROID
def kodi_apk_update_check(kodi_version_update_check_manual, os_type_label):
    dialog = xbmcgui.Dialog()
    try:

        LATEST_APK_VERSION_TEXT_FILE = float(tools.open_url(CONFIG.LATEST_APK_VERSION_TEXT_FILE).text)
        is_new_version_available = LATEST_APK_VERSION_TEXT_FILE > CONFIG.KODIV
        
        if is_new_version_available:
        
            yes_pressed = dialog.yesno(f"{CONFIG.ADDONTITLE} ({os_type_label})",
                               f'[COLOR yellow][B]קיים עדכון גרסה לאפליקציה שלנו![/B][/COLOR]\nגרסת קודי נוכחית: [B][COLOR red]{CONFIG.KODIV}[/COLOR][/B]\nגרסת קודי מעודכנת: [B][COLOR limegreen]{LATEST_APK_VERSION_TEXT_FILE}[/COLOR][/B]\nהאם ברצונך לעדכן את האפליקציה?',
                               nolabel='[B][COLOR red]מאוחר יותר[/COLOR][/B]',
                               yeslabel='[B][COLOR springgreen]עדכן[/COLOR][/B]')
                               
            if yes_pressed:
                yes_pressed = dialog.yesno(f"{CONFIG.ADDONTITLE} ({os_type_label})",
                                   f'[B]משתמש בסטרימר Android TV? בחר [COLOR orange]Downloader[/COLOR].\n\nמשתמש בסטרימר/מכשיר אנדרואיד רגיל? בחר [COLOR yellow]Google Chrome[/COLOR].[/B]',
                                   nolabel='[B][COLOR orange]Downloader[/COLOR][/B]',
                                   yeslabel='[B][COLOR yellow]Google Chrome[/COLOR][/B]') 
                                   
                if yes_pressed:
                    google_chrome_app_packge_id = 'com.android.chrome'
                            
                    if check_if_app_installed(google_chrome_app_packge_id):
                        # Open Google Chrome on APK_DOWNLOAD_URL.
                        app      = google_chrome_app_packge_id
                        intent   = 'android.intent.action.VIEW'
                        dataType = ''
                        dataURI  = CONFIG.APK_DOWNLOAD_URL
                        xbmc.executebuiltin(f'StartAndroidActivity("{app}", "{intent}", "{dataType}", "{dataURI}")')
                        return
                        
                    else:
                        yes_pressed = dialog.yesno(f"{CONFIG.ADDONTITLE} ({os_type_label})",
                                           '[B]אפליקציית [COLOR yellow]Google Chrome[/COLOR] אינה מותקנת.[/B]',
                                           nolabel='[B]ביטול[/B]',
                                           yeslabel='[B]הורד מהחנות[/B]')
                        if yes_pressed:
                            # Open Google Play Store on Google Chrome app.
                            open_google_play_store_on_specific_app(google_chrome_app_packge_id)
                            return
                        else:
                            return
                    
                else:
                    downloader_app_packge_id = 'com.esaba.downloader'
                    
                    msg = f"כעת תיפתח אפליקציית Downloader. יש להזין את המספר:\n[COLOR orange]{CONFIG.APK_DOWNLOADER_CODE}[/COLOR]\nולבחור את גרסת ה-APK (32/64 ביט) המתאימה למכשיר שלכם.\n[COLOR limegreen]עכשיו זה הזמן לרשום/לצלם את המספר![/COLOR]"
                    from resources.libs.gui import window
                    window.show_notification_with_extra_image(msg, 999, CONFIG.APK_DOWNLOADER_CODE_IMAGE_URL)
                    
                    # Check if Downloader app installed.
                    if check_if_app_installed(downloader_app_packge_id):
                        xbmc.executebuiltin(f'StartAndroidActivity({downloader_app_packge_id})')
                        return
                        
                    else:
                        yes_pressed = dialog.yesno(f"{CONFIG.ADDONTITLE} ({os_type_label})",
                                           '[B]אפליקציית [COLOR orange]Downloader[/COLOR] אינה מותקנת.[/B]',
                                           nolabel='[B]ביטול[/B]',
                                           yeslabel='[B]הורד מהחנות[/B]')
                        if yes_pressed:
                            # Open Google Play Store on Downloader app.
                            open_google_play_store_on_specific_app(downloader_app_packge_id)
                            return
                        else:
                            return
                
            else:
                return
                    
        elif kodi_version_update_check_manual:
            dialog.ok(f"{CONFIG.ADDONTITLE} ({os_type_label})", f'[COLOR yellow][B]לא קיים עדכון לאפליקציה![/B][/COLOR]\nגרסת קודי נוכחית: [B][COLOR limegreen]{CONFIG.KODIV}[/COLOR][/B]\nגרסת קודי מעודכנת: [B][COLOR limegreen]{LATEST_APK_VERSION_TEXT_FILE}[/COLOR][/B]')
                         
    except Exception as e:
        logging.log(f'[kodi_version_update_check] Exception: {str(e)}')
        if kodi_version_update_check_manual:
            dialog.ok(f"{CONFIG.ADDONTITLE} ({os_type_label})", f'התרחשה שגיאה:\n{str(e)}')


# KODI-RD-IL - WINDOWS
def kill_kodi_and_install_exe(exe_full_path):
    
    import xbmcvfs
    if not xbmcvfs.exists(exe_full_path):
        logging.log_notify(CONFIG.ADDONTITLE,
                            '[COLOR {0}]הקובץ לא נמצא![/COLOR]'.format(CONFIG.COLOR2))
    
    def kill_kodi():
        subprocess.call('taskkill /f /im kodi.exe', shell=True)
    
    import threading,subprocess
    kodi_killer = threading.Timer(1.0, kill_kodi)
    kodi_killer.start()
    subprocess.call(exe_full_path, shell=True)


# KODI-RD-IL - WINDOWS
def kodi_windows_update_check(kodi_version_update_check_manual, os_type_label):
    dialog = xbmcgui.Dialog()
    
    try:
        LATEST_WINDOWS_VERSION_NUMBER = float(tools.open_url(CONFIG.LATEST_WINDOWS_VERSION_TEXT_FILE).text)
        is_new_version_available = LATEST_WINDOWS_VERSION_NUMBER > CONFIG.KODIV
            
        if is_new_version_available:
            
            yes = dialog.yesno(f"{CONFIG.ADDONTITLE} ({os_type_label})",
                               f'[COLOR yellow][B]קיים עדכון גרסה לאפליקציה שלנו![/B][/COLOR]\nגרסת קודי נוכחית: [B][COLOR red]{CONFIG.KODIV}[/COLOR][/B]\nגרסת קודי מעודכנת: [B][COLOR limegreen]{LATEST_WINDOWS_VERSION_NUMBER}[/COLOR][/B]\nהאם ברצונך לעדכן את האפליקציה?',
                               nolabel='[B][COLOR red]מאוחר יותר[/COLOR][/B]',
                               yeslabel='[B][COLOR springgreen]עדכן[/COLOR][/B]')
                                       
            if not yes:
                return
            
            if yes:
                ######## BUILD DIRECT EXE WINDOWS INSTALER URL ########
                DIRECT_WINDOWS_DOWNLOAD_URL = f"{CONFIG.WINDOWS_DOWNLOAD_URL}/Kodi + Real Debrid Israel {LATEST_WINDOWS_VERSION_NUMBER} Setup.exe"
                #######################################################
                
                response = tools.open_url(DIRECT_WINDOWS_DOWNLOAD_URL, check=True)
                if not response:
                    logging.log_notify(f"{CONFIG.ADDONTITLE} ({os_type_label})",
                                        '[COLOR {0}]קישור ההורדה אינו תקין![/COLOR]'.format(CONFIG.COLOR2))
                    return
                    
                destination_path = CONFIG.PACKAGES
                exe_file_name = os.path.basename(DIRECT_WINDOWS_DOWNLOAD_URL)
                exe_full_path = os.path.join(destination_path, exe_file_name)
                   
                progress_dialog = xbmcgui.DialogProgress() 
                progress_dialog.create(f"{CONFIG.ADDONTITLE} ({os_type_label})",
                              '[COLOR {0}][B]מוריד:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, exe_file_name)
                              +'\n'+''
                              +'\n'+'נא המתן')
                
                try:
                    os.remove(exe_full_path)
                except:
                    pass
                Downloader().download(DIRECT_WINDOWS_DOWNLOAD_URL, exe_full_path)
                xbmc.sleep(100)
                progress_dialog.close()
                    
                dialog.ok(f"{CONFIG.ADDONTITLE} ({os_type_label})", f"[B]ההורדה הסתיימה בהצלחה.\nלחץ אישור כדי לסגור את קודי ולהתחיל את ההתקנה.[/B]")
                kill_kodi_and_install_exe(exe_full_path)
                        
        elif kodi_version_update_check_manual:
            dialog.ok(f"{CONFIG.ADDONTITLE} ({os_type_label})", f'[COLOR yellow][B]לא קיים עדכון לאפליקציה![/B][/COLOR]\nגרסת קודי נוכחית: [B][COLOR limegreen]{CONFIG.KODIV}[/COLOR][/B]\nגרסת קודי מעודכנת: [B][COLOR limegreen]{LATEST_WINDOWS_VERSION_NUMBER}[/COLOR][/B]')
                         
    except Exception as e:
        logging.log(f'[kodi_version_update_check] Exception: {str(e)}')
        if kodi_version_update_check_manual:
            dialog.ok(f"{CONFIG.ADDONTITLE} ({os_type_label})", f'התרחשה שגיאה:\n{str(e)}')


# xbmc.executebuiltin(f"RunPlugin(plugin://{CONFIG.ADDON_ID}/?mode=install&action=kodi_version_update_check&kodi_version_update_check_manual=False)")
def kodi_version_update_check(kodi_version_update_check_manual="false"):

    kodi_version_update_check_manual = True if kodi_version_update_check_manual=="true" else False
    os_type_label = tools.platform().capitalize()
    dialog = xbmcgui.Dialog()
        
    # Android APK
    if tools.platform() == 'android':
        ###### KODI ANDROID APK INSTALLED CHECK ###########
        if not check_if_running_custom_kodi(CONFIG.APK_PACKAGE_ID):
            if kodi_version_update_check_manual:
                dialog.ok(f"{CONFIG.ADDONTITLE} ({os_type_label})",'[B]אינך עם האפליקצייה הייעודית שלנו![/B]')
            return
        kodi_apk_update_check(kodi_version_update_check_manual, os_type_label)
    
    # Windows Software
    elif tools.platform() == 'windows':
        ###### KODI WINDOWS SOFTWARE INSTALLED CHECK ###########
        if not check_if_running_custom_kodi(CONFIG.WINDOWS_INSTALLATION_PATH):
            if kodi_version_update_check_manual:
                dialog.ok(f"{CONFIG.ADDONTITLE} ({os_type_label})",'[B]אינך עם תוכנת הקודי הייעודית שלנו![/B]')
            return
        kodi_windows_update_check(kodi_version_update_check_manual, os_type_label)
        
    else:
        dialog.ok(CONFIG.ADDONTITLE, f"[B]הפיצ'ר אינו נתמך עבור: {os_type_label}[/B]")
##########################################


##########################################
# KODI-RD-IL - REAL DEBRID SPEED TEST        
def build_speed_test():
    dialog = xbmcgui.Dialog()
    
    # Speed Test addon
    yes_pressed = dialog.yesno(CONFIG.ADDONTITLE,
                       f'[B][COLOR yellow]האם להפעיל בדיקת מהירות דרך הרחבת Speed Test או דרך האתר של ריל דבריד?[/COLOR][/B]',
                       nolabel='[B]Speed Test[/B]',
                       yeslabel='[B]Real Debrid[/B]')
                       
    if not yes_pressed:
        xbmc.executebuiltin('InstallAddon("script.speedtester")')
        xbmc.executebuiltin('RunAddon("script.speedtester")')
        
    else:       
        os_type_label = tools.platform().capitalize()
        
        # Windows
        if tools.platform() == 'windows':
            # Open the URL in default browser
            import webbrowser
            webbrowser.get().open_new_tab("https://real-debrid.com/speedtest")
            
        # Android / Android TV - through browsers apps
        elif tools.platform() == 'android':
        
            android_apps_browsers_list = ['com.android.chrome', 'com.phlox.tvwebbrowser', 'com.seraphic.openinet.pre', 'com.tcl.browser']
            installed_browser_package_id = None

            # Loop through each browser in the list
            for browser_package_id in android_apps_browsers_list:
                # Check if the browser is installed
                if check_if_app_installed(browser_package_id):
                    installed_browser_package_id = browser_package_id
                    break

            if not installed_browser_package_id:
                yes_pressed = dialog.yesno(f"{CONFIG.ADDONTITLE} ({os_type_label})",
                                   f'[B][COLOR yellow]לא מותקן דפדפן תומך!\nדפדנים נתמכים:[/COLOR]\nGoogle Chrome, TV Bro, OPEN BROWSER, BrowseHere[/B]',
                                   nolabel='[B]ביטול[/B]',
                                   yeslabel='[B]קח אותי לחנות[/B]')
                if yes_pressed:
                    # Open Google Play Store
                    xbmc.executebuiltin('StartAndroidActivity(com.android.vending)')
                    return
                return
                            
            app      = installed_browser_package_id
            intent   = 'android.intent.action.VIEW'
            dataType = ''
            dataURI  = "https://real-debrid.com/speedtest"
            xbmc.executebuiltin(f'StartAndroidActivity("{app}", "{intent}", "{dataType}", "{dataURI}")')
            return
            
        else:
            dialog.ok(CONFIG.ADDONTITLE, f"[B]פתיחת דפדפן עבור בדיקת מהירות Real Debrid אינו זמין עבור מערכת ההפעלה: {os_type_label}[/B]")
##########################################
    