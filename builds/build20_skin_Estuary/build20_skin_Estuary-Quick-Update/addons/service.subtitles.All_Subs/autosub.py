
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

global found_embed_ok

global video_id,pre_video_id,trigger
global current_list_item,break_wait
break_wait=False
current_list_item=""
video_id=""
pre_video_id=""
trigger=False
found_embed_ok=False
que=urllib.parse.quote_plus
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
    if ',' in  Addon.getSetting('ExcludeAddons'):
        ExcludeAddons = Addon.getSetting('ExcludeAddons').split(',')  
    else:
        ExcludeAddons = [Addon.getSetting('ExcludeAddons')]
    for items in ExcludeAddons:
        if items.lower() in current_list_item.lower() and (len(items)>0):
            log.warning("isExcluded(): Video is playing from '%s', which is currently set as !!excluded_addons!!."%items )
            return False
    return True
def find_for_break():
    counter=0
    vidtime=0
        
    
    
    log.warning('Wating for video')
    once=True
    subs=[]
    while counter<50:
        
        try:
          subs=xbmc.Player().getAvailableSubtitleStreams()
          if len(subs)>0:
            break
          
          vidtime = xbmc.Player().getTime()
          if vidtime>0:
                if once:
                    vidtime_pre=vidtime
                    once=False
                totalTime = xbmc.Player().getTotalTime()
                if vidtime_pre!=vidtime:
                    break
                vidtime_pre=vidtime
                
          
          
        except:
          pass
        counter+=1
        xbmc.sleep(100)
        log.warning('Vid Time:'+str(vidtime))
    if 'heb' in subs:
        log.warning('Break All')
        general.break_all=True
def find_embed(f_result):
    global found_embed_ok
    found_embed_ok=False
    counter=0
    vidtime=0
        
    
    
    log.warning('Wating for video')
    once=True
    while counter<50:
        
        try:
          subs=xbmc.Player().getAvailableSubtitleStreams()
          #if len(subs)>0:
          #  break
          vidtime = xbmc.Player().getTime()
          if vidtime>0:
                if once:
                    vidtime_pre=vidtime
                    once=False
                totalTime = xbmc.Player().getTotalTime()
                if vidtime_pre!=vidtime:
                    log.warning(vidtime)
                    log.warning(vidtime_pre)
                    break
                vidtime_pre=vidtime
                
          
          
        except:
          pass
        counter+=1
        xbmc.sleep(100)
        log.warning('Vid Time:'+str(vidtime))
    log.warning('counter:'+str(counter))
    
    log.warning('subs:')
    log.warning(subs)
    index_heb=0
    for items in subs:
        if items=='heb':
            general.break_all=True
            log.warning('Placing Stream Sub: '+str(index_heb))
            xbmc.Player().setSubtitleStream(index_heb)
            found_embed_ok=True
            if (general.show_msg!="END"):
                notify( "נבחרה כתובית מובנית בעברית" )
            else:
                notify( "נבחרה כתובית מובנית בעברית" )
            
            video_data=get_video_data()
            save_data=video_data['imdb']+str(video_data['season'])+str(video_data['episode'])+video_data['OriginalTitle']+video_data['Tagline']+'כתובית מובנית'
            if (video_data['Tagline']!=""):
                save_file_name(que(save_data))
            break
        index_heb+=1
    xbmc.sleep(500)
    general.show_msg="END"
def place_sub(f_result,last_sub_index,all_subs):
    log.warning('Place sub:')
    
    
    general.show_msg="מוריד כתובית נבחרת"
    selected_sub=f_result[0]
    for items in f_result:
        if (last_sub_index==items[8]):
            selected_sub=items
            break
    c_sub_file=None
    for items in f_result:
        general.show_msg="מוריד כתובית נבחרת"
        if general.break_all:
            break
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
            if (sub_file!='Dont use'):
            
                notify( f"{language} | {source} | {str(items[5])}% | {filename}" )
            
            
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
            else:
                
                c_sub_file='Dont use'
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
                    sub_name=sub_name+'[/I]'
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
    
    sub_final_data.append({'label':"קאש",
                          'label2':'[COLOR khaki][I]'+"ניקוי קאש כתוביות"+'[/I][/COLOR]',
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url':"plugin://%s/?action=clean" % (MyScriptID),
                          "sync": "",
                          "hearing_imp":""})
    sub_final_data.append({'label':"קאש",
                          'label2':'[COLOR khaki][I]'+"ניקוי קאש תרגום מכונה"+'[/I][/COLOR]',  
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url':"plugin://%s/?action=clean_folders" % (MyScriptID),
                          "sync": "",
                          "hearing_imp":""})
    return sub_final_data
