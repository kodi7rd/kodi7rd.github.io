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

# build addons blacklist imports
import glob
from resources.libs.common import tools
from resources.libs import whitelist

# Create an SSL context that allows SSL verification to be skipped
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
######################################################################

# GitHub links for custom_save_data_config.json and build_addons_whitelist.txt + build_addons_blacklist files
custom_save_data_config_github_url = "https://kodi7rd.github.io/wizard/assets/custom_save_data_config/custom_save_data_config.json"
build_addons_whitelist_github_url = "https://kodi7rd.github.io/wizard/assets/custom_save_data_config/build_addons_whitelist.txt"
build_addons_blacklist_github_url = "https://kodi7rd.github.io/wizard/assets/custom_save_data_config/build_addons_blacklist.txt"

# Load the configuration from the JSON file
with urllib.request.urlopen(custom_save_data_config_github_url, context=context) as response:
    custom_save_data_config = json.loads(response.read().decode('utf-8'))
    
# Log JSON
logging.log("custom_save_data_config.py | custom_save_data_config.json: " + str(custom_save_data_config), level=xbmc.LOGINFO)

# set USE_JSON_FILE from JSON file.
USE_JSON_FILE = str(custom_save_data_config.get('USE_JSON_FILE', 'false')).lower()

def set_custom_save_data_variables_from_github():

    # Override the variables based on the configuration
    CONFIG.KEEPTRAKT = str(custom_save_data_config.get('CONFIG.KEEPTRAKT', CONFIG.KEEPTRAKT)).lower() if 'CONFIG.KEEPTRAKT' in custom_save_data_config else CONFIG.KEEPTRAKT
    CONFIG.KEEPDEBRID = str(custom_save_data_config.get('CONFIG.KEEPDEBRID', CONFIG.KEEPDEBRID)).lower() if 'CONFIG.KEEPDEBRID' in custom_save_data_config else CONFIG.KEEPDEBRID
    CONFIG.KEEPLOGIN = str(custom_save_data_config.get('CONFIG.KEEPLOGIN', CONFIG.KEEPLOGIN)).lower() if 'CONFIG.KEEPLOGIN' in custom_save_data_config else CONFIG.KEEPLOGIN
    CONFIG.KEEPFENDATA = str(custom_save_data_config.get('CONFIG.KEEPFENDATA', CONFIG.KEEPFENDATA)).lower() if 'CONFIG.KEEPFENDATA' in custom_save_data_config else CONFIG.KEEPFENDATA
    CONFIG.KEEPTWILIGHTDATA = str(custom_save_data_config.get('CONFIG.KEEPTWILIGHTDATA', CONFIG.KEEPTWILIGHTDATA)).lower() if 'CONFIG.KEEPTWILIGHTDATA' in custom_save_data_config else CONFIG.KEEPTWILIGHTDATA
    CONFIG.KEEPFENTASTICDATA = str(custom_save_data_config.get('CONFIG.KEEPFENTASTICDATA', CONFIG.KEEPFENTASTICDATA)).lower() if 'CONFIG.KEEPFENTASTICDATA' in custom_save_data_config else CONFIG.KEEPFENTASTICDATA
    CONFIG.KEEPFAVS = str(custom_save_data_config.get('CONFIG.KEEPFAVS', CONFIG.KEEPFAVS)).lower() if 'CONFIG.KEEPFAVS' in custom_save_data_config else CONFIG.KEEPFAVS
    CONFIG.KEEPSOURCES = str(custom_save_data_config.get('CONFIG.KEEPSOURCES', CONFIG.KEEPSOURCES)).lower() if 'CONFIG.KEEPSOURCES' in custom_save_data_config else CONFIG.KEEPSOURCES
    CONFIG.KEEPADVANCED = str(custom_save_data_config.get('CONFIG.KEEPADVANCED', CONFIG.KEEPADVANCED)).lower() if 'CONFIG.KEEPADVANCED' in custom_save_data_config else CONFIG.KEEPADVANCED
    CONFIG.KEEPPROFILES = str(custom_save_data_config.get('CONFIG.KEEPPROFILES', CONFIG.KEEPPROFILES)).lower() if 'CONFIG.KEEPPROFILES' in custom_save_data_config else CONFIG.KEEPPROFILES
    CONFIG.KEEPPLAYERCORE = str(custom_save_data_config.get('CONFIG.KEEPPLAYERCORE', CONFIG.KEEPPLAYERCORE)).lower() if 'CONFIG.KEEPPLAYERCORE' in custom_save_data_config else CONFIG.KEEPPLAYERCORE
    CONFIG.KEEPGUISETTINGS = str(custom_save_data_config.get('CONFIG.KEEPGUISETTINGS', CONFIG.KEEPGUISETTINGS)).lower() if 'CONFIG.KEEPGUISETTINGS' in custom_save_data_config else CONFIG.KEEPGUISETTINGS
    CONFIG.KEEPREPOS = str(custom_save_data_config.get('CONFIG.KEEPREPOS', CONFIG.KEEPREPOS)).lower() if 'CONFIG.KEEPREPOS' in custom_save_data_config else CONFIG.KEEPREPOS
    CONFIG.KEEPSUPER = str(custom_save_data_config.get('CONFIG.KEEPSUPER', CONFIG.KEEPSUPER)).lower() if 'CONFIG.KEEPSUPER' in custom_save_data_config else CONFIG.KEEPSUPER
    CONFIG.KEEPADDONS33DB = str(custom_save_data_config.get('CONFIG.KEEPADDONS33DB', CONFIG.KEEPADDONS33DB)).lower() if 'CONFIG.KEEPADDONS33DB' in custom_save_data_config else CONFIG.KEEPADDONS33DB
    logging.log("custom_save_data_config.py | Finished overriding CONFIG.KEEP variables.", level=xbmc.LOGINFO)    


