
from sys import argv
import xbmcplugin,xbmcgui,sys,xbmcaddon,os
from urllib.parse import parse_qsl
import xbmcvfs,json,shutil
xbmc_tranlate_path=xbmcvfs.translatePath
from resources.modules import cache
from resources.modules import log
import xbmc,socket
import urllib.parse
from urllib.parse import  unquote_plus, unquote,  quote
from resources.modules.engine import get_subtitles,download_sub
from resources.modules.general import get_video_data,get_db_data,notify,Thread,show_results
from resources.modules.general import MyScriptName,MyScriptID,save_file_name,CachedSubFolder
from resources.modules.sub_window import MySubs
unque=urllib.parse.unquote_plus
que=urllib.parse.quote_plus
user_dataDir = xbmc_tranlate_path(xbmcaddon.Addon().getAddonInfo("profile"))
if not os.path.exists(user_dataDir):
     os.makedirs(user_dataDir)
addonPath = xbmc_tranlate_path(xbmcaddon.Addon().getAddonInfo("path"))
MySubFolder = xbmc_tranlate_path(os.path.join(user_dataDir, 'Downloaded_subs'))
socket.setdefaulttimeout(10)

    

def get_params():
    try:
        param = dict(parse_qsl(argv[2].replace('?','')))
    except:
        log.warning(argv)
        param={}
        param['action']=argv[1]
    return param


                
def display_subtitle(f_result,video_data,last_sub_index,all_subs):
    all_d=[]

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
            try:
                  listitem = xbmcgui.ListItem(label          = items[0],
                                                label2         = sub_name,
                                                iconImage      = items[2],
                                               
                                                thumbnailImage = items[3]
                                                )
            except:
                listitem = xbmcgui.ListItem(label          = items[0],
                                                label2         = sub_name
                                                
                                                )
            listitem.setArt({'thumb' : items[3], 'icon': items[2]})
            listitem.setProperty( "sync", items[6] )
            listitem.setProperty( "hearing_imp",items[7] )
            all_d.append((items[4],listitem,False))
            #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=str(items['url']), listitem=listitem, isFolder=False)
    listitem = xbmcgui.ListItem(label="פתח הגדרות הרחבה",label2='[COLOR plum][I]'+ "פתח הגדרות הרחבה"+'[/I][/COLOR]')
    url = "plugin://%s/?action=open_settings" % (MyScriptID)
    all_d.append((url,listitem,True))
    
    listitem = xbmcgui.ListItem(label="ניקוי מטמון",label2='[COLOR khaki][I]'+"ניקוי מטמון DarkSubs"+'[/I][/COLOR]')
    url = "plugin://%s/?action=clean" % (MyScriptID)
    all_d.append((url,listitem,True))

    listitem = xbmcgui.ListItem(label="בטל כתוביות",label2='[COLOR seagreen][I]'+ "בטל כתוביות"+'[/I][/COLOR]')
    url = "plugin://%s/?action=disable_subs"% (MyScriptID)
    all_d.append((url,listitem,True))
    
    listitem = xbmcgui.ListItem(label="פתח חלון כתוביות",label2='[COLOR lightblue][I]'+ "חלון כתוביות"+'[/I][/COLOR]')
    url = "plugin://%s/?action=sub_window"% (MyScriptID)
    all_d.append((url,listitem,True))
    
    
    return all_d
def convert_to_utf(file):
    try:
        with codecs.open(file, "r", "cp1255") as f:
            srt_data = f.read()

        with codecs.open(file, 'w', 'utf-8') as output:
            output.write(srt_data)
    except: pass
def get_params_single(url):

    param = dict(parse_qsl(url.replace('?','')))
    return param
if len(sys.argv) >= 2:   
    params = get_params()
    video_data=get_video_data()
    log.warning(params)
    action=None
    
    
    try:        
        action=(params["action"])
    except:
            pass
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
    log.warning('action:'+action)
    if action=='search':
        test_get=xbmcgui.Window(10000).getProperty('torrent_name')
        log.warning(test_get)
        from resources.modules import general
        general.with_dp=True
        general.show_msg="מחפש כתוביות"
        log.warning(general.show_msg)
        thread=[]
                    
        thread.append(Thread(show_results))

        thread[0].start()
    
        f_result=cache.get(get_subtitles,0,video_data,table='subs')
        if (f_result):
            last_sub_index,all_subs=get_db_data(f_result)
            all_d=display_subtitle(f_result,video_data,last_sub_index,all_subs)
        else:
            cache.clear(['subs'])
            general.show_msg="אין כתוביות"
            all_d=display_subtitle({},video_data,'',[])
            xbmc.sleep(800)
        general.show_msg="END"
        
        xbmc.sleep(100)
        xbmcplugin .addDirectoryItems(int(sys.argv[1]),all_d,len(all_d))
    elif action=='download':
        
        
        from resources.modules import general
        general.with_dp=True
        general.show_msg="מוריד"
        log.warning(general.show_msg)
        thread=[]
                    
        thread.append(Thread(show_results))

        thread[0].start()
        
        
        try:
            sub_file=download_sub(source,download_data,MySubFolder,language,filename)
            
            log.warning(sub_file)
            general.show_msg="END"
            if not general.break_all:
                listitem =  xbmcgui.ListItem(label=sub_file)
                
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sub_file, listitem=listitem,isFolder=False)
                save_file_name(filename)
                c_sub_file=os.path.join(CachedSubFolder,source+language+filename)
                if not os.path.exists(c_sub_file):
                    shutil.copy(sub_file,c_sub_file)
        except Exception as e:
            xbmcgui.Dialog().ok('שגיאה','תקלה בהורדה \n'+str(e))
    elif action=='open_settings':
        xbmcaddon.Addon().openSettings()
    elif action=='clean':
        cache.clear(['subs'])
        notify( "המטמון נוקה" )
    elif action=='disable_subs':
        xbmc.Player().setSubtitles("")
        listitem = xbmcgui.ListItem(label="a")
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url="ww", listitem=listitem,isFolder=False)
        notify("כתוביות בוטלו")
    elif action=='sub_window':
        f_result=cache.get(get_subtitles,24,video_data,table='subs')
        xbmc.executebuiltin('Dialog.Close(all,true)')
        xbmc.Player().pause()
        last_sub_index,all_subs=get_db_data(f_result)
        
        window = MySubs('DarkSubs - חלון כתוביות' ,f_result,f_result,video_data,all_subs,last_sub_index)
    elif action=='sub_window_unpause':
        f_result=cache.get(get_subtitles,24,video_data,table='subs')
        xbmc.executebuiltin('Dialog.Close(all,true)')
        
        last_sub_index,all_subs=get_db_data(f_result)
        
        window = MySubs('DarkSubs - חלון כתוביות' ,f_result,f_result,video_data,all_subs,last_sub_index)
    elif action=='next':
        from resources.modules import general
        general.with_dp=False
        general.show_msg="כתובית הבאה"
        log.warning(general.show_msg)
        thread=[]
                    
        thread.append(Thread(show_results))

        thread[0].start()
    
        f_result=cache.get(get_subtitles,24,video_data,table='subs')

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
            params=get_params_single(selected_sub[4])
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
    elif action=='previous':
        from resources.modules import general
        general.with_dp=False
        general.show_msg="כתובית קודמת"
        
        thread=[]
                    
        thread.append(Thread(show_results))

        thread[0].start()
    
        f_result=cache.get(get_subtitles,24,video_data,table='subs')

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
            params=get_params_single(selected_sub[4])
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
        
    try:
        xbmc.sleep(100)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing =True,cacheToDisc =True)
        
    except:
        pass
    