def add_demo_embbded(f_result_temp):
    index_sub=0
    video_data=get_video_data()
    f_result_start=[]
    download_data={}
    download_data['url']=str(index_sub)
    download_data['file_name']=str(index_sub)
    save_data=video_data['imdb']+str(video_data['season'])+str(video_data['episode'])+video_data['OriginalTitle']+video_data['Tagline']+'כתובית מובנית'
    
    url = "plugin://%s/?action=download&download_data=%s&filename=%s&language=%s&source=bsplayer" % (MyScriptID,
                                                        que(json.dumps(download_data)),
                                                        que(que(que(save_data))),
                                                        "Hebrew")
    json_value={'url':url,
                         'label':"Hebrew",
                         'label2':'[LOC] '+' כתובית מובנית',
                         'iconImage':"0",
                         'thumbnailImage':"he",
                         'hearing_imp':'false',
                         'site_id':'[LOC]',
                         'sub_color':'GOLD',
                         'filename':que(save_data),
                         'sync': 'true'}
                         
                    
    f_result_start.append((json_value['label'],'[COLOR %s]'%json_value['sub_color']+json_value['label2']+'[/COLOR]',json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],101,json_value['sync'],json_value['hearing_imp'],json_value['filename'],json_value['site_id']))
    
    for items in f_result_temp:
        f_result_start.append(items)
    return f_result_start
