import sys
import os
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmc

if len(sys.argv) > 1:
    HANDLE = int(sys.argv[1])
else:
    HANDLE = -1
    
# Addon Variables
ADDON = xbmcaddon.Addon()
ADDON_FANART = ADDON.getAddonInfo('fanart')
ADDON_PATH = ADDON.getAddonInfo('path')
CUSTOM_ART = os.path.join(ADDON_PATH, 'resources', 'kodi_rd_israel_art')
MSG_TEXT = 'בחר בשירות אותו תרצה לחבר להרחבת Twilight'
# Images used for the contact window.  http:// for default icon and fanart
CONTACTICON = os.path.join(CUSTOM_ART, 'real_debrid_trakt_logo.png')
# Themes
THEME_TITLE = u'[B][COLOR {color2}]{{}}[/COLOR][/B]'.format(color2='lightblue')
THEME_TEXT = u'[B][COLOR {color2}]{{}}[/COLOR][/B]'.format(color2='yellow')

# Exit Actions
ACTION_PREVIOUS_MENU = 10  # ESC action
ACTION_NAV_BACK = 92  # Backspace action
ACTION_BACKSPACE = 110  # ?
BACK_ACTIONS = [ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_BACKSPACE]

def show_contact(msg=""):
    class ContactWindow(xbmcgui.WindowXMLDialog):
        def __init__(self, *args, **kwargs):
            self.image = kwargs["image"]
            self.fanart = kwargs["fanart"]
            self.msg = THEME_TEXT.format(kwargs["msg"])

        def onInit(self):
            self.fanartimage = 101
            self.imagecontrol = 102
            self.msg_textbox = 103
            self.twilight_connect_rd_button = 104
            self.twilight_connect_trakt_button = 105
            self.twilight_connect_ad_button = 106
            self.close_button = 120
            self.show_dialog()

        def show_dialog(self):
            self.getControl(self.fanartimage).setImage(self.fanart)
            self.getControl(self.fanartimage).setColorDiffuse('9FFFFFFF')
            self.getControl(self.imagecontrol).setImage(self.image)
            self.getControl(self.msg_textbox).setText(self.msg)
            self.setFocusId(self.twilight_connect_rd_button)

        def onClick(self, controlid):
            if controlid == self.close_button:
                self.close()
            elif controlid == self.twilight_connect_rd_button:
                self.close()
                # Open Twilight Real Debrid Authentication Window
                xbmc.executebuiltin('RunPlugin(plugin://plugin.video.twilight/?mode=real_debrid.authenticate)')
            elif controlid == self.twilight_connect_trakt_button:
                self.close()
                # Open Twilight Trakt Authentication Window
                xbmc.executebuiltin('RunPlugin(plugin://plugin.video.twilight/?mode=trakt.trakt_authenticate)')
            elif controlid == self.twilight_connect_ad_button:
                self.close()
                # Open Twilight All Debrid Authentication Window
                xbmc.executebuiltin('RunPlugin(plugin://plugin.video.twilight/?mode=alldebrid.authenticate)')


        def onAction(self, action):
            if action.getId() in BACK_ACTIONS:
                self.close()

    cw = ContactWindow("Contact.xml", ADDON_PATH, 'Default', fanart=ADDON_FANART,
                  image=CONTACTICON, msg=MSG_TEXT)
    cw.doModal()
    del cw

def main():
    show_contact(msg="")

if __name__ == "__main__":
    main()
    if HANDLE > -1:
        xbmcplugin.endOfDirectory(HANDLE)
