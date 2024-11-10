# -*- coding: utf-8 -*-
import sys,xbmcgui,xbmc,xbmcplugin,xbmcaddon
import json
from resources.modules import log


def run_async_task(target):
    import threading
    task_thread = threading.Thread(target=target)
    task_thread.start()
    task_thread.join()


    


def start():
    if len(sys.argv) >= 2:
        ##### TELEGRAM ###########
        if sys.argv[1] == "login_to_telegram":
            from resources.sources.telegram import run_async_login_to_telegram
            run_async_task(run_async_login_to_telegram)
            return
        if sys.argv[1] == "logout_from_telegram":
            from resources.sources.telegram import run_async_logout_from_telegram
            run_async_task(run_async_logout_from_telegram)
            return
        if sys.argv[1] == "telegram_helper_window":
            from resources.sources.telegram import telegram_helper_window
            telegram_helper_window()
            return
        ##########################
        #Addon = xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("get_subs",'1')
    
        xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_return","")
        log.warning(sys.argv)
        try:
            sub_data=sys.argv[2]+'$$$$$$$$'+sys.argv[1]
        except:
            sub_data="None"+'$$$$$$$$'+sys.argv[1]
        #xbmcgui.Window(10000).setProperty("man_search_subs",str(sub_data))
        xbmcaddon.Addon('service.subtitles.All_Subs').setSetting("man_search_subs",sub_data)
        response=""
        timeout=0
        all_d=[]
        while response=="":
            response=xbmcaddon.Addon('service.subtitles.All_Subs').getSetting("man_search_return")
            
            
            xbmc.sleep(100)
            timeout+=1
            if timeout>400:#40 sec
                break
        log.warning(response)
        
        if timeout>400:
            sys.exit(1)
        response=json.loads(response)
        if "hearing_imp" in str(response) and 'thumbnailImage' in str(response):
            
            
            
            for items in response:
                listitem = xbmcgui.ListItem(label          = items['label'],
                                            label2         = items['label2'],
                                            
                                            )
                listitem.setArt({'thumb' : items['thumbnailImage'], 'icon': items['iconImage']})
                listitem.setProperty( "sync", items["sync"] )
                listitem.setProperty( "hearing_imp",items["hearing_imp"] )
                
                all_d.append((items['url'],listitem,False))
            
        else:
            response=response.replace('\\\\','\\')
            log.warning(response)
            listitem =  xbmcgui.ListItem(label=response)
            
            if response!='"clean"' and response!='"open_settings"' :
                xbmc.executebuiltin('Dialog.Close(all,true)')
            
            #sys.exit(1)
    try:
        xbmcplugin .addDirectoryItems(int(sys.argv[1]),all_d,len(all_d))
        xbmc.sleep(100)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing =True,cacheToDisc =True)
        log.warning('4')
    except:
        pass
    
            
            