def add_embbded(f_result):
        video_data=get_video_data()
        subs=xbmc.Player().getAvailableSubtitleStreams()
        log.warning('Embbeded subs Engine:')
        log.warning(subs)
        
        index_sub=0
        
        f_result_start=[]
        for items in subs:
            
            if items=='heb':
                download_data={}
                download_data['url']=str(index_sub)
                download_data['file_name']=str(index_sub)
                save_data=video_data['imdb']+str(video_data['season'])+str(video_data['episode'])+video_data['OriginalTitle']+video_data['Tagline']+'כתובית מובנית'
                
                url = "plugin://%s/?action=download&download_data=%s&filename=%s&language=%s&source=bsplayer" % (MyScriptID,
                                                                    que(json.dumps(download_data)),
                                                                    que(que(que(save_data))),
                                                                    "Hebrew")
                json_value={'url':url,
                                     'label':"Hebrew",
                                     'label2':'[LOC] '+' כתובית מובנית',
                                     'iconImage':"0",
                                     'thumbnailImage':"he",
                                     'hearing_imp':'false',
                                     'site_id':'[LOC]',
                                     'sub_color':'GOLD',
                                     'filename':que(save_data),
                                     'sync': 'true'}
                                     
                                
                f_result_start.append((json_value['label'],'[COLOR %s]'%json_value['sub_color']+json_value['label2']+'[/COLOR]',json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],101,json_value['sync'],json_value['hearing_imp'],json_value['filename'],json_value['site_id']))
                
            index_sub+=1
       
        for items in f_result_start:
        
            f_result.insert(0, items)
        return f_result
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
        f_result=add_embbded(f_result)
  
        last_sub_index,all_subs=get_db_data(f_result)

        return_result=display_subtitle(f_result,video_data,last_sub_index,all_subs,argv1)
        log.warning(return_result)
        #xbmc.Player().setSubtitleStream(1)
    
    elif action=='download':
        
        
        
        log.warning(params["filename"])
        sub_file=download_sub(source,download_data,MySubFolder,language,filename)
        fault=False
        if (sub_file!='Dont use'):
        
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
                    
        else:
            notify( 'נבחרה כתובית מובנית, המתן מספר שניות' )
            log.warning(filename)
            save_file_name(filename)
        return_result=json.dumps(sub_file)
        
    elif action=='open_settings':
        xbmcaddon.Addon().openSettings()
        return_result=json.dumps(action)
    elif action=='clean':
        cache.clear(['subs'])
        notify( "קאש כתוביות נוקה" )
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
        f_result=add_embbded(f_result)
        last_sub_index,all_subs=get_db_data(f_result)
        xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_subs",'')
        window = MySubs('DarkSubs - חלון כתוביות' ,f_result,f_result,video_data,all_subs,last_sub_index)
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
        f_result=add_embbded(f_result)
        last_sub_index,all_subs=get_db_data(f_result)
        xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_subs",'')
        window = MySubs('DarkSubs - חלון כתוביות' ,f_result,f_result,video_data,all_subs,last_sub_index)
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
        f_result=add_embbded(f_result)
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
            if (sub_file!='Dont use'):
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
        f_result=add_embbded(f_result)
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
            if (sub_file!='Dont use'):
                xbmc.Player().setSubtitles(sub_file)
                save_file_name(params["filename"])
            else:
                save_file_name(unque(params["filename"]))
                
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
        notify( "קאש תרגום מכונה נוקה" )
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
        global current_list_item,break_wait,found_embed_ok
        Addon=xbmcaddon.Addon()
        from resources.modules import general
        last_sub_index=""
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
                f_result=None
                
                
                force_download=True
                if  Addon.getSetting("force")=='true':
                  force_download=True
                if  Addon.getSetting("force")=='false' and xbmc.getCondVisibility("VideoPlayer.HasSubtitles"):
                  force_download=False
                
                
                log.warning('current_list_item::'+str(current_list_item))
                if Addon.getSetting("autosub")=='true':
                  try:
                      movieFullPath = xbmc.Player().getPlayingFile()

                      excluded=isExcluded(movieFullPath,current_list_item)
                  except: pass
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
                        
                        temp=add_demo_embbded(f_result)
                        general.show_msg="מחפש כתובית קודמת"
                        last_sub_index,all_subs=get_db_data(temp)
                        
                        if (last_sub_index=="") or 'כתובית מובנית' in unque(last_sub_index):
                          thread=[]
                          thread.append(Thread(find_for_break))
                          thread[0].start()
                      
                        if len(f_result)>0 and 'כתובית מובנית' not in unque(last_sub_index):
                            sub_name=place_sub(f_result,last_sub_index,all_subs)
                        
                    except Exception as e:
                        import linecache
              
                        exc_type, exc_obj, tb = sys.exc_info()
                        f = tb.tb_frame
                        lineno = tb.tb_lineno
                        filename = f.f_code.co_filename
                        linecache.checkcache(filename)
                        log.warning('Error in subs:'+str(e)+','+'line:'+str(lineno))
                    if not found_embed_ok:
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
                  if totalTime < ExcludeTime and excluded:
                    xbmc.Player().setSubtitles("")
                  log.warning(sub_name)
                  if (sub_name) and sub_name!='Dont use':
                    log.warning('Place SUb::'+str(sub_name))
                    xbmc.Player().setSubtitles(sub_name)
                  if (last_sub_index=="") or 'כתובית מובנית' in unque(last_sub_index) and f_result:
                      thread=[]
                      thread.append(Thread(find_embed,f_result))
                      thread[0].start()
                  xbmc.sleep(2000)
                  if (sub_name) and sub_name!='Dont use':
                    xbmc.Player().setSubtitles(sub_name)
                  
                  general.show_msg="END"
                    
monitor=KodiMonitor()

# Auto clean DarkSubs cache + machine translate folders on Kodi startup.
if  Addon.getSetting("clean_cache_on_startup") == 'true':
    try:
        log.warning("Clean cache on startup Starting...")
        xbmc.executebuiltin("RunScript(special://home/addons/service.subtitles.All_Subs/resources/modules/clean_cache_functions.py, clean_all_cache)")
        log.warning("Clean cache on startup Finished.")
    except Exception as e:
        log.warning(f"Clean cache on startup FAILED. ERROR: {str(e)}")
        pass

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
        
        

    
    

    
  