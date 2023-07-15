import sys
import os
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmc
import urllib.request
from urllib.parse import urljoin
import ssl
import json

if len(sys.argv) > 1:
    HANDLE = int(sys.argv[1])
else:
    HANDLE = -1

# Create an SSL context that allows SSL verification to be skipped
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# Addon Variables
ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')

# Themes
THEME_TITLE = u'[COLOR {color2}]{{}}[/COLOR]'.format(color2='lightblue')
THEME_TEXT = u'[COLOR {color2}]{{}}[/COLOR]'.format(color2='yellow')

# Exit Actions
ACTION_PREVIOUS_MENU = 10  # ESC action
ACTION_NAV_BACK = 92  # Backspace action
ACTION_BACKSPACE = 110  # ?
BACK_ACTIONS = [ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_BACKSPACE]


def show_guide(title, url):
    class ShowGuide(xbmcgui.WindowXMLDialog):

        def __init__(self, *args, **kwargs):
            try:
                with urllib.request.urlopen(url, context=context) as response:
                    self.guide_text = response.read().decode('utf-8')
            except Exception as e:
                self.guide_text = "הייתה בעיה בטעינת הטקסט. אם אתה רואה את ההודעה הזאת, נא דווח על כך בקבוצת הטלגרם בצירוף השם מהתפריט שניסית לפתוח.\n\nhttp://bit.ly/kodi7rd"
            
            self.title = THEME_TITLE.format(title)
            self.guide_text = THEME_TEXT.format(self.guide_text)

        def onInit(self):
            self.titlebox = 102
            self.textbox = 103
            self.close_button = 202
            self.show_dialog()

        def show_dialog(self):
            self.getControl(self.titlebox).setLabel(self.title)
            self.getControl(self.textbox).setText(self.guide_text)
            
        def on_menu_item_selected_index_number(self, menu_item_selected_index_number):
            if menu_item_selected_index_number.getId() in BACK_ACTIONS:
                self.close()

        def onClick(self, controlid):
            if controlid == self.close_button:
                self.close()

    guide = ShowGuide("guide.xml", ADDON_PATH, 'Default')
    guide.doModal()
    del guide

def main():
    # Get menu items list (file_title_map.json from GitHub)
    file_title_map_github_link = "https://kodi7rd.github.io/custom_addons/build_guides_addon/assets/file_title_map.json"
    
    try:
        with urllib.request.urlopen(file_title_map_github_link, context=context) as response:
            file_title_map = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        file_title_map = {
        "קיימת שגיאה בטעינת הנתונים. אנא דווח על כך בקבוצת הטלגרם.": ""
        }

    menu_items = list(file_title_map.keys())
    
    # GitHub link for guides directory contains all guides .txt files
    guides_directory_github_url = "https://kodi7rd.github.io/custom_addons/build_guides_addon/assets/guides/"
    
    while True:
        menu_item_selected_index_number = xbmcgui.Dialog().select("בחר נושא", menu_items)
        if menu_item_selected_index_number == -1:  # User cancelled the menu
            break
        else:
            title = menu_items[menu_item_selected_index_number]
            # Generate full url for guide .txt file. Example: https://kodi7rd.github.io/custom_addons/build_guides_addon/assets/guides/<filename>.txt
            url = urljoin(guides_directory_github_url, file_title_map[title])
            show_guide(title, url)

if __name__ == "__main__":
    main()
    if HANDLE > -1:
        xbmcplugin.endOfDirectory(HANDLE)
