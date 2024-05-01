import time,re,xbmcaddon
import xbmc,xbmcgui,xbmcplugin,xbmcvfs
import os,json,shutil
from resources.modules import cache
from resources.modules import log
from resources.modules.engine import download_sub,get_subtitles,sort_subtitles
from urllib.parse import  unquote_plus, unquote,  quote
from resources.modules.twilight import write_heb_embedded_taglines
from resources.modules.twilight.write_heb_embedded_taglines_check import write_heb_embedded_taglines_check_func
from resources.modules.general import TransFolder,clean_name,CachedSubFolder,get_video_data,get_db_data,MySubFolder,notify,Thread,show_results,save_file_name
from urllib.parse import parse_qsl
from resources.modules.sub_window import MySubs
import urllib.parse
from resources.modules import general
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
que=urllib.parse.quote_plus
    
####################################################################################
    
# Currently only for Hebrew/English, the most common.
def translate_sub_language_to_hebrew(language):
    if "Hebrew" in language:
        return "עברית"
    elif language == "English":
        return "אנגלית"
    elif language == "Russian":
        return "רוסית"
    elif language == "Arabic":
        return "ערבית"
    else:
        return language
####################################################################################

def wait_for_video():

    log.warning('Waiting for video')
    counter=0
    vidtime_pre=0
    once=True
    
    while counter<70:
        try:
            vidtime = xbmc.Player().getTime()
            if vidtime>0:
                  if once:
                      vidtime_pre=vidtime
                      once=False
                  if vidtime_pre!=vidtime:
                      break
                  vidtime_pre=vidtime
                  
            counter+=1
            xbmc.sleep(100)
        except:
          break
          
    log.warning(f"DEBUG | Time waited for video to start (wait_for_video): {counter/10} seconds.")

######################### EMBEDDED SUBS #####################################
    
def determine_placeHebrewEmbeddedSub(last_sub_in_cache_is_external, last_sub_in_cache_is_heb_embedded, first_external_sub_language):

    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()

    # Check if "auto_place_hebrew_embedded_subs" setting is 'true'
    if Addon.getSetting("auto_place_hebrew_embedded_subs") == 'true':
        # Check if last sub cache is not an external subtitle (not empty or not embedded Hebrew sub).
        if not last_sub_in_cache_is_external:
            return True
            
    else:
        # Check if first external subtitle language is NOT "Hebrew"
        if first_external_sub_language != "Hebrew":
            # Check if last sub cache is not an external subtitle (not empty or not embedded Hebrew sub).
            if not last_sub_in_cache_is_external:
                return True
                
        # If first_external_sub_language=="Hebrew", Check if last sub cache is Hebrew embedded
        elif last_sub_in_cache_is_heb_embedded:
            return True 
    
    return False
    
    
def wait_for_video_and_return_subs_list():

    log.warning('Waiting for video')
    counter=0
    vidtime=0
    once=True
    subs=[]
    
    while counter<70:
        try:
          subs=xbmc.Player().getAvailableSubtitleStreams()
          if len(subs)>0:
            log.warning(f"DEBUG | Time waited for video to start (wait_for_video_and_return_subs_list): {counter/10} seconds.")
            return subs
          
          vidtime = xbmc.Player().getTime()
          if vidtime>0:
                if once:
                    vidtime_pre=vidtime
                    once=False
                if vidtime_pre!=vidtime:
                    break
                vidtime_pre=vidtime
        except:
          pass
        counter+=1
        xbmc.sleep(100)
    
    log.warning(f"DEBUG | Time waited for video to start (wait_for_video_and_return_subs_list): {counter/10} seconds.")    
    return subs
        
        
def check_if_embedded_sub_exists(embedded_language):
    subs = wait_for_video_and_return_subs_list()
    return any(sub == embedded_language for sub in subs)
    
    
def get_embedded_sub_index(subs, embedded_language):
    return next((index for index, sub in enumerate(subs) if sub == embedded_language), None)

    
