import xbmcaddon

import os

#########################################################
#         Global Variables - DON'T EDIT!!!              #
#########################################################
ADDON_ID = xbmcaddon.Addon().getAddonInfo('id')
PATH = xbmcaddon.Addon().getAddonInfo('path')
ART = os.path.join(PATH, 'resources', 'media')
CUSTOM_ART = os.path.join(PATH, 'resources', 'kodi_rd_israel_art')
#########################################################

#########################################################
#        User Edit Variables                            #
#########################################################
ADDONTITLE = '[COLOR yellow]Kodi + Real Debrid Israel Wizard[/COLOR]'
BUILDERNAME = '[COLOR yellow]Kodi + Real Debrid Israel[/COLOR]'
EXCLUDES = [ADDON_ID]
# Text File with build info in it. Please read https://github.com/a4k-openproject/plugin.program.openwizard/wiki/Installing-Builds
BUILDFILE = 'https://kodi7rd.github.io/wizard/assets/build.txt'
# How often you would like it to check for build updates in days
# 0 being every startup of kodi
UPDATECHECK = 0
# Text File with apk info in it.  Leave as 'http://' to ignore
APKFILE = 'http://'

#########################################################
# KODI-RD-IL - BUILD SKIN SWITCH
BUILD_SKIN_SWITCH_IMAGE_URL = 'https://kodi7rd.github.io/wizard/assets/build_menu_screenshots/kodirdil21.png'
# KODI-RD-IL - AUTO QUICK UPDATES
QUICK_UPDATE_NOTIFICATION_URL = 'https://kodi7rd.github.io/wizard/assets/notification_files/quick_update.txt'
# KODI-RD-IL - AUTO ANDROID/WINDOWS UPDATE
# WINDOWS SOFTWARE
LATEST_WINDOWS_VERSION_TEXT_FILE = 'https://kodi7rd.github.io/wizard/assets/kodi_version_auto_update/windows/latest_windows_version.txt'
WINDOWS_DOWNLOAD_URL = "https://kodi7rd.github.io/windows"
WINDOWS_INSTALLATION_PATH = "C:\Kodi + Real Debrid Israel"
# ANDROID APK
LATEST_APK_VERSION_TEXT_FILE = 'https://kodi7rd.github.io/wizard/assets/kodi_version_auto_update/apk/latest_apk_version.txt'
APK_DOWNLOAD_URL = 'https://kodi7rd.github.io/apk'
APK_PACKAGE_ID = 'org.xbmc.kodirdil'
APK_DOWNLOADER_CODE = '864332'
APK_DOWNLOADER_CODE_IMAGE_URL = 'https://kodi7rd.github.io/wizard/assets/kodi_version_auto_update/apk/apk_downloader_code.png'
#########################################################

# Text File with Youtube Videos urls.  Leave as 'http://' to ignore
YOUTUBETITLE = ''
YOUTUBEFILE = 'http://'
# Text File for addon installer.  Leave as 'http://' to ignore
ADDONFILE = 'http://'
# Text File for advanced settings.  Leave as 'http://' to ignore
ADVANCEDFILE = 'http://'
#########################################################

#########################################################
#        Theming Menu Items                             #
#########################################################
# If you want to use locally stored icons the place them in the Resources/Art/
# folder of the wizard then use os.path.join(ART, 'imagename.png')
# do not place quotes around os.path.join
# Example:  ICONMAINT     = os.path.join(ART, 'mainticon.png')
#           ICONSETTINGS  = 'https://www.yourhost.com/repo/wizard/settings.png'
# Leave as http:// for default icon
ICONBUILDS = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONMAINT = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONSPEED = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONAPK = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONADDONS = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONYOUTUBE = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONSAVE = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONTRAKT = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONREAL = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONLOGIN = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONCONTACT = os.path.join(CUSTOM_ART, 'wizard.jpg')
ICONSETTINGS = os.path.join(CUSTOM_ART, 'wizard.jpg')
# Hide the section separators 'Yes' or 'No'
HIDESPACERS = 'No'
# Character used in separator
SPACER = '='

# You can edit these however you want, just make sure that you have a %s in each of the
# THEME's so it grabs the text from the menu item
COLOR1 = 'blue'
COLOR2 = 'yellow'
COLOR_LIMEGREEN = 'limegreen'
COLOR_YELLOW = 'yellow'
COLOR_WHITE = 'white'
# Primary menu items   / {0} is the menu item and is required
THEME1 = u'[COLOR {color1}][I][COLOR {color1}][B]Kodi + Real Debrid Israel[/B][/COLOR][COLOR {color2}][COLOR {color1}] - [/I][/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
# Build Names          / {0} is the menu item and is required
THEME2 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
# Alternate items      / {0} is the menu item and is required
THEME3 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
# LIMEGREEN Alternate items      / {0} is the menu item and is required
THEME_LIMEGREEN = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR_LIMEGREEN)
# YELLOW Alternate items      / {0} is the menu item and is required
THEME_YELLOW = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR_YELLOW)
# Current Build Header / {0} is the menu item and is required
THEME4 = u'[COLOR {color1}]גרסת בילד נוכחי:[/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
# Current Theme Header / {0} is the menu item and is required
THEME5 = u'[COLOR {color1}]Current Theme:[/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
# KODI_RD_ISRAEL Custom Theme for COLOR_WHITE text usage (window.py - def show_dialog)
THEME6 = u'[COLOR {COLOR_WHITE}]{{}}[/COLOR]'.format(COLOR_WHITE=COLOR_WHITE)

# Message for Contact Page
# Enable 'Contact' menu item 'Yes' hide or 'No' dont hide
HIDECONTACT = 'Yes'
# You can add \n to do line breaks
CONTACT = 'Thank you for choosing OpenWizard'
# Images used for the contact window.  http:// for default icon and fanart
CONTACTICON = os.path.join(ART, 'qricon.jpg')
CONTACTFANART = 'http://'
#########################################################

#########################################################
#        Auto Update For Those With No Repo             #
#########################################################
# Enable Auto Update 'Yes' or 'No'
AUTOUPDATE = 'Yes'
#########################################################

#########################################################
#        Auto Install Repo If Not Installed             #
#########################################################
# Enable Auto Install 'Yes' or 'No'
AUTOINSTALL = 'No'
# Addon ID for the repository
REPOID = 'spaceholder'
# Url to Addons.xml file in your repo folder(this is so we can get the latest version)
REPOADDONXML = 'https://'
# Url to folder zip is located in
REPOZIPURL = 'https://'
#########################################################

#########################################################
#        Notification Window                            #
#########################################################
# Enable Notification screen Yes or No
ENABLE = 'Yes'
# Url to notification file
NOTIFICATION = 'https://kodi7rd.github.io/wizard/assets/notification_files/build_first_launch.txt'
# Use either 'Text' or 'Image'
HEADERTYPE = 'Image'
# Font size of header
FONTHEADER = 'Font14'
HEADERMESSAGE = ''
# url to image if using Image 424x180
HEADERIMAGE = os.path.join(CUSTOM_ART, 'kodi_rd_il_icon.png')
# Font for Notification Window
FONTSETTINGS = 'Font13'
# Background for Notification Window
BACKGROUND = 'http://'
#########################################################
