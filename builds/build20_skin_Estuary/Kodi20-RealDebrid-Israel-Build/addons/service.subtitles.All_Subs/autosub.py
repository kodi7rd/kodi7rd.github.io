
import time,re,xbmcaddon
import xbmc,xbmcgui,xbmcplugin,xbmcvfs
import os,json,shutil
from resources.modules import cache
from resources.modules import log
from resources.modules.engine import download_sub,get_subtitles,sort_subtitles
from urllib.parse import  unquote_plus, unquote,  quote
from resources.modules.general import TransFolder,clean_name,CachedSubFolder,get_video_data,get_db_data,MySubFolder,notify,Thread,show_results,save_file_name
from urllib.parse import parse_qsl
from resources.modules.sub_window import MySubs
import urllib.parse
from resources.modules import general
from resources.sources import bsplayer
from resources.sources import ktuvit
from resources.sources import opensubtitles
from resources.sources import subscene
from resources.sources import wizdom
Addon=xbmcaddon.Addon()
MyScriptName = xbmcaddon.Addon().getAddonInfo('name')
MyScriptID = xbmcaddon.Addon().getAddonInfo('id')
unque=urllib.parse.unquote_plus
monit = xbmc.Monitor()
ab_req=monit.abortRequested()
log.warning('Starting %s Service!!!'%MyScriptName)


global video_id,pre_video_id,trigger
global current_list_item,break_wait
break_wait=False
current_list_item=""
video_id=""
pre_video_id=""
trigger=False
    
def isExcluded(movieFullPath,current_list_item):
    excluded_addons=['idanplus','sdarot.tv','youtube','kids_new']

    current_list_item=current_list_item+movieFullPath
 
    if (current_list_item.find("pvr://") > -1) :
        log.warning("isExcluded(): Video is playing via Live TV, which is currently set as excluded location.")
        return False
    if (xbmc.getInfoLabel("VideoPlayer.mpaa")=='heb'):
          log.warning("isExcluded(): mpaa!!." )
          return False
    for x in excluded_addons:
        
        if x in current_list_item.lower():
            
            log.warning("isExcluded(): Video is playing from '%s', which is currently set as !!excluded_addons!!."%x )
            
            return False
    if ',' in  Addon.getSetting('ExcludeAddos'):
        ExcludeAddos = Addon.getSetting('ExcludeAddos').split(',')  
    else:
        ExcludeAddos = [Addon.getSetting('ExcludeAddos')]
    for items in ExcludeAddos:
        if items.lower() in current_list_item.lower() and (len(items)>0):
            log.warning("isExcluded(): Video is playing from '%s', which is currently set as !!excluded_addons!!."%items )
            return False
    return True
def place_sub(f_result):
    last_sub_index,all_subs=get_db_data(f_result)
    selected_sub=f_result[0]
    for items in f_result:
        if (last_sub_index==items[8]):
            selected_sub=items
            break
    c_sub_file=None
    for items in f_result:
        params=get_params(selected_sub[4],"")
        download_data=unque(params["download_data"])
        download_data=json.loads(download_data)
        source=(params["source"])
        language=(params["language"])
        filename=unque(params["filename"])
        try:
            sub_file=download_sub(source,download_data,MySubFolder,language,filename)
            fault=False
            log.warning('Auto Sub result:'+str(sub_file))
            xbmc.sleep(100)
            xbmc.Player().setSubtitles(sub_file)
            log.warning('1')
            save_file_name(params["filename"])
            f_count=0
            max_sub_cache=int(Addon.getSetting("subtitle_trans_cache"))
            log.warning('2')
            for filename_o in os.listdir(CachedSubFolder):
                
                f_count+=1
            
            if (f_count>max_sub_cache):
                    for filename_o in os.listdir(CachedSubFolder):
                        f = os.path.join(CachedSubFolder, filename_o)
                        os.remove(f) 
            log.warning(sub_file)
            try:
                file_type=(os.path.splitext(sub_file)[1])
            except:
                file_type=""
            c_sub_file=os.path.join(CachedSubFolder,source+language+filename+file_type)
            if not os.path.exists(c_sub_file):
                    if file_type=='.idx'  or file_type=='.sup':
                        shutil.copy(sub_file,c_sub_file.replace('idx','sub').replace('sup','sub'))
                    shutil.copy(sub_file,c_sub_file)
                    
            break
        except Exception as e:
            log.warning('Error in Sub:'+str(e))
            selected_sub=items
            fault=True
            
        
    return c_sub_file
