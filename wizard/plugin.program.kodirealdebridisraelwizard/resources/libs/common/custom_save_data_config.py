######################################################################
#        KODI_RD_ISRAEL Custom Save Data Config Imports              #
import sys
import json
import os
import urllib.request
from urllib.parse import urljoin
import ssl
import xbmc
from resources.libs.common import logging
from resources.libs.common.config import CONFIG
from resources.libs.common import tools

# Create an SSL context that allows SSL verification to be skipped
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
######################################################################

# GitHub links for custom_save_data_config.json and addons whitelist.txt files
custom_save_data_config_github_url = "https://kodi7rd.github.io/wizard/assets/custom_save_data_config/custom_save_data_config.json"
addons_whitelist_github_url = "https://kodi7rd.github.io/wizard/assets/custom_save_data_config/whitelist.txt"

# Load the configuration from the JSON file
with urllib.request.urlopen(custom_save_data_config_github_url, context=context) as response:
    custom_save_data_config = json.loads(response.read().decode('utf-8'))
    
# Log JSON
logging.log("custom_save_data_config.json: " + str(custom_save_data_config), level=xbmc.LOGINFO)

# set USE_JSON_FILE from JSON file.
USE_JSON_FILE = str(custom_save_data_config.get('USE_JSON_FILE', 'false')).lower()

def set_custom_save_data_variables_from_github():

    # Override the variables based on the configuration
    CONFIG.KEEPTRAKT = str(custom_save_data_config.get('CONFIG.KEEPTRAKT', CONFIG.KEEPTRAKT)).lower() if 'CONFIG.KEEPTRAKT' in custom_save_data_config else CONFIG.KEEPTRAKT
    CONFIG.KEEPDEBRID = str(custom_save_data_config.get('CONFIG.KEEPDEBRID', CONFIG.KEEPDEBRID)).lower() if 'CONFIG.KEEPDEBRID' in custom_save_data_config else CONFIG.KEEPDEBRID
    CONFIG.KEEPLOGIN = str(custom_save_data_config.get('CONFIG.KEEPLOGIN', CONFIG.KEEPLOGIN)).lower() if 'CONFIG.KEEPLOGIN' in custom_save_data_config else CONFIG.KEEPLOGIN
    CONFIG.KEEPFENDATA = str(custom_save_data_config.get('CONFIG.KEEPFENDATA', CONFIG.KEEPFENDATA)).lower() if 'CONFIG.KEEPFENDATA' in custom_save_data_config else CONFIG.KEEPFENDATA
    CONFIG.KEEPFAVS = str(custom_save_data_config.get('CONFIG.KEEPFAVS', CONFIG.KEEPFAVS)).lower() if 'CONFIG.KEEPFAVS' in custom_save_data_config else CONFIG.KEEPFAVS
    CONFIG.KEEPSOURCES = str(custom_save_data_config.get('CONFIG.KEEPSOURCES', CONFIG.KEEPSOURCES)).lower() if 'CONFIG.KEEPSOURCES' in custom_save_data_config else CONFIG.KEEPSOURCES
    CONFIG.KEEPADVANCED = str(custom_save_data_config.get('CONFIG.KEEPADVANCED', CONFIG.KEEPADVANCED)).lower() if 'CONFIG.KEEPADVANCED' in custom_save_data_config else CONFIG.KEEPADVANCED
    CONFIG.KEEPPROFILES = str(custom_save_data_config.get('CONFIG.KEEPPROFILES', CONFIG.KEEPPROFILES)).lower() if 'CONFIG.KEEPPROFILES' in custom_save_data_config else CONFIG.KEEPPROFILES
    CONFIG.KEEPPLAYERCORE = str(custom_save_data_config.get('CONFIG.KEEPPLAYERCORE', CONFIG.KEEPPLAYERCORE)).lower() if 'CONFIG.KEEPPLAYERCORE' in custom_save_data_config else CONFIG.KEEPPLAYERCORE
    CONFIG.KEEPGUISETTINGS = str(custom_save_data_config.get('CONFIG.KEEPGUISETTINGS', CONFIG.KEEPGUISETTINGS)).lower() if 'CONFIG.KEEPGUISETTINGS' in custom_save_data_config else CONFIG.KEEPGUISETTINGS
    CONFIG.KEEPREPOS = str(custom_save_data_config.get('CONFIG.KEEPREPOS', CONFIG.KEEPREPOS)).lower() if 'CONFIG.KEEPREPOS' in custom_save_data_config else CONFIG.KEEPREPOS
    CONFIG.KEEPSUPER = str(custom_save_data_config.get('CONFIG.KEEPSUPER', CONFIG.KEEPSUPER)).lower() if 'CONFIG.KEEPSUPER' in custom_save_data_config else CONFIG.KEEPSUPER
    logging.log("Finished overriding CONFIG.KEEP variables.", level=xbmc.LOGINFO)    


def set_addons_whitelist_from_github():

    # Override CONFIG.KEEPWHITELIST from JSON file.
    CONFIG.KEEPWHITELIST = str(custom_save_data_config.get('CONFIG.KEEPWHITELIST', CONFIG.KEEPWHITELIST)).lower() if 'CONFIG.KEEPWHITELIST' in custom_save_data_config else CONFIG.KEEPWHITELIST
    
    if CONFIG.KEEPWHITELIST == 'false':
        delete_addons_whitelist_file()
        return    
        
    logging.log("CONFIG.KEEPWHITELIST is: " + CONFIG.KEEPWHITELIST + ". Writing into whitelist.txt file..", level=xbmc.LOGINFO)
    # Fetch whitelist.txt from GitHub.
    with urllib.request.urlopen(addons_whitelist_github_url, context=context) as response:
        github_addons_whitelist_file = response.read().decode('utf-8')
    logging.log("GitHub whitelist.txt contents: " + github_addons_whitelist_file, level=xbmc.LOGINFO)
    
    with open(CONFIG.WHITELIST, 'w', encoding='utf-8') as f:
        for line in github_addons_whitelist_file.splitlines():
            f.write(line + '\n')


def delete_addons_whitelist_file():
    # Delete userdata/addon_data/<wizard_name>/whitelist.txt to ensure no addons deletion.    
    logging.log("CONFIG.KEEPWHITELIST is: " + CONFIG.KEEPWHITELIST + ". Deleting whitelist.txt file..", level=xbmc.LOGINFO)
    if os.path.exists(CONFIG.WHITELIST):
        os.remove(CONFIG.WHITELIST)


# Main
def main():
    # Exit if USE_JSON_FILE is false.
    if USE_JSON_FILE == 'false':
        logging.log("USE_JSON_FILE is: " + USE_JSON_FILE + ". Exiting custom_save_data_config.py..", level=xbmc.LOGINFO)
        return
        
    logging.log("USE_JSON_FILE is: " + USE_JSON_FILE + ". Starting custom_save_data_config.py functions..", level=xbmc.LOGINFO)
    set_custom_save_data_variables_from_github()
    set_addons_whitelist_from_github()


if __name__ == '__main__':
    main()