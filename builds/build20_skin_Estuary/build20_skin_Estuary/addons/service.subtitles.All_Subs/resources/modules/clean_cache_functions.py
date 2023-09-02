# Imports
import xbmcgui,xbmcvfs
import os,shutil,sys
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database
    
# Addon parameters
MyScriptName = "DarkSubs"
iconx = "special://home/addons/service.subtitles.All_Subs/icon.png"

# Userdata Directory
xbmc_tranlate_path = xbmcvfs.translatePath
user_dataDir = xbmc_tranlate_path("special://home/userdata/addon_data/service.subtitles.All_Subs")
# Subs Cache Folders
SubCacheDBFolder = xbmc_tranlate_path(os.path.join(user_dataDir, 'cache_f'))
# Machine Translate Cache Folders
CachedSubFolder = xbmc_tranlate_path(os.path.join(user_dataDir, 'Cached_subs'))
TransFolder = xbmc_tranlate_path(os.path.join(user_dataDir, 'trans_subs'))


# Notify function from modules/general.py
def notify(msg_id, times=2500, icon=iconx,sound=False):
        xbmcgui.Dialog().notification(MyScriptName, f"[COLOR yellow]{msg_id}[/COLOR]", icon, int(times), sound)

# clear(table=None) function from modules/cache.py
def clear_sources_db(table=None):

    try:
        if table == None: table = ['rel_list']
        elif not type(table) == list: table = [table]
       
        mypath = SubCacheDBFolder
        if not os.path.exists(mypath):
            os.mkdir(mypath)
        dbcon = database.connect(os.path.join(mypath,'sources.db'))
        dbcur = dbcon.cursor()

        for t in table:
            try:
                dbcur.execute("DROP TABLE IF EXISTS %s" % t)
                dbcur.execute("VACUUM")
                dbcon.commit()
            except:
                pass
    except Exception as e:
        notify( f"ERROR: {str(e)}" )
        pass

# Clear database.db
def clear_database_db(table=None):
        
    try:
        if table == None: table = ['rel_list']
        elif not type(table) == list: table = [table]
       
        mypath = user_dataDir
        if not os.path.exists(mypath):
            os.mkdir(mypath)
        dbcon = database.connect(os.path.join(mypath,'database.db'))
        dbcur = dbcon.cursor()

        for t in table:
            try:
                dbcur.execute("DROP TABLE IF EXISTS %s" % t)
                dbcur.execute("VACUUM")
                dbcon.commit()
            except:
                pass
    except Exception as e:
        notify( f"ERROR: {str(e)}" )
        pass
    

def clean_machine_translate_folders():
    try:
        shutil.rmtree(CachedSubFolder)
    except: pass
    xbmcvfs.mkdirs(CachedSubFolder)
    try:
        shutil.rmtree(TransFolder)
    except: pass
    xbmcvfs.mkdirs(TransFolder)
    xbmc.sleep(300)

    if not os.path.exists(CachedSubFolder):
         os.makedirs(CachedSubFolder)


    if not os.path.exists(TransFolder):
         os.makedirs(TransFolder)


# Get command line arguments
args = sys.argv
action = None

# Check if the script is called with arguments
if len(args) > 1:
    action = args[1]

# Clear subs DB cache action
if action == "clean_all_cache":
    clear_sources_db(['subs'])
    clear_database_db(['list_subs_cache'])
    clean_machine_translate_folders()
    notify( "קאש כתוביות נוקה" )