def set_embedded_hebrew_sub(video_data):

    subs = wait_for_video_and_return_subs_list()
    index_sub = get_embedded_sub_index(subs, 'heb')
    
    if index_sub is not None:
        log.warning(f'Placing Hebrew embedded Stream Sub: index_sub={str(index_sub)}')
        xbmc.Player().setSubtitleStream(index_sub)
        
        save_data='HebrewSubEmbedded'+video_data['imdb']+str(video_data['season'])+str(video_data['episode'])+video_data['OriginalTitle']+video_data['Tagline']
        save_file_name(que(save_data),"Hebrew",video_data)
            
        xbmc.sleep(300)
    
    
def add_embbded_sub_if_exists(video_data, f_result, embedded_language):

    # Avoid checking when using subtitles search from context menu (display_subtitle)
    if not xbmc.Player().isPlaying():
        log.warning(f'DEBUG | add_embbded_sub_if_exists STOP | embedded_language={embedded_language} | xbmc.Player().isPlaying(): {xbmc.Player().isPlaying()}')
        return f_result

    if embedded_language=='heb':
        try:
            global is_embedded_hebrew_sub_exists
            if not is_embedded_hebrew_sub_exists:
                log.warning(f'DEBUG | add_embbded_sub_if_exists STOP | embedded_language={embedded_language} | is_embedded_hebrew_sub_exists: {is_embedded_hebrew_sub_exists}')
                return f_result
        except:
            pass
            
    if embedded_language=='heb':
        embedded_sub_name_prefix = 'HebrewSubEmbedded'
        FullLanguageName = 'Hebrew'
        thumbnailImageLanguageName = 'he'
        EmbeddedSubLabel = 'תרגום מובנה בעברית'
    elif embedded_language=='eng':
        embedded_sub_name_prefix = 'EnglishSubEmbedded'
        FullLanguageName = 'English'
        thumbnailImageLanguageName = 'en'
        EmbeddedSubLabel = 'תרגום מובנה באנגלית'
        
    # Exit if embedded sub is already present in f_result. Else, continue. Safe checking again.
    for items in f_result:
        if embedded_sub_name_prefix in items[8]:
            return f_result
            
    subs=wait_for_video_and_return_subs_list()
    index_sub = get_embedded_sub_index(subs, embedded_language)
    log.warning(f'add_embbded_sub_if_exists | embedded_language={embedded_language} | Embbeded subs list: {subs} | index_sub={index_sub}')

    if index_sub is not None:
        download_data={}
        download_data['url']=str(index_sub)
        download_data['file_name']=str(index_sub)
        save_data=embedded_sub_name_prefix+video_data['imdb']+str(video_data['season'])+str(video_data['episode'])+video_data['OriginalTitle']+video_data['Tagline']
        
        url = "plugin://%s/?action=download&download_data=%s&filename=%s&language=%s&source=%s" % (MyScriptID,
                                                            que(json.dumps(download_data)),
                                                            que(que(que(save_data))),
                                                            FullLanguageName,
                                                            embedded_sub_name_prefix)
        json_value={'url':url,
                             'label':FullLanguageName,
                             'label2':'[LOC] '+ EmbeddedSubLabel,
                             'iconImage':"0",
                             'thumbnailImage':thumbnailImageLanguageName,
                             'hearing_imp':'false',
                             'site_id':'[LOC]',
                             'sub_color':'cyan',
                             'filename':que(save_data),
                             'sync': 'true'}
                             
                        
        index = 0
        if embedded_language=='eng':
            # Find the index where English subtitles should be inserted
            for i, sub in enumerate(f_result):
                if sub[0] == 'Hebrew':
                    index = i + 1  # Insert after the last Hebrew subtitle
                             
            
        f_result.insert(index, (json_value['label'],'[COLOR %s]'%json_value['sub_color']+json_value['label2']+'[/COLOR]',json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],101,json_value['sync'],json_value['hearing_imp'],json_value['filename'],json_value['site_id']))
        
    return f_result
    
    