def set_addons_whitelist_from_github():

    # Override CONFIG.KEEPWHITELIST from JSON file.
    CONFIG.KEEPWHITELIST = str(custom_save_data_config.get('CONFIG.KEEPWHITELIST', CONFIG.KEEPWHITELIST)).lower() if 'CONFIG.KEEPWHITELIST' in custom_save_data_config else CONFIG.KEEPWHITELIST
    
    if CONFIG.KEEPWHITELIST == 'false':
        delete_addons_whitelist_file()
        return    
        
    logging.log("custom_save_data_config.py | CONFIG.KEEPWHITELIST is: " + CONFIG.KEEPWHITELIST + ". Writing into whitelist.txt file..", level=xbmc.LOGINFO)
    
    write_extra_addons_to_local_whitelist()
    merge_local_whitelist_with_github_addons()


def write_extra_addons_to_local_whitelist():
    
    # Read Build Blacklist addons from GitHub        
    with urllib.request.urlopen(build_addons_blacklist_github_url) as f:
        build_addons_blacklist = [line.decode("utf-8").strip() for line in f.readlines()]
      
    logging.log("custom_save_data_config.py | build_addons_blacklist: " + str(build_addons_blacklist), level=xbmc.LOGINFO)
    
    # Taken from whitelist.py - list all extra installed addons, excluding defaults, and build addons blacklist from GitHub.
    addonnames = []
    addonids = []
    addonfolds = []
    
    fold = glob.glob(os.path.join(CONFIG.ADDONS, '*/'))
    for folder in sorted(fold, key=lambda x: x):
        foldername = os.path.split(folder[:-1])[1]
        if foldername in CONFIG.EXCLUDES:
            continue
        elif foldername in CONFIG.DEFAULTPLUGINS:
            continue
        elif foldername in CONFIG.DEPENDENCIES:
            continue
        elif foldername in build_addons_blacklist:
            continue
        elif foldername == 'packages':
            continue
        xml = os.path.join(folder, 'addon.xml')
        if os.path.exists(xml):
            a = tools.read_from_file(xml)
            temp, addid = whitelist.parse(a, foldername)
            addonnames.append(temp)
            addonids.append(addid)
            addonfolds.append(foldername)
    fold2 = glob.glob(os.path.join(CONFIG.ADDON_DATA, '*/'))
    for folder in sorted(fold2, key=lambda x: x):
        foldername = os.path.split(folder[:-1])[1]
        if foldername in addonfolds:
            continue
        if foldername in CONFIG.EXCLUDES:
            continue
        if foldername in build_addons_blacklist:
            continue
        xml = os.path.join(CONFIG.ADDONS, foldername, 'addon.xml')
        xml2 = os.path.join(CONFIG.XBMC, 'addons', foldername, 'addon.xml')
        if os.path.exists(xml):
            a = tools.read_from_file(xml)
        elif os.path.exists(xml2):
            a = tools.read_from_file(xml2)
        else:
            continue
        temp, addid = whitelist.parse(a, foldername)
        addonnames.append(temp)
        addonids.append(addid)
        addonfolds.append(foldername)
       
    white_list = []
    for index in range(len(addonnames)):
        white_list.append("['%s', '%s', '%s']" % (addonnames[index], addonids[index], addonfolds[index]))
        
    writing = '\n'.join(white_list)    
    tools.write_to_file(CONFIG.WHITELIST, writing)


