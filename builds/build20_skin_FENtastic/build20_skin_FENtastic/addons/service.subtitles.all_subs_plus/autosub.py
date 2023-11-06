#!/usr/bin/python

import xbmc,xbmcaddon,xbmcvfs,xbmcplugin
from xbmcvfs import  mkdirs
import time,json,hashlib
import os,re,linecache
import sys,base64
import cache,threading

from service import search_all,change_background
from service import running,action,searchstring,notify3,colorize_text,getKodiPreferredPlayerLanugageCode
from service import MyAddon,__settings__,MyScriptID,all_setting,download_next,location,last_sub_download,getParams,subtitle_cache_next
#from service import links_wizdom,links_ktuvit,links_open,links_subscene,links_subcenter,links_local,imdbid,base_aa

from shutil import rmtree

#from aa_subs_api.aa_subs import get_aa_server

KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
if KODI_VERSION<=18:
    xbmc_translate_path=xbmc.translatePath
else:
    xbmc_translate_path=xbmcvfs.translatePath

#base_aa='aHR0cHM6Ly9zZXJ2ZXIxMDkzLnNlZWRob3N0LmV1L2tzdWJzL0h1Yi8='
#base_aa='aHR0cHM6Ly9yb2NrLnNlZWRob3N0LmV1L2tjYXQxMjMvSHViLw=='

__author__ = MyAddon.getAddonInfo('author')
__scriptid__ = MyAddon.getAddonInfo('id')
__scriptname__ = MyAddon.getAddonInfo('name')
__version__ = MyAddon.getAddonInfo('version')
__language__ = MyAddon.getLocalizedString
debug = MyAddon.getSetting("Debug")
__cwd__ = xbmc_translate_path(MyAddon.getAddonInfo('path'))
__profile__ = xbmc_translate_path(MyAddon.getAddonInfo('profile'))
__resource__ = xbmc_translate_path(os.path.join(__cwd__, 'resources'))

cache_list_folder=(xbmc_translate_path(os.path.join(__profile__, 'cache_list_folder')))
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
current_list_item=''
excludeTime = int((__settings__.getSetting('ExcludeTime')))*60

from myLogger import myLogger

def Debug(msg):
    myLogger("[AutoSubs] " + msg)

def DebugExclude(msg):
    Debug("isExclude() :: " + msg)

sys.path.append(__resource__)

#try:
#f = urllib2.urlopen('https://raw.githubusercontent.com/ebs111/ebs_repo/master/repository/zips/service.subtitles.All_Subs/ignore.txt')
Debug(os.path.join(__cwd__,'ignore.txt'))


# Create the ignore addons list to be excluded from using the AutoSub feature
if KODI_VERSION<=18:
    f=open(os.path.join(__cwd__,'ignore.txt'), 'r')
else:
    f=open(os.path.join(__cwd__,'ignore.txt'), 'r', encoding="utf-8-sig")
excluded_addons_temp=f.readlines()
excluded_addons=[]
f.close()
Debug('Excluded list')
for ext in excluded_addons_temp:
    x=(ext).replace('\n','').replace('\r','').lower()
    excluded_addons.append(x)

if KODI_VERSION>18:
    class Thread (threading.Thread):
       def __init__(self, target, *args):
        super().__init__(target=target, args=args)
       def run(self, *args):

          self._target(*self._args)
else:
    class Thread(threading.Thread):
        def __init__(self, target, *args):
            self._target = target
            self._args = args

            threading.Thread.__init__(self)

        def run(self):
            self._target(*self._args)

Debug('start')
Debug("Loading '%s' version '%s'" % (__scriptname__, __version__))

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    try:
        # myLogger('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj), logLevel=xbmc.LOGERROR)
        Debug( 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
        return "Error"
    except:
        return "Error"

def getSetting(setting):
    global all_setting
    return all_setting[setting].strip()

# helper function to get bool type from settings
def getSettingAsBool(setting):
    return getSetting(setting).lower() == "true"

# check exclusion settings for filename passed as argument
def isExcluded(videoFullPath):
    global current_list_item

    DebugExclude('Excluded Check')
    DebugExclude('excluded_addons: ' + repr(excluded_addons))
    DebugExclude('current_list_item: ' + repr(current_list_item.lower()))
    DebugExclude("videoFullPath '%s'" % videoFullPath)

    DebugExclude("Checking exclusion settings for '%s'." % videoFullPath)
    exlude_local_files_smb=all_setting["exlude_local_files_smb"]=='true'

    if not videoFullPath:
        return True

    if 'smb:' in videoFullPath or 'smb:' in current_list_item:
        if exlude_local_files_smb:
            DebugExclude("Video is Local from SMB. Exclude.")
            return True
        else:
            DebugExclude("Video is Local from SMB. Do not exclude.")
            return False

    if ("pvr://" in videoFullPath or "pvr://" in current_list_item.lower()) :
        DebugExclude("Video is playing via Live TV, which is currently set as excluded location.")
        return True

    if (xbmc.getInfoLabel("VideoPlayer.mpaa")=='heb'):
        DebugExclude("mpaa is 'heb'. Excluded from list defined!!." )
        return True

    if any(x in current_list_item.lower() for x in excluded_addons):
        DebugExclude("Video is playing from '%s', which is currently set as !!excluded_addons!!." %current_list_item)
        return True

    ExcludeAddos = getSetting('ExcludeAddos')
    if ExcludeAddos and getSettingAsBool('ExcludeAddosOption'):
        if ((ExcludeAddos.lower()) in current_list_item.lower() ):
            DebugExclude("Video is playing from '%s', which is currently set as excluded path 1." % ExcludeAddos)
            return True

    ExcludeAddos2 = getSetting('ExcludeAddos2')
    if ExcludeAddos2 and getSettingAsBool('ExcludeAddosOption2'):
        if ( (ExcludeAddos2.lower()) in current_list_item.lower() ):
            DebugExclude("Video is playing from '%s', which is currently set as excluded path 2." % ExcludeAddos2)
            return True

    ExcludeAddos3 = getSetting('ExcludeAddos3')
    if ExcludeAddos3 and getSettingAsBool('ExcludeAddosOption3'):
        if ((ExcludeAddos3.lower()) in current_list_item.lower()   ):
            DebugExclude("Video is playing from '%s', which is currently set as excluded path 3." % ExcludeAddos3)
            return True

    ExcludeAddos4 = getSetting('ExcludeAddos4')
    if ExcludeAddos4 and getSettingAsBool('ExcludeAddosOption4'):
        if ((ExcludeAddos4.lower()) in current_list_item.lower()  ):
            DebugExclude("Video is playing from '%s', which is currently set as excluded path 4." % ExcludeAddos4)
            return True

    ExcludeAddos5 = getSetting('ExcludeAddos5')
    if ExcludeAddos5 and getSettingAsBool('ExcludeAddosOption5'):
        if ((ExcludeAddos5.lower()) in current_list_item.lower()  ):
            DebugExclude("Video is playing from '%s', which is currently set as excluded path 5." % ExcludeAddos5)
            return True

    if getSettingAsBool('ExcludeAddosOption6'):
        ExcludeAddos6_pre = getSetting('ExcludeAddos6')
        ExcludeAddos6=ExcludeAddos6_pre.split(',')
        for items in ExcludeAddos6:
            if ((items.lower()) in current_list_item.lower()  ) and len(items)>0:
                DebugExclude("Video is playing from '%s', which is currently set as excluded path 6." % items)
                return True

    return False

class MainMonitor(xbmc.Monitor):

    def __init__(self):
        super(MainMonitor, self).__init__()

    def onSettingsChanged(self):
        from service import refresh_setting,all_setting
        global location,subtitle_cache_next
        refresh_setting()
        Debug("Setting Changed")

        next_sub=(MyAddon.getSetting("nextsub"))
        Debug(next_sub)

        if next_sub=='background':
            all_setting=change_background(all_setting)
            MyAddon.setSetting("background",all_setting["background"])
            MyAddon.setSetting("nextsub",'no')

        elif next_sub!='no':
            try:
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('Allsubs', 'Changing Subs')))
            except:
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('Allsubs', 'Changing Subs')).encode('utf-8'))

            if os.path.exists(cache_list_folder):#if cache folder exist
                list_files=os.listdir(cache_list_folder)
                if len (list_files)>0:
                  last_sub=os.path.join(cache_list_folder,list_files[0])
                else:
                  last_sub=''

                save_all_data=[]
                enable_count=-1
                break_func=0
                last_sub_download=subtitle_cache_next().get('last_sub')

                max_sub=0
                if os.path.exists(last_sub):#if list file exist
                    file = open(last_sub+'_sort', 'r')
                    save_all_data=json.loads(file.read())
                    file.close()
                    max_sub=len(save_all_data)


                    for save_data_value in save_all_data:
                        lab1,lab2,icn,thu,url,pre=save_data_value

                        if break_func>0:
                            break

                        params=getParams('?'+url.split('?')[1])

                        enable_count=enable_count+1
                        hash_data=hashlib.sha256(str(json.dumps(params)).encode('utf-8','ignore')).hexdigest()

                        if last_sub_download=='ZERO':
                            break_func=1
                            break
                        if last_sub_download==hash_data:
                            break_func=1
                            break

                    if next_sub=='next' :
                        location=enable_count+1
                        try:
                            xbmc.executebuiltin((u'Notification(%s,%s)' % ('Allsubs', 'Next Subs')))
                        except:
                            xbmc.executebuiltin((u'Notification(%s,%s)' % ('Allsubs', 'Next Subs')).encode('utf-8'))
                        if location==max_sub:
                            location=0
                    elif next_sub=='previous':
                        if enable_count==0:
                            try:
                               xbmc.executebuiltin((u'Notification(%s,%s)' % ('Allsubs', 'Previous Subs')))
                            except:
                               xbmc.executebuiltin((u'Notification(%s,%s)' % ('Allsubs', 'Previous Subs')).encode('utf-8'))
                            location=max_sub-1
                        else:
                            location=enable_count-1

                    location=download_next(location,all_setting,last_sub_download,save_all_data,max_sub)
                    addon = xbmcaddon.Addon('service.subtitles.All_Subs')
                    addon.setSetting("nextsub", 'no')

                else:
                    try:
                        begin_search_process()
                    except:
                        PrintException()
                        try:
                            xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, 'Failed')))
                        except:
                            xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, 'Failed')).encode('utf-8'))

        #xbmc.executebuiltin('XBMC.Container.Update(%s)' % __cwd__)


class AutoSubsPlayer(xbmc.Player):
    global __settings__,MyAddon,MyScriptID

    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        Debug("Initalized")
        self.run = True

    def onPlayBackStopped(self):
        running=0
        Debug("Stopped")
        try:
          rmtree(cache_list_folder)
        except: pass
        mkdirs(cache_list_folder)
        self.run = True

    def onPlayBackEnded(self):
        Debug("Ended")
        self.run = True

    def onPlayBackStarted(self):
        global running,subtitle_cache_next,current_list_item
        Debug('start player')

        if all_setting["autosub"]=='true':
            try:
                if self.run:
                    xbmc.sleep(1000)
                    Debug('Is autosub Playing: '+str(xbmc.Player().isPlaying()))
                    totalTime = xbmc.Player().getTotalTime()
                    #totalTime ==0.0
                    if xbmc.Player().isPlaying():
                        Debug('Start Playing')
                        #vidtime = xbmc.Player().getTime()
                        #Debug('vidtime:'+str(vidtime))
                        while 1:
                            vidtime = xbmc.Player().getTime()
                            Debug('vidtime:'+str(vidtime))
                            if vidtime>0:
                                totalTime = xbmc.Player().getTotalTime()
                                #Debug('totalTimeIn:'+str(totalTime))
                                break
                            if not xbmc.Player().isPlaying():
                                totalTime = 0.0
                                #totalTime ==0.0
                                break
                            xbmc.sleep(100)
                    Debug("totalTime: '%s'" % totalTime)
                    Debug("excludeTime: '%s'" % excludeTime)

                    #--------------------------------------------------------------------------
                    # Check if the video source is excluded from using the AutoSub feature
                    videoFullPath = xbmc.Player().getPlayingFile()
                    try:
                        is_excluded = isExcluded(videoFullPath)
                    except:
                        is_excluded = False
                        Debug('AutoSubs isExcluded ERROR')

                    Debug('isExcluded: '+repr(is_excluded))

                    #--------------------------------------------------------------------------

                    avoid_autosubs_on_built_in_subs = all_setting["avoid_on_built_in"] == 'true'
                    Debug("Avoid when there is built-in subs: '%s'" % (avoid_autosubs_on_built_in_subs))
                    useBuiltInSub = False
                    if avoid_autosubs_on_built_in_subs:
                        availableLangs = xbmc.Player().getAvailableSubtitleStreams() # return availabe built-in subs languages
                        if len(availableLangs) > 0:
                            preferredLang = getKodiPreferredPlayerLanugageCode(all_setting)
                            Debug("Preferred language '%s'" % (preferredLang))
                            Debug("Available built-in subs languages: %s" % availableLangs)
                            useBuiltInSub = preferredLang in availableLangs

                    Debug('useBuiltInSub: ' + str(useBuiltInSub))

                    #--------------------------------------------------------------------------

                    # Force override subtitles even if the video file already contains subtitles
                    force_download=True
                    if all_setting["force"]=='true':
                        force_download=True
                    if all_setting["force"]=='false' and xbmc.getCondVisibility("VideoPlayer.HasSubtitles"):
                        force_download=False
                    Debug('force_download: ' + str(force_download))

                    if (xbmc.Player().isPlaying() and totalTime > excludeTime and not is_excluded
                        and (force_download or not useBuiltInSub)):
                        self.run = False
                        #xbmc.sleep(1000)
                        Debug('Started: AutoSearching for Subs')
                        running=0
                        if running==0:
                            running=1
                          #try:
                            Debug('running: ' + repr(running))
                            begin_search_process()

                            #subtitle_cache_next.set('last_sub','ZERO')

                          #except Exception as e:
                          # xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, str(e))).encode('utf-8'))
                          # try:
                          #   PrintException()
                          # except:
                          #  pass
                            running=0
                            Debug('running: ' + repr(running))
                        #xbmc.executebuiltin('XBMC.ActivateWindow(SubtitleSearch)')
                    else:
                        if useBuiltInSub:
                            Debug("The video already contains subtitles in preferred language")

                            activeBuiltinSubs = xbmc.Player().getSubtitles() # return current built-in/loaded subs language
                            Debug("Current active built-in sub language: '%s'" % activeBuiltinSubs)

                            if activeBuiltinSubs != preferredLang:
                                Debug("Setting preferred active built-in sub")
                                indexPreferredLangSub = availableLangs.index(preferredLang)
                                xbmc.Player().setSubtitleStream(indexPreferredLangSub)
                            else:
                                Debug("Preferred active built-in sub is already set")

                            if all_setting["popup"]!="0":
                                notify3(colorize_text(__language__(32102),'aqua'),2)

                        else:
                            Debug('Subs found or excluded')
                        self.run = False
            except Exception as e:
                Debug("AutoSub failed: %s" %e)
                notify3(colorize_text(__language__(32103),'aqua'),2)
                # if all_setting["pause"]=='1': #resume
                #     xbmc.Player().pause()
                pass

def begin_search_process():
    #0 = Without pause
    #1 = Pause and Resume
    #2 = Pause
    if all_setting["pause"]!='0': #pause
        xbmc.Player().pause()

    search_all(2,all_setting)

    # if all_setting["pause"]=='1':
    #     xbmc.Player().pause()

'''
def get_aa_server_ch():
    Debug('-----------------Start Update AA-----------------')
    #get_aa_server(base64.b64decode(base_aa).decode('utf-8')+'Movies/',False)
    x_pre_movie=cache.get(get_aa_server,100,base64.b64decode(base_aa).decode('utf-8')+'Movies/','movie', table='subs_aa')
    x_pre_tv=cache.get(get_aa_server,100,base64.b64decode(base_aa).decode('utf-8')+'Series/','tv', table='subs_aa')

    if x_pre_tv is not None:
        Debug('-----------------Done Update AA TV: %s-----------------'%(len(x_pre_tv)))
    else:
        Debug('-----------------Failed Update AA TV')

    if x_pre_movie is not None:
        Debug('-----------------Done Update AA MOVIE: %s-----------------'%(len(x_pre_movie)))
    else:
        Debug('-----------------Failed Update AA MOVIE')

    return 'OK'
'''

xbmc.sleep(100)
Debug('Action Autosubs:'+str(action))
if action =='search':
    search_all(3,(all_setting))

# helper function to get string type from settings
elif action == 'manualsearch':
    #search_all(3,(all_setting))
    search_all(3,(all_setting),manual_search=True,manual_title=searchstring)

if action is None:
    from service import refresh_setting,all_setting

    update_time=1
    reset_running=0
    sleep_time = 1000
    last_run=0
    time_Show=100

    refresh_setting()

    player_monitor = AutoSubsPlayer()
    monitor = MainMonitor()

    Debug('AutoSubs service_started')
    #        if all_setting["autosub"]=='true':
    try:
        rmtree(cache_list_folder)
    except: pass
    mkdirs(cache_list_folder)

    #counter_2_hr=7300

    try:
        ab_req=xbmc.abortRequested()
    except:
        monit = xbmc.Monitor()
        ab_req=monit.abortRequested()
    while not ab_req:
        if(time.time() > last_run + update_time) and running==0 and not xbmc.Player().isPlaying():
            now = time.time()
            last_run = now - (now % update_time)
            '''
            if KODI_VERSION >= 17:
              current_list_item_temp=(xbmc.getInfoLabel("ListItem.AddonName"))
              if len(current_list_item_temp)>0 :
                  current_list_item=current_list_item_temp
            else:
            '''
            current_list_item_temp=(xbmc.getInfoLabel("ListItem.FileNameAndPath"))
            if len(current_list_item_temp) > 0:
                if ('plugin://') in current_list_item_temp: #or ('smb://') in current_list_item_temp):
                    regex='//(.+?)/'
                    match=re.compile(regex).findall(current_list_item_temp)
                    if len (match)>0:
                        current_list_item = match[0]
                    else:
                        current_list_item = current_list_item_temp
                else:
                    current_list_item = current_list_item_temp


        if running==1:
            reset_running=reset_running+1
            if reset_running>30:
                running=0
                reset_running=0
            else:
                reset_running=0

        xbmc.sleep(sleep_time)
        '''
        if counter_2_hr>7200:
            thread=[]
            thread.append(Thread(get_aa_server_ch))
            thread[0].start()
            counter_2_hr=0

        counter_2_hr+=1
        '''
    del player_monitor