def add_embbded_subs_to_subs_list(video_data, f_result):

    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
        
    # Add Hebrew Embbeded Subtitles if exists
    search_language_hebrew_bool = (Addon.getSetting('language_hebrew') == 'true' or Addon.getSetting("all_lang") == 'true')
    if search_language_hebrew_bool:
        f_result=add_embbded_sub_if_exists(video_data, f_result, 'heb')
        
    # Add English Embbeded Subtitles if exists
    search_language_english_bool = (Addon.getSetting('language_english') == 'true' or Addon.getSetting("all_lang") == 'true')
    if search_language_english_bool:
        f_result=add_embbded_sub_if_exists(video_data, f_result, 'eng')
    
    return f_result
        
####################################################################################
    
def isPlayingAddonExcluded(movieFullPath,current_list_item):
    excluded_addons=['idanplus','sdarot.tv','youtube','kids_new']

    current_list_item=current_list_item+movieFullPath
 
    if (current_list_item.find("pvr://") > -1) :
        log.warning("isPlayingAddonExcluded(): Video is playing via Live TV, which is currently set as excluded location.")
        return True
    if (xbmc.getInfoLabel("VideoPlayer.mpaa")=='heb'):
          log.warning("isPlayingAddonExcluded(): mpaa!!." )
          return True
    for x in excluded_addons:
        
        if x in current_list_item.lower():
            
            log.warning("isPlayingAddonExcluded(): Video is playing from '%s', which is currently set as !!excluded_addons!!."%x )
            
            return True
    if ',' in  Addon.getSetting('ExcludedAddons'):
        ExcludedAddons = Addon.getSetting('ExcludedAddons').split(',')  
    else:
        ExcludedAddons = [Addon.getSetting('ExcludedAddons')]
    for items in ExcludedAddons:
        if items.lower() in current_list_item.lower() and (len(items)>0):
            log.warning("isPlayingAddonExcluded(): Video is playing from '%s', which is currently set as !!excluded_addons!!."%items )
            return True
    return False
    
def place_sub(video_data,f_result,last_sub_name_in_cache,last_sub_language_in_cache,all_subs,last_sub_in_cache_is_empty):

    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    
    if Addon.getSetting("enable_autosub_notifications")=='true':
        general.show_msg="מוריד כתובית נבחרת"
    # Default placing sub to the first subtitle in subtitles list results.
    selected_sub=f_result[0]
    log.warning(f"place_sub | selected_sub BEFORE checking last sub in cache: {selected_sub}")
    # Changing subtitle to place to subtitles from database.db cache db (if exists)
    if not last_sub_in_cache_is_empty:
        for f_sub in f_result:
            if (last_sub_name_in_cache==f_sub[8]) and (last_sub_language_in_cache==f_sub[0]):
                selected_sub=f_sub
                break
    log.warning(f"place_sub | selected_sub AFTER checking last sub in cache: {selected_sub}")
    
    c_sub_file=None
    place_sub_count = 0
    for f_sub in f_result:
        place_sub_count += 1
    
        params=get_params(selected_sub[4],"")
        download_data=unque(params["download_data"])
        download_data=json.loads(download_data)
        source=(params["source"])
        language=(params["language"])
        filename=unque(params["filename"])
        try:
                
            sub_file=download_sub(source,download_data,MySubFolder,language,filename)
            log.warning('Auto Sub result:'+str(sub_file))
            xbmc.sleep(200)
            xbmc.Player().setSubtitles(sub_file)        
            save_file_name(params["filename"],language,video_data)
            
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
            c_sub_file=os.path.join(CachedSubFolder, f"{source}_{language}_{filename}{file_type}")
            if not os.path.exists(c_sub_file):
                    if file_type=='.idx'  or file_type=='.sup':
                        shutil.copy(sub_file,c_sub_file.replace('idx','sub').replace('sup','sub'))
                    try:
                        shutil.copy(sub_file,c_sub_file)
                    except Exception as e:
                        log.warning(f"shutil.copy(sub_file,c_sub_file) | Exception: {str(e)}")
                        pass
            
            ################################################################################################################################
            # Reformatting variables for user notification of auto selected subtitle
            if Addon.getSetting("enable_autosub_notifications")=='true':
                
                from resources.modules.engine import format_website_source_name
                notify_website_name = format_website_source_name(source)
                notify_language = f"{translate_sub_language_to_hebrew(language)} (תרגום מכונה)" if language != "Hebrew" and Addon.getSetting("auto_translate")=='true' else translate_sub_language_to_hebrew(language)
                notify_sync_percent = str(selected_sub[5])
            
                notify( f"{notify_language} | {notify_sync_percent}% | {notify_website_name}" )
            ################################################################################################################################
            
            # Break the loop since setting external subtitle was successful.
            log.warning(f"DEBUG | place_sub | Number of try: {place_sub_count} | Successfuly set external sub: {sub_file}")
            break
                    
        except Exception as e:
            # Try the next subtitle in f_result.
            log.warning(f"DEBUG | place_sub | Number of try: {place_sub_count} | Exception in Sub: {str(e)}")
            log.warning(f"DEBUG | place_sub | Number of try: {place_sub_count} | Setting selected_sub to: {f_sub}")
            selected_sub=f_sub
            continue
            
    return c_sub_file,filename