def merge_local_whitelist_with_github_addons():
    try:
        # Read current whitelist
        with open(CONFIG.WHITELIST, 'r', encoding='utf-8') as f:
            local_whitelist = [line.strip() for line in f]
    except Exception:
        # If an error occurs while reading the file, use an empty list
        local_whitelist = []
    
    logging.log("custom_save_data_config.py | Local whitelist.txt to merge: " + str(local_whitelist), level=xbmc.LOGINFO)

    with urllib.request.urlopen(build_addons_whitelist_github_url) as f:
        github_addons_whitelist_file = [line.decode("utf-8").strip() for line in f.readlines()] 
        
    logging.log("custom_save_data_config.py | GitHub whitelist.txt to merge: " + str(github_addons_whitelist_file), level=xbmc.LOGINFO)
    
    github_addons_whitelist_list = []
    for index in range(len(github_addons_whitelist_file)):
        github_addons_whitelist_list.append("['%s', '%s', '%s']" % (github_addons_whitelist_file[index], github_addons_whitelist_file[index], github_addons_whitelist_file[index]))

    # Combine and remove duplicates while preserving order
    merged_whitelist = list(dict.fromkeys(github_addons_whitelist_list + local_whitelist))
    
    # Write merged whitelist back to file
    writing = '\n'.join(merged_whitelist)    
    tools.write_to_file(CONFIG.WHITELIST, writing) 


def delete_addons_whitelist_file():
    # Delete userdata/addon_data/<wizard_name>/whitelist.txt to ensure no addons deletion.    
    logging.log("custom_save_data_config.py | CONFIG.KEEPWHITELIST is: " + CONFIG.KEEPWHITELIST + ". Deleting whitelist.txt file..", level=xbmc.LOGINFO)
    if os.path.exists(CONFIG.WHITELIST):
        os.remove(CONFIG.WHITELIST)


# Main
def main():
    # Exit if USE_JSON_FILE is false.
    if USE_JSON_FILE == 'false':
        logging.log("custom_save_data_config.py | USE_JSON_FILE is: " + USE_JSON_FILE + ". Exiting custom_save_data_config.py..", level=xbmc.LOGINFO)
        return
        
    logging.log("custom_save_data_config.py | USE_JSON_FILE is: " + USE_JSON_FILE + ". Starting custom_save_data_config.py functions..", level=xbmc.LOGINFO)
    set_custom_save_data_variables_from_github()
    set_addons_whitelist_from_github()

if __name__ == '__main__':
    main()