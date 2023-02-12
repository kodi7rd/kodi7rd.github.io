#!/usr/bin/python

import os,re,linecache
import sys,base64
import cache,threading
import xbmc,time,json
import xbmcaddon,logging,hashlib
from service import search_all,change_background
from service import running,action,searchstring
from service import MyAddon,__settings__,__addon__,MyScriptID,all_setting,download_next,location,last_sub_download,getParams,subtitle_cache_next
from service import links_wizdom,links_subcenter,links_local,links_first,links_open,imdbid
from xbmcvfs import  mkdirs
from shutil import rmtree
from resources.modules import log
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
if KODI_VERSION<=18:
    xbmc_tranlate_path=xbmc.translatePath
else:
    import xbmcvfs
    xbmc_tranlate_path=xbmcvfs.translatePath
base_aa='aHR0cHM6Ly9zZXJ2ZXIxMDkzLnNlZWRob3N0LmV1L2tzdWJzL0h1Yi8='
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__cwd__ = __addon__.getAddonInfo('path')
__version__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
debug = __addon__.getSetting("debug")
__cwd__ = xbmc_tranlate_path(__addon__.getAddonInfo('path'))
__profile__ = xbmc_tranlate_path(__addon__.getAddonInfo('profile'))
__resource__ = xbmc_tranlate_path(os.path.join(__cwd__, 'resources'))

cache_list_folder=(xbmc_tranlate_path(os.path.join(__profile__, 'cache_list_folder')))
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
current_list_item=''
ExcludeTime = int((__settings__.getSetting('ExcludeTime')))*60

sys.path.append(__resource__)

log.warning(os.path.join(__cwd__,'ignore.txt'))


if KODI_VERSION<=18:
    f=open(os.path.join(__cwd__,'ignore.txt'), 'r') 
else:
    f=open(os.path.join(__cwd__,'ignore.txt'), 'r', encoding="utf-8") 
excluded_addons_temp=f.readlines()
excluded_addons=[]
f.close()
log.warning('Excluded list')
for ext in excluded_addons_temp:
  x=(ext).replace('\n','').replace('\r','').lower()
  excluded_addons.append(x)
     
#except:
#  excluded_addons=['tenil','reshet','kidsil','movix','mako','rss','sertil','jksp','multidown','sdarot','ebs4_kids_tv']
if KODI_VERSION>18:
    
    class Thread (threading.Thread):
       def __init__(self, target, *args):
        super().__init__(target=target, args=args)
       def run(self, *args):
          
          self._target(*self._args)
          return 0
else:
   
    class Thread(threading.Thread):
        def __init__(self, target, *args):
           
            self._target = target
            self._args = args
            
            
            threading.Thread.__init__(self)
            
        def run(self):
            
            self._target(*self._args)

log.warning('start')
def get_aa_server(url,it):
    import requests,xbmcvfs
    MyTmp_aa = (xbmc_tranlate_path(os.path.join(__profile__, 'aa_buff')))
    try:
        shutil.rmtree(MyTmp_aa)
    except: pass
    xbmcvfs.mkdirs(MyTmp_aa)
    
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
           
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
    x=requests.get(url,headers=headers).content.decode('utf-8')
    if it:
        fi_name='aa_tv.txt'
    else:
        fi_name='aa_movie.txt'
    output_file=os.path.join(MyTmp_aa,fi_name)
    
    file = open(output_file, 'w')
  
    file.write(x) 
    file.close()
    return output_file
    
def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    log.warning( 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def Debug(msg, force = False):
    log.warning(msg)
    

Debug("Loading '%s' version '%s'" % (__scriptname__, __version__))
if action=='search':
  search_all(3,(all_setting))
# helper function to get string type from settings
elif action == 'manualsearch':
    
    #search_all(3,(all_setting))
    search_all(3,(all_setting),manual_search=True,manual_title=searchstring)
def getSetting(setting):
    global all_setting
    return all_setting[setting].strip()

# helper function to get bool type from settings
def getSettingAsBool(setting):
    return getSetting(setting).lower() == "true"

# check exclusion settings for filename passed as argument
def isExcluded(movieFullPath):
    global current_list_item
    if not movieFullPath:
        return False
    Debug (current_list_item)
    Debug("isExcluded(): Checking exclusion settings for '%s'." % movieFullPath)
    check_local=all_setting["local_files"]=='true'
    if not check_local and 'smb:' in movieFullPath:
        Debug("isExcluded(): Video is Local.")
        return False
    if (movieFullPath.find("pvr://") > -1) :
        Debug("isExcluded(): Video is playing via Live TV, which is currently set as excluded location.")
        return False
    log.warning('Excluded Check:')
    log.warning(current_list_item.lower())
    log.warning(excluded_addons)
    if (xbmc.getInfoLabel("VideoPlayer.mpaa")=='heb'):
          Debug("isExcluded(): Excluded from list defined!!." )
          return False
    if any(x in current_list_item.lower() for x in excluded_addons):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as !!excluded_addons!!." )
            return False

    ExcludeAddos = getSetting('ExcludeAddos')
    
    if ExcludeAddos and getSettingAsBool('ExcludeAddosOption'):
        if ((ExcludeAddos.lower()) in current_list_item.lower() ):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 1." % ExcludeAddos)
            return False
    
    ExcludeAddos2 = getSetting('ExcludeAddos2')

    if ExcludeAddos2 and getSettingAsBool('ExcludeAddosOption2'):
        if ( (ExcludeAddos2.lower()) in current_list_item.lower() ):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 2." % ExcludeAddos2)
            return False

    ExcludeAddos3 = getSetting('ExcludeAddos3')
    if ExcludeAddos3 and getSettingAsBool('ExcludeAddosOption3'):
        if ((ExcludeAddos3.lower()) in current_list_item.lower()   ):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 3." % ExcludeAddos3)
            return False

    ExcludeAddos4 = getSetting('ExcludeAddos4')
    if ExcludeAddos4 and getSettingAsBool('ExcludeAddosOption4'):
        if ((ExcludeAddos4.lower()) in current_list_item.lower()  ):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 4." % ExcludeAddos4)
            return False

    ExcludeAddos5 = getSetting('ExcludeAddos5')
    if ExcludeAddos5 and getSettingAsBool('ExcludeAddosOption5'):
        if ((ExcludeAddos5.lower()) in current_list_item.lower()  ):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 5." % ExcludeAddos5)
            return False
    
    if getSettingAsBool('ExcludeAddosOption6'):
        
        ExcludeAddos6_pre = getSetting('ExcludeAddos6')
 
        ExcludeAddos6=ExcludeAddos6_pre.split(',')

        for items in ExcludeAddos6:
            
           if ((items.lower()) in current_list_item.lower()  ) and len(items)>0:
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 6." % items)
            return False
    return True
class MainMonitor(xbmc.Monitor):
    
    def __init__(self):
        super(MainMonitor, self).__init__()

    def onSettingsChanged(self):
        global location,subtitle_cache_next
        all_setting=(refresh_setting())
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
           if  os.path.exists(cache_list_folder):#if cache folder exist
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
               addon = xbmcaddon.Addon('service.subtitles.All_Subs_Flash')
               addon.setSetting("nextsub", 'no')
              else:
               try:
                 if  all_setting["pause"]=='true':
                   xbmc.Player().pause()
                 
                 search_all(2,all_setting)
                 #subtitle_cache_next.set('last_sub','ZERO')
                 if  all_setting["pause"]=='true':
                      xbmc.Player().pause()
               except:
                 PrintException()
                 try:
                    xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, 'Failed')))
                 except:
                    xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, 'Failed')).encode('utf-8'))


class AutoSubsPlayer(xbmc.Player):
    global __settings__,__addon__,MyAddon,MyScriptID
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
      try:
        global running,subtitle_cache_next
        log.warning('start player')

        
        if self.run:

            movieFullPath = xbmc.Player().getPlayingFile()
            Debug("movieFullPath '%s'" % movieFullPath)
            xbmc.sleep(1000)
            availableLangs = xbmc.Player().getAvailableSubtitleStreams()

            Debug("availableLangs '%s'" % availableLangs)
            totalTime = xbmc.Player().getTotalTime()
            totalTime ==0.0
            if xbmc.Player().isPlaying():
                log.warning('Start Playing')
                vidtime = xbmc.Player().getTime()
                log.warning('vidtime:'+str(vidtime))
                while 1:
                    vidtime = xbmc.Player().getTime()
                    log.warning('vidtime:'+str(vidtime))
                    if vidtime>0:
                        totalTime = xbmc.Player().getTotalTime()
                        log.warning('totalTimeIn:'+str(totalTime))
                        break
                    if not xbmc.Player().isPlaying():
                        totalTime ==0.0
                        break
                    xbmc.sleep(100)
            Debug("totalTime '%s'" % totalTime)
            Debug("ExcludeTime '%s'" % ExcludeTime)
            force_download=True
            if  all_setting["force"]=='true':
              force_download=True
            if  all_setting["force"]=='false' and xbmc.getCondVisibility("VideoPlayer.HasSubtitles"):
              force_download=False
            res=(isExcluded(movieFullPath))
            log.warning('res')
            log.warning(res)
            log.warning('Is autosub Playing:'+str(xbmc.Player().isPlaying()))
            log.warning('totalTime:'+str(totalTime))
            log.warning('movieFullPath:'+str(movieFullPath))
            log.warning('(isExcluded(movieFullPath)) ):'+str((isExcluded(movieFullPath)) ))
            log.warning('force_download:'+str(force_download) )
            if (xbmc.Player().isPlaying() and totalTime > ExcludeTime and force_download==True and (isExcluded(movieFullPath)) ):
                self.run = False
                #xbmc.sleep(1000)
                Debug('Started: AutoSearching for Subs')
                Debug('running')
                Debug(running)
                running=0
                if running==0 :
                    running=1
                  #try:
                    if  all_setting["pause"]=='true':
                      xbmc.Player().pause()
                    if all_setting["autosub"]=='true':
                      search_all(2,all_setting)
                    
                    #subtitle_cache_next.set('last_sub','ZERO')
                    if  all_setting["pause"]=='true':
                      xbmc.Player().pause()
                  #except Exception as e:
                  # xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, str(e))).encode('utf-8'))
                  # try:
                  #   PrintException()
                  # except:
                  #  pass
                    running=0
                #xbmc.executebuiltin('XBMC.ActivateWindow(SubtitleSearch)')
            else:
                Debug('Started: Subs found or Excluded')
                self.run = False
      except:
        pass
def get_aa_server_ch():
    log.warning('-----------------Start Update AA-----------------')
    #get_aa_server(base64.b64decode(base_aa).decode('utf-8')+'Movies/',False)
    x_pre_tv=cache.get(get_aa_server,0,base64.b64decode(base_aa).decode('utf-8')+'Movies/',False, table='subs_aa')
    x_pre=cache.get(get_aa_server,0,base64.b64decode(base_aa).decode('utf-8')+'Series/',True, table='subs_aa')
    x_pre_tv=str(x_pre_tv)
    x_pre=str(x_pre_tv)
    log.warning('-----------------Done Update AA TV:%s MV:%s-----------------'%(len(x_pre_tv),len(x_pre)))
    return 'OK'
def refresh_setting():
   global __settings__,__addon__,MyAddon,MyScriptID,all_setting
   MyAddon = xbmcaddon.Addon()
   MyScriptID = MyAddon.getAddonInfo('id')
   __settings__ = xbmcaddon.Addon(id=MyScriptID)
   __addon__ = xbmcaddon.Addon()
   
   all_setting={}
   all_setting=({"Email":MyAddon.getSetting("Email"),
                "Password":MyAddon.getSetting("Password"),
                "action":MyAddon.getSetting("action"),
                "OSuser":MyAddon.getSetting("OSuser"),
                "OSpass":MyAddon.getSetting("OSpass"),
                "aa_subs":MyAddon.getSetting("aa_subs"),
                "wizrad":MyAddon.getSetting("wizrad"),
                "subscene":MyAddon.getSetting("subscene"),
                "opensubtitle":MyAddon.getSetting("opensubtitle"),
                "English":MyAddon.getSetting("English"),
                "autosub":MyAddon.getSetting("autosub"),
                "pause":MyAddon.getSetting("pause"),
                "ExcludeTime":MyAddon.getSetting("ExcludeTime"),
                "ExcludeAddosOption":MyAddon.getSetting("ExcludeAddosOption"),
                "ExcludeAddos":MyAddon.getSetting("ExcludeAddos"),
                "ExcludeAddosOption2":MyAddon.getSetting("ExcludeAddosOption2"),
                "ExcludeAddos2":MyAddon.getSetting("ExcludeAddos2"),
                "ExcludeAddosOption3":MyAddon.getSetting("ExcludeAddosOption3"),
                "ExcludeAddos3":MyAddon.getSetting("ExcludeAddos3"),
                "ExcludeAddosOption4":MyAddon.getSetting("ExcludeAddosOption4"),
                "ExcludeAddos4":MyAddon.getSetting("ExcludeAddos4"),
                "ExcludeAddosOption5":MyAddon.getSetting("ExcludeAddosOption5"),
                "ExcludeAddos5":MyAddon.getSetting("ExcludeAddos5"),
                "ExcludeAddosOption6":MyAddon.getSetting("ExcludeAddosOption6"),
                "ExcludeAddos6":MyAddon.getSetting("ExcludeAddos6"),
                "enable_font":MyAddon.getSetting("enable_font"),
                "background":MyAddon.getSetting("background"), 
                "bold":MyAddon.getSetting("bold"),
                "size":MyAddon.getSetting("size"),
                "color":MyAddon.getSetting("color"), 
                "background_level":MyAddon.getSetting("background_level"),
                "yify":MyAddon.getSetting("yify"),
                "force":MyAddon.getSetting("force"),
                "popup":MyAddon.getSetting("popup"),
                "storage":MyAddon.getSetting("storage"),
                "firstplace":MyAddon.getSetting("firstplace"),
                "szcode":MyAddon.getSetting("szcode"),
                "sort_subs":MyAddon.getSetting("sort_subs"),
                "auto_translate":MyAddon.getSetting("auto_translate"),
                "arab":MyAddon.getSetting("arab"),
                "spanish":MyAddon.getSetting("spanish"),
                "history_log":MyAddon.getSetting("history_log"),
                "other_lang":MyAddon.getSetting("other_lang"),
                "storage_en":MyAddon.getSetting("storage_en"),
                "all_lang":MyAddon.getSetting("all_lang"),
                "local_files":MyAddon.getSetting("local_files"),
                "Debug":MyAddon.getSetting("Debug")})
   temp=json.dumps(all_setting)
   return  json.loads(temp)
   
xbmc.sleep(100)
log.warning('Action Autosubs:'+str(action))
if action==None:
  update_time=1
  reset_running=0
  sleep_time = 1000
  last_run=0
  time_Show=100
  all_setting=refresh_setting()
  player_monitor = AutoSubsPlayer()
  monitor=MainMonitor()
  log.warning('AutoSubs service_started')
  try:
    rmtree(cache_list_folder)
  except: pass
  mkdirs(cache_list_folder)
  counter_2_hr=7300
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
                    
                      if len(current_list_item_temp)>0 and (('plugin://') in current_list_item_temp or ('smb://') in current_list_item_temp):
                          
                          regex='//(.+?)/'
                          match=re.compile(regex).findall(current_list_item_temp)
                          if len (match)>0:
                               current_list_item=match[0]
                          else:
                             current_list_item=current_list_item_temp
    if running==1:
      reset_running=reset_running+1
      if reset_running>30:
        running=0
        reset_running=0
      else:
        reset_running=0
    xbmc.sleep(1000)
    '''
    if counter_2_hr>7200:
        thread=[]
            
        thread.append(Thread(get_aa_server_ch))
                
            
        thread[0].start()
        
        counter_2_hr=0
    
    counter_2_hr+=1
    '''
  del player_monitor