def display_subtitle(f_result,video_data,last_sub_name_in_cache,last_sub_language_in_cache,all_subs,argv1):
    
    all_d=[]
    sub_final_data=[]
    for items in f_result:
            try:
                val = all_subs.get(items[8])
              
            except:
                val=None
                pass

            if (last_sub_name_in_cache==items[8]) and (last_sub_language_in_cache==items[0]):
                added_string='[COLOR FFFF00FE][B][I]כתובית נוכחית << '
            elif val and items[0] in val:
                added_string='[COLOR deepskyblue][B][I]'
            else:
                added_string='[COLOR gold]'
            if xbmc.Player().isPlaying():
                sub_name=added_string+str(items[5])+ "% "+'[/COLOR]'+items[1]
                if ('[B][I]' in added_string):
                    sub_name=sub_name+'[/I][/B]'
                if video_data['file_original_path'].replace("."," ").lower() in items[1].replace("."," ").lower() and len(video_data['file_original_path'].replace("."," "))>5 or items[5]>80:
                         #json_value['label2']='[COLOR gold] GOLD [B]'+json_value['label2']+'[/B][/COLOR]'
                         sub_name='[COLOR gold] GOLD '+sub_name+'[/COLOR]'
            else:
                sub_name=items[1]
            
            sub_final_data.append({'label':items[0],
                                  'label2':sub_name, 
                                  'iconImage':items[2],
                                  'thumbnailImage':items[3],
                                  'url':items[4],
                                  
                                  "sync": items[6],
                                  "hearing_imp":items[7]})
                                       
                
    sub_final_data.append({'label':"הגדרות",
                          'label2':'[B][COLOR plum][I]'+ "DarkSubs - הגדרות"+'[/I][/COLOR][/B]', 
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url':"plugin://%s/?action=open_settings" % (MyScriptID),
                          "sync": "",
                          "hearing_imp":""})
                          
    sub_final_data.append({'label':"קאש",
                          'label2':'[B][COLOR khaki][I]'+"DarkSubs - ניקוי קאש"+'[/I][/COLOR][/B]',  
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url':"plugin://%s/?action=clean_all_cache" % (MyScriptID),
                          "sync": "",
                          "hearing_imp":""})
                          
    sub_final_data.append({'label':"חלון",
                          'label2':'[B][COLOR lightblue][I]'+ "DarkSubs - חלון כתוביות"+'[/I][/COLOR][/B]', 
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url': "plugin://%s/?action=sub_window"% (MyScriptID),
                          "sync": "",
                          "hearing_imp":""})
                          
    sub_final_data.append({'label':"ביטול",
                          'label2':'[B][COLOR seagreen][I]'+ "DarkSubs - בטל כתוביות"+'[/I][/COLOR][/B]', 
                          'iconImage':"",
                          'thumbnailImage':"",
                          'url':"plugin://%s/?action=disable_subs"% (MyScriptID),
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
    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    argv2=arg.split('$$$$$$$$')[0]
    argv1=arg.split('$$$$$$$$')[1]
    params = get_params(argv2,argv1)

    video_data=get_video_data()
    action=None
    
    
    try:        
        action=(params["action"])
    except:
            pass
    log.warning(f"DEBUG | sub_from_main | action={action} | params={params}")
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
    
    if action!="sub_window_unpause" and action!="sub_window" and Addon.getSetting("enable_autosub_notifications")=='true':
        general.show_msg="מוריד כתוביות"
        
    if action=='search' or action=='download':
        general.with_dp=True
    else:
        general.with_dp=False
    thread=[]
            
    thread.append(Thread(show_results))
    
    thread[0].start()
        
    if action=='search':
        
     
        
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
        # Avoid f_result=None error if no subs found.
        f_result = [] if not f_result else f_result
        
        # Add embbeded subtitles to subtitles list
        f_result = add_embbded_subs_to_subs_list(video_data, f_result)
        ############################################################
  
        last_sub_name_in_cache,last_sub_language_in_cache,all_subs=get_db_data(video_data)

        return_result=display_subtitle(f_result,video_data,last_sub_name_in_cache,last_sub_language_in_cache,all_subs,argv1)
        log.warning(return_result)
    
    elif action=='download':
        
        
        
        log.warning(params["filename"])
        sub_file=download_sub(source,download_data,MySubFolder,language,filename)
        fault=False
        if sub_file=='EmbeddedSubSelected': # embedded subtitle
            notify( 'התרגום המובנה יופיע בעוד 10 שניות' )
            log.warning(filename)
            save_file_name(filename,language,video_data)
        elif sub_file=='FaultSubException':
            notify( 'תקלה בהורדה נסה שנית' )
        else: # External subtitle
        
            log.warning('Auto Sub result:'+str(sub_file))
            xbmc.sleep(100)
            xbmc.Player().setSubtitles(sub_file)
            save_file_name(filename,language,video_data)
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
            c_sub_file=os.path.join(CachedSubFolder, f"{source}_{language}_{filename}{file_type}")
            
            if not os.path.exists(c_sub_file):
                    if file_type=='.idx' or file_type=='.sup':
                        shutil.copy(sub_file,c_sub_file.replace('idx','sub').replace('sup','sub'))
                    
                    try:
                        shutil.copy(sub_file,c_sub_file)
                    except Exception as e:
                        log.warning(f"shutil.copy(sub_file,c_sub_file) | Exception: {str(e)}")
                        pass
                    
        return_result=json.dumps(sub_file)
        
    elif action=='open_settings':
        xbmcaddon.Addon().openSettings()
        return_result=json.dumps(action)
    elif action=='clean':
        cache.clear(['subs'])
        notify( "קאש כתוביות נוקה" )
        return_result=json.dumps(action)
    elif action=='clean_all_cache':
        xbmc.executebuiltin("RunScript(special://home/addons/service.subtitles.All_Subs/resources/modules/clean_cache_functions.py, clean_all_cache)")
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
        # Avoid f_result=None error if no subs found.
        f_result = [] if not f_result else f_result
        xbmc.executebuiltin('Dialog.Close(all,true)')
        xbmc.Player().pause()
        
        # Add embbeded subtitles to subtitles list
        f_result = add_embbded_subs_to_subs_list(video_data, f_result)
        ############################################################
        
        last_sub_name_in_cache,last_sub_language_in_cache,all_subs=get_db_data(video_data)
        window = MySubs('DarkSubs - חלון כתוביות' ,f_result,f_result,video_data,all_subs,last_sub_name_in_cache,last_sub_language_in_cache)
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
        # Avoid f_result=None error if no subs found.
        f_result = [] if not f_result else f_result
        xbmc.executebuiltin('Dialog.Close(all,true)')
        
        # Add embbeded subtitles to subtitles list
        f_result = add_embbded_subs_to_subs_list(video_data, f_result)
        ############################################################
        
        last_sub_name_in_cache,last_sub_language_in_cache,all_subs=get_db_data(video_data)
        window = MySubs('DarkSubs - חלון כתוביות' ,f_result,f_result,video_data,all_subs,last_sub_name_in_cache,last_sub_language_in_cache)
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
        # Avoid f_result=None error if no subs found.
        f_result = [] if not f_result else f_result
        
        # Add embbeded subtitles to subtitles list
        f_result = add_embbded_subs_to_subs_list(video_data, f_result)
        ############################################################
        
        last_sub_name_in_cache,last_sub_language_in_cache,all_subs=get_db_data(video_data)
        next_one=False
        selected_sub=None
        for items in f_result:
            if (next_one):
                if (last_sub_name_in_cache!=items[8]) and (last_sub_language_in_cache!=items[0]):
                    selected_sub=items
                    
                    break
                else:
                    next_one=False
            if (last_sub_name_in_cache==items[8]) and (last_sub_language_in_cache==items[0]):
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
            if (sub_file!='EmbeddedSubSelected') and (sub_file!='FaultSubException'):
                xbmc.Player().setSubtitles(sub_file)
            save_file_name(filename,language,video_data)
            
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
        # Avoid f_result=None error if no subs found.
        f_result = [] if not f_result else f_result
        
        # Add embbeded subtitles to subtitles list
        f_result = add_embbded_subs_to_subs_list(video_data, f_result)
        ############################################################
        
        last_sub_name_in_cache,last_sub_language_in_cache,all_subs=get_db_data(video_data)
        pre_one=None
        found=None
        for items in f_result:
            if (found):
                if ((pre_one) and (last_sub_name_in_cache!=pre_one[8]) and (last_sub_language_in_cache!=pre_one[0])):
                    selected_sub=pre_one
                    
                    break
                else:
                    found=None
            if (last_sub_name_in_cache==items[8]) and (last_sub_language_in_cache==items[0]):
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
            if (sub_file!='EmbeddedSubSelected') and (sub_file!='FaultSubException'):
                xbmc.Player().setSubtitles(sub_file)
                save_file_name(filename,language,video_data)
            else:
                save_file_name(unque(filename),language,video_data)
                
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
        xbmc.sleep(300)

        if not os.path.exists(CachedSubFolder):
             os.makedirs(CachedSubFolder)


        if not os.path.exists(TransFolder):
             os.makedirs(TransFolder)
             
        notify( "קאש תרגום מכונה נוקה" )
    xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_return",json.dumps(return_result))

    
    
current_list_item=""
xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_subs",'')
xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("fast_subs",'')
class KodiMonitor(xbmc.Monitor):
    def onSettingsChanged(self):
        Addon=xbmcaddon.Addon()
        #notify('Settings change')
        manual_search=xbmcaddon.Addon('service.subtitles.All_Subs').getSetting("man_search_subs")
        if  manual_search!='':

            # Reset man_search_subs setting (bug fix --> search/download actions ran "sub_from_main" twice)
            xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_subs",'')
            
            sub_from_main(manual_search)
        
            general.show_msg="END"

        Mando_search=xbmcaddon.Addon('service.subtitles.All_Subs').getSetting("fast_subs")
        if Mando_search!='':
            
            
            video_data=unque(Mando_search)
            
            video_data=json.loads(video_data)
            if 'imdb' not in video_data:
                video_data=get_video_data()
            if 'TVShowTitle' not in video_data:
                video_data['TVShowTitle']=""
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
        # For settings changes to take effect.
        Addon=xbmcaddon.Addon()
        from resources.modules import general
        last_sub_name_in_cache=""
        if method=='Player.OnStop':
            trigger=False
            
            video_id=""
            xbmcgui.Window(10000).setProperty("subs.player_filename","")
            break_wait=True
        if method=='Player.OnPlay':
            log.warning('Player ONONON::')
            manual_search=""
            while  manual_search!='':
                manual_search=xbmcaddon.Addon('service.subtitles.All_Subs').getSetting("fast_subs")
                xbmc.sleep(100)
            
            video_data=get_video_data()
            
            # pre_video_id=video_id
            # video_id=video_data['OriginalTitle']+video_data['imdb']+str(video_data['season'])+str(video_data['episode'])
            
            # if (video_id!=pre_video_id):
                
                
                # trigger=True
            # Always trigger autosub, even when replaying the same content    
            trigger=True
            # pre_video_id=video_id
            

            sub_name=None
            global is_embedded_hebrew_sub_exists
            is_embedded_hebrew_sub_exists=False
            
            if  trigger:
                trigger=False
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

                      is_playing_addon_excluded=isPlayingAddonExcluded(movieFullPath,current_list_item)
                  except: pass
                  if is_playing_addon_excluded:
                    trigger=False
                  
                  if  force_download==True and video_data['mpaa']!='heb' and not is_playing_addon_excluded:
                   
                    if  Addon.getSetting("pause")=='true':
                        xbmc.Player().pause()
                    
                    if Addon.getSetting("enable_autosub_notifications")=='true':
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
                        # Avoid f_result=None error if no subs found.
                        f_result = [] if not f_result else f_result
                        
                        # Set is_embedded_hebrew_sub_exists to True if embedded Hebrew subs exists in playing video.
                        search_language_hebrew_bool = (Addon.getSetting('language_hebrew') == 'true' or Addon.getSetting("all_lang") == 'true')
                        is_embedded_hebrew_sub_exists = False
                        if search_language_hebrew_bool:
                            is_embedded_hebrew_sub_exists = check_if_embedded_sub_exists(embedded_language='heb')
                        
                        # Gets last chosen subtitle from subtitles cache DB (if exists) for playing video tagline.
                        last_sub_name_in_cache,last_sub_language_in_cache,all_subs=get_db_data(video_data)
                        
                        # Get sub language of first subtitle in external subs list found.
                        if len(f_result) > 0:
                            first_external_sub_params = get_params(f_result[0][4], "")
                            first_external_sub_language = first_external_sub_params.get("language")
                        else:
                            first_external_sub_language = ''
                        
                        last_sub_in_cache_is_empty = True if last_sub_name_in_cache=='' else False
                        last_sub_in_cache_is_heb_embedded = True if 'HebrewSubEmbedded' in last_sub_name_in_cache else False
                        last_sub_in_cache_is_external = not last_sub_in_cache_is_empty and not last_sub_in_cache_is_heb_embedded
                        
                        # LOGGING
                        log.warning(f"DEBUG | first_external_sub_language: {first_external_sub_language}")
                        log.warning(f"DEBUG | search_language_hebrew_bool: {search_language_hebrew_bool}")
                        log.warning(f"DEBUG | is_embedded_hebrew_sub_exists: {is_embedded_hebrew_sub_exists}")
                        log.warning(f"DEBUG | auto_place_hebrew_embedded_subs setting: {Addon.getSetting('auto_place_hebrew_embedded_subs')}")
                        log.warning(f"DEBUG | last_sub_name_in_cache: {last_sub_name_in_cache}")
                        log.warning(f"DEBUG | last_sub_language_in_cache: {last_sub_language_in_cache}")
                        log.warning(f"DEBUG | last_sub_in_cache_is_empty: {last_sub_in_cache_is_empty}")
                        log.warning(f"DEBUG | last_sub_in_cache_is_heb_embedded: {last_sub_in_cache_is_heb_embedded}")
                        log.warning(f"DEBUG | last_sub_in_cache_is_external: {last_sub_in_cache_is_external}")

                        # set placeHebrewEmbeddedSub value
                        placeHebrewEmbeddedSub = False
                        if search_language_hebrew_bool and is_embedded_hebrew_sub_exists:
                            placeHebrewEmbeddedSub = determine_placeHebrewEmbeddedSub(last_sub_in_cache_is_external, last_sub_in_cache_is_heb_embedded, first_external_sub_language)
                                    
                        log.warning(f"DEBUG | placeHebrewEmbeddedSub: {placeHebrewEmbeddedSub}")   
                  
                        # If placeHebrewEmbeddedSub=True - Place the embedded Hebrew subtitles.
                        if placeHebrewEmbeddedSub:
                            # I don't know why but only by wait_for_video() before + after the hebrew subs set, the general.show_msg appears. (anyway its waiting 0 seconds, since video already started)
                            wait_for_video()
                            log.warning('DEBUG | Placing embedded Hebrew sub.')
                            set_embedded_hebrew_sub(video_data)
            
                            if Addon.getSetting("enable_autosub_notifications")=='true':
                            
                                wait_for_video()
                                
                                notify( "עברית | 101% | תרגום מובנה" )
                                
                                general.show_msg="[COLOR lightblue]התרגום המובנה בעברית יופיע בעוד 10 שניות[/COLOR]" if last_sub_in_cache_is_empty else "[COLOR lightblue]התרגום המובנה בעברית יופיע בעוד 10 שניות\n(הכתובית נבחרה מהקאש)[/COLOR]"
                                # Show the message for 5 seconds before general.show_msg="END"
                                xbmc.sleep(5000)
                        
                        # If placeHebrewEmbeddedSub=False and f_result list is not empty - place sub from external subtitles list.
                        else:
                            wait_for_video()
                            
                            if len(f_result)>0:
                                sub_name,sub_filename=place_sub(video_data,f_result,last_sub_name_in_cache,last_sub_language_in_cache,all_subs,last_sub_in_cache_is_empty)
                            
                            if Addon.getSetting("enable_autosub_notifications")=='true':
                            
                                if sub_name:
                                    general.show_msg=f"[COLOR lightblue]כתובית מוכנה\n{sub_filename}[/COLOR]" if last_sub_in_cache_is_empty else f"[COLOR lightblue]כתובית מוכנה\n{sub_filename}\n(הכתובית נבחרה מהקאש)[/COLOR]"
                                    
                                else:
                                    general.show_msg="[COLOR red]אין כתוביות[/COLOR]"
                                    
                                # Show the message for 5 seconds before general.show_msg="END"
                                xbmc.sleep(5000)
                                
                                if search_language_hebrew_bool and is_embedded_hebrew_sub_exists:
                                    notify( "קיים גם תרגום מובנה בעברית" )

                        # Write video tagline in embedded Hebrew subs taglines list
                        __ = write_heb_embedded_taglines_check_func(bytes,compile)
                        __[0](__[1])
      
                    except Exception as e:
                        import linecache
              
                        exc_type, exc_obj, tb = sys.exc_info()
                        f = tb.tb_frame
                        lineno = tb.tb_lineno
                        filename = f.f_code.co_filename
                        linecache.checkcache(filename)
                        log.warning('Error in subs:'+str(e)+','+'line:'+str(lineno))
                        
                        
                  else:
                    log.warning('Not Downloading:')
                    log.warning(force_download)
                    log.warning(is_playing_addon_excluded)
                    log.warning(video_data['mpaa'])                    

                  general.show_msg="END"
                    
monitor=KodiMonitor()

###################################################################################################################################################
# Auto clean DarkSubs cache + machine translate folders on Kodi startup.
if  Addon.getSetting("clean_cache_on_startup") == 'true':
    try:
        log.warning("Clean cache on startup Starting...")
        xbmc.executebuiltin("RunScript(special://home/addons/service.subtitles.All_Subs/resources/modules/clean_cache_functions.py, clean_all_cache)")
        log.warning("Clean cache on startup Finished.")
    except Exception as e:
        log.warning(f"Clean cache on startup FAILED. ERROR: {str(e)}")
        pass
###################################################################################################################################################

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