def display_subtitle(f_result,video_data,last_sub_index,all_subs,argv1):
    
    all_d=[]
    sub_final_data=[]
    for items in f_result:
            try:
                val=all_subs[items[8]]
              
            except:
                val=None
                pass
            
            if (last_sub_index==items[8]):
                added_string='[COLOR deepskyblue][B][I]>> '
            elif val:
                added_string='[COLOR deepskyblue][B][I]'
            else:
                added_string='[COLOR gold]'
            if xbmc.Player().isPlaying():
                sub_name=added_string+str(items[5])+ "% "+'[/COLOR]'+items[1]
                if ('[B][I]' in added_string):
                    sub_name=sub_name+'[/I][/B]'
                if video_data['file_original_path'].replace("."," ").lower() in items[1].replace("."," ").lower() and len(video_data['file_original_path'].replace("."," "))>5 or items[5]>80:
                         #json_value['label2']='[COLOR gold] GOLD [B]'+json_value['label2']+'[/B][/COLOR]'
                         sub_name='[COLOR gold] GOLD [B]'+sub_name+'[/B][/COLOR]'
            else:
                sub_name=items[1]
            
            sub_final_data.append({'label':items[0],
                                  'label2':sub_name, 
                                  'iconImage':items[2],
                                  'thumbnailImage':items[3],
                                  'url':items[4],
                                  
                                  "sync": items[6],
                                  "hearing_imp":items[7]})
                                       
                
    sub_final_data.append({'label':"פתח הגדרות הרחבה",
                          'label2':'[COLOR plum][I]'+ "פתח הגדרות הרחבה"+'[/I][/COLOR]', 
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url':"plugin://%s/?action=open_settings" % (MyScriptID),
                          "sync": "",
                          "hearing_imp":""})
            
    
    
    sub_final_data.append({'label':"בטל כתוביות",
                          'label2':'[COLOR seagreen][I]'+ "בטל כתוביות"+'[/I][/COLOR]', 
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url':"plugin://%s/?action=disable_subs"% (MyScriptID),
                          "sync": "",
                          "hearing_imp":""})
                          
    sub_final_data.append({'label':"פתח חלון כתוביות",
                          'label2':'[COLOR lightblue][I]'+ "חלון כתוביות"+'[/I][/COLOR]', 
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url': "plugin://%s/?action=sub_window"% (MyScriptID),
                          "sync": "",
                          "hearing_imp":""})
    
    sub_final_data.append({'label':"ניקוי",
                          'label2':'[COLOR khaki][I]'+"אפס את נתוני המטמון של התוסף"+'[/I][/COLOR]', 
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url':"plugin://%s/?action=clean" % (MyScriptID),
                          "sync": "",
                          "hearing_imp":""})
    sub_final_data.append({'label':"ניקוי קאש כתוביות",
                          'label2':'[COLOR khaki][I]'+"אפס את נתוני המטמון של התוסף"+'[/I][/COLOR]', 
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url':"plugin://%s/?action=clean_folders" % (MyScriptID),
                          "sync": "",
                          "hearing_imp":""})
    return sub_final_data
   
    
def get_params(argv2,argv1):
    if argv2!="None":
        param = dict(parse_qsl(argv2.replace('?','')))
    else:
        
        param={}
        param['action']=argv1
    return param
def sub_from_main(arg):
    argv2=arg.split('$$$$$$$$')[0]
    argv1=arg.split('$$$$$$$$')[1]
    params = get_params(argv2,argv1)

    video_data=get_video_data()
    log.warning(params)
    action=None
    
    
    try:        
        action=(params["action"])
    except:
            pass
    log.warning(action)
    try:
        download_data=unque(params["download_data"])
        download_data=json.loads(download_data)
    except:
        pass
    try:
        source=(params["source"])
    except:
        pass
    try:
        filename=unque(params["filename"])
    except:
        pass
    try:
        language=(params["language"])
    except:
        pass
    from resources.modules import general
    if action!="sub_window_unpause" and action!="sub_window":
    
        general.show_msg="מוריד כתוביות"
    if action=='search' or action=='download':
        general.with_dp=True
    else:
        general.with_dp=False
    thread=[]
            
    thread.append(Thread(show_results))
    
    thread[0].start()
        
    if action=='search':
        log.warning('Foundmanual_search33:')
        
        
        log.warning(video_data)
        from resources import main
        main.from_autosub=True
        tag_original=video_data['Tagline']
        video_data.pop('Tagline')
        
        file_org=video_data['file_original_path']
        video_data.pop('file_original_path')
        
        f_result=cache.get(get_subtitles,24,video_data,table='subs')
        video_data['file_original_path']=file_org
        video_data['Tagline']=tag_original
        
        f_result=cache.get(sort_subtitles,24,f_result,video_data,table='subs')
        last_sub_index,all_subs=get_db_data(f_result)
        return_result=display_subtitle(f_result,video_data,last_sub_index,all_subs,argv1)
        log.warning(return_result)
        
    
    elif action=='download':
        
        
       
        sub_file=download_sub(source,download_data,MySubFolder,language,filename)
        fault=False
        log.warning('Auto Sub result:'+str(sub_file))
        xbmc.sleep(100)
        xbmc.Player().setSubtitles(sub_file)
        save_file_name(filename)
        f_count=0
        max_sub_cache=int(Addon.getSetting("subtitle_trans_cache"))
        for filename_o in os.listdir(CachedSubFolder):
            
            f_count+=1
        
        if (f_count>max_sub_cache):
                for filename_o in os.listdir(CachedSubFolder):
                    f = os.path.join(CachedSubFolder, filename_o)
                    os.remove(f) 
  

        try:
            file_type=(os.path.splitext(sub_file)[1])
        except:
            file_type=""
        c_sub_file=os.path.join(CachedSubFolder,source+language+filename+file_type)

        if not os.path.exists(c_sub_file):
                if file_type=='.idx' or file_type=='.sup':
                    shutil.copy(sub_file,c_sub_file.replace('idx','sub').replace('sup','sub'))
                
                shutil.copy(sub_file,c_sub_file)
                
        return_result=json.dumps(sub_file)
    
    elif action=='open_settings':
        xbmcaddon.Addon().openSettings()
        return_result=json.dumps(action)
    elif action=='clean':
        cache.clear(['subs'])
        notify( "המטמון נוקה" )
        return_result=json.dumps(action)
    elif action=='disable_subs':
        xbmc.Player().setSubtitles("")
        return_result=json.dumps(action)
        notify("כתוביות בוטלו")
    elif action=='sub_window':
        tag_original=video_data['Tagline']
        video_data.pop('Tagline')
        
        file_org=video_data['file_original_path']
        video_data.pop('file_original_path')
        
        f_result=cache.get(get_subtitles,24,video_data,table='subs')
        video_data['file_original_path']=file_org
        video_data['Tagline']=tag_original
        
        f_result=cache.get(sort_subtitles,24,f_result,video_data,table='subs')
        xbmc.executebuiltin('Dialog.Close(all,true)')
        xbmc.Player().pause()
        last_sub_index,all_subs=get_db_data(f_result)
        xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_subs",'')
        window = MySubs('Subtitles - ' ,f_result,f_result,video_data,all_subs,last_sub_index)
        return_result=json.dumps(action)
    elif action=='sub_window_unpause':
        tag_original=video_data['Tagline']
        video_data.pop('Tagline')
        
        file_org=video_data['file_original_path']
        video_data.pop('file_original_path')
        
        f_result=cache.get(get_subtitles,24,video_data,table='subs')
        video_data['file_original_path']=file_org
        video_data['Tagline']=tag_original
        
        f_result=cache.get(sort_subtitles,24,f_result,video_data,table='subs')
        xbmc.executebuiltin('Dialog.Close(all,true)')
        
        last_sub_index,all_subs=get_db_data(f_result)
        xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_subs",'')
        window = MySubs('Subtitles - ' ,f_result,f_result,video_data,all_subs,last_sub_index)
        return_result=json.dumps(action)
    elif action=='next':
        from resources.modules import general
        general.with_dp=False
        general.show_msg="כתובית הבאה"
        log.warning(general.show_msg)
        thread=[]
                    
        thread.append(Thread(show_results))

        thread[0].start()
    
        tag_original=video_data['Tagline']
        video_data.pop('Tagline')
        
        file_org=video_data['file_original_path']
        video_data.pop('file_original_path')
        
        f_result=cache.get(get_subtitles,24,video_data,table='subs')
        video_data['file_original_path']=file_org
        video_data['Tagline']=tag_original
        
        f_result=cache.get(sort_subtitles,24,f_result,video_data,table='subs')
        last_sub_index,all_subs=get_db_data(f_result)
        next_one=False
        selected_sub=None
        for items in f_result:
            if (next_one):
                if (last_sub_index!=items[8]):
                    selected_sub=items
                    
                    break
                else:
                    next_one=False
            if (last_sub_index==items[8]):
                next_one=True
            
        if selected_sub:
            params=get_params(selected_sub[4],"")
            download_data=unque(params["download_data"])
            download_data=json.loads(download_data)
            source=(params["source"])
            language=(params["language"])
            filename=params["filename"]
            general.show_msg="מוריד"
            sub_file=download_sub(source,download_data,MySubFolder,language,filename)
            log.warning('Next Sub result:'+str(sub_file))
            general.show_msg="מוכן"
            
            xbmc.Player().setSubtitles(sub_file)
            save_file_name(params["filename"])
            
        else:
            general.show_msg="סוף הכתוביות"
            
        xbmc.sleep(800)
        general.show_msg="END"
        return_result=json.dumps(action)
    elif action=='previous':
        from resources.modules import general
        general.with_dp=False
        general.show_msg="כתובית קודמת"
        
        thread=[]
                    
        thread.append(Thread(show_results))

        thread[0].start()
        tag_original=video_data['Tagline']
        video_data.pop('Tagline')
        
        file_org=video_data['file_original_path']
        video_data.pop('file_original_path')
        
        f_result=cache.get(get_subtitles,24,video_data,table='subs')
        video_data['file_original_path']=file_org
        video_data['Tagline']=tag_original
        
        f_result=cache.get(sort_subtitles,24,f_result,video_data,table='subs')
        last_sub_index,all_subs=get_db_data(f_result)
        pre_one=None
        found=None
        for items in f_result:
            if (found):
                if ((pre_one) and (last_sub_index!=pre_one[8])):
                    selected_sub=pre_one
                    
                    break
                else:
                    found=None
            if (last_sub_index==items[8]):
                found=True
            else:
                pre_one=items
        log.warning('found_P:'+str(found))
        if found:
            params=get_params(selected_sub[4],"")
            download_data=unque(params["download_data"])
            download_data=json.loads(download_data)
            source=(params["source"])
            language=(params["language"])
            filename=params["filename"]
            sub_file=download_sub(source,download_data,MySubFolder,language,filename)
            log.warning('previous Sub result:'+str(sub_file))
            general.show_msg=sub_file
            xbmc.sleep(100)
            xbmc.Player().setSubtitles(sub_file)
            save_file_name(params["filename"])
        else:
            general.show_msg="זאת הכתובית הראשונה"
            xbmc.sleep(800)
        general.show_msg="END"
        return_result=json.dumps(action)
    elif action=='clean_folders':
        general.show_msg="מוחק קבצים"
        try:
            shutil.rmtree(CachedSubFolder)
        except: pass
        xbmcvfs.mkdirs(CachedSubFolder)
        try:
            shutil.rmtree(TransFolder)
        except: pass
        xbmcvfs.mkdirs(TransFolder)
        return_result=json.dumps(action)
        general.show_msg="END"
    xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_return",json.dumps(return_result))

    
    
current_list_item=""
xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_subs",'')
xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("fast_subs",'')
class KodiMonitor(xbmc.Monitor):
    def onSettingsChanged(self):
        Addon=xbmcaddon.Addon()
        #notify('Settings change')
        manual_searh=xbmcaddon.Addon('service.subtitles.All_Subs').getSetting("man_search_subs")
        if  manual_searh!='':
            
            sub_from_main(manual_searh)
        
            general.show_msg="END"
            xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_subs",'')
        Mando_search=xbmcaddon.Addon('service.subtitles.All_Subs').getSetting("fast_subs")
        if Mando_search!='':
            
            
            video_data=unque(Mando_search)
            video_data=json.loads(video_data)
            log.warning('FoundMando_search33:')
            
            video_data['title']=clean_name(video_data['title'])
            video_data['OriginalTitle']=clean_name(video_data['OriginalTitle'])
            log.warning(video_data)
            from resources import main
            main.from_autosub=True
            tag_original=video_data['Tagline']
            video_data.pop('Tagline')
            
            
            
            f_result=cache.get(get_subtitles,24,video_data,table='subs')
            
            video_data['Tagline']=tag_original
            xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("fast_subs",'')
            
            
            
    def onNotification( self, sender, method, data):
        global video_id,pre_video_id,trigger
        global current_list_item,break_wait
        Addon=xbmcaddon.Addon()
        from resources.modules import general
        
        if method=='Player.OnStop':
            trigger=False
            
            video_id=""
            xbmcgui.Window(10000).setProperty("subs.player_filename","")
            break_wait=True
        if method=='Player.OnPlay':
            log.warning('Player ONONON::')
            manual_searh=""
            while  manual_searh!='':
                manual_searh=xbmcaddon.Addon('service.subtitles.All_Subs').getSetting("fast_subs")
                xbmc.sleep(100)
            ExcludeTime = int((Addon.getSetting('ExcludeTime')))*60
            
            video_data=get_video_data()
            
            pre_video_id=video_id
            video_id=video_data['OriginalTitle']+video_data['imdb']+str(video_data['season'])+str(video_data['episode'])
            
            if (video_id!=pre_video_id):
                
                
                trigger=True
            pre_video_id=video_id
            
                
            
            sub_name=None
            log.warning(current_list_item_temp)
            
            if  trigger:
                trigger=False
                totalTime=0
                
                
                
                force_download=True
                if  Addon.getSetting("force")=='true':
                  force_download=True
                if  Addon.getSetting("force")=='false' and xbmc.getCondVisibility("VideoPlayer.HasSubtitles"):
                  force_download=False
                
                
                log.warning('current_list_item::'+str(current_list_item))
                if Addon.getSetting("autosub")=='true':
                  movieFullPath = xbmc.Player().getPlayingFile()
                  
                  excluded=isExcluded(movieFullPath,current_list_item)
                  if not excluded:
                    trigger=False
                  
                  if  force_download==True and video_data['mpaa']!='heb' and excluded:
                   
                    if  Addon.getSetting("pause")=='true':
                        xbmc.Player().pause()
                    
                    general.show_msg="מוריד כתוביות"
                    general.with_dp=False
                    thread=[]
                            
                    thread.append(Thread(show_results))
                    from resources import main
                    main.from_autosub=True
                    thread[0].start()
                    
                    
                    try:
                        tag_original=video_data['Tagline']
                        video_data.pop('Tagline')
                        
                        file_org=video_data['file_original_path']
                        video_data.pop('file_original_path')
                        
                        f_result=cache.get(get_subtitles,24,video_data,table='subs')
                        video_data['file_original_path']=file_org
                        video_data['Tagline']=tag_original
                        
                        f_result=cache.get(sort_subtitles,24,f_result,video_data,table='subs')
                        if len(f_result)>0:
                            sub_name=place_sub(f_result)
                        
                    except Exception as e:
                        import linecache
              
                        exc_type, exc_obj, tb = sys.exc_info()
                        f = tb.tb_frame
                        lineno = tb.tb_lineno
                        filename = f.f_code.co_filename
                        linecache.checkcache(filename)
                        line = linecache.getline(filename, lineno, f.f_globals)
                        
                        log.warning('ERROR IN Downloading:'+str(lineno))
                        log.warning('inline:'+line)
                        log.warning(e)
                        notify(str(e))
                    
                    
                    if  Addon.getSetting("pause")=='true':
                        xbmc.Player().pause()
                    
                    if sub_name:
                        general.show_msg="[COLOR lightblue]כתובית מוכנה[/COLOR]"
                    else:
                        general.show_msg="[COLOR red]אין כתוביות[/COLOR]"
                    
                    
                    
                    
                  else:
                    log.warning('Not Downloading:')
                    log.warning(totalTime)
                    log.warning(ExcludeTime)
                    log.warning(force_download)
                    log.warning(excluded)
                    log.warning(video_data['mpaa'])
                  counter=0
                  vidtime_pre=0
                  once=True
                  while (not break_wait) and counter<50:
                      try:
                          vidtime = xbmc.Player().getTime()
                          if vidtime>0:
                                if once:
                                    vidtime_pre=vidtime
                                    once=False
                                totalTime = xbmc.Player().getTotalTime()
                                if vidtime_pre!=vidtime:
                                    break
                                vidtime_pre=vidtime
                                
                          counter+=1
                          xbmc.sleep(100)
                      except:
                        break
                  log.warning('totalTime::'+str(totalTime))
                  if totalTime < ExcludeTime:
                    xbmc.Player().setSubtitles("")
                  if (sub_name):
                    log.warning('Place SUb::'+str(sub_name))
                    xbmc.Player().setSubtitles(sub_name)
                  xbmc.sleep(2000)
                  general.show_msg="END"
                    
monitor=KodiMonitor()

while not ab_req:
    
    current_list_item_temp=(xbmc.getInfoLabel("ListItem.FileNameAndPath"))
    if len(current_list_item_temp)>0 and (('plugin://') in current_list_item_temp or ('smb://') in current_list_item_temp or ('pvr://') in current_list_item_temp):
            if 'pvr://' in current_list_item_temp:
                current_list_item='pvr://video' 
            else:
                regex='//(.+?)/'
                match=re.compile(regex).findall(current_list_item_temp)
                if len (match)>0:
                   current_list_item=match[0]
                else:
                    current_list_item=current_list_item_temp
    if monitor.waitForAbort(1):
       break
del monitor
        
        

    
    

    
  