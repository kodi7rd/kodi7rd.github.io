import xbmc,xbmcgui,time,xbmcplugin
from resources.modules import log
import pkgutil,json
import os,sys,shutil
import xbmcvfs,xbmcaddon
xbmc_tranlate_path=xbmcvfs.translatePath
from urllib.parse import  unquote_plus, unquote,  quote
import threading
import urllib.parse
import chardet
global break_all

from resources.modules.general import Thread,CachedSubFolder,TransFolder,user_dataDir
from resources.modules import cache


iconx=xbmcaddon.Addon().getAddonInfo('icon')
MyScriptID = xbmcaddon.Addon().getAddonInfo('id')
#import requests
break_all=False


from resources.sources import bsplayer
from resources.sources import ktuvit
from resources.sources import opensubtitles
from resources.sources import subscene
from resources.sources import wizdom

que=urllib.parse.quote_plus
Addon=xbmcaddon.Addon()
addonPath = xbmc_tranlate_path(Addon.getAddonInfo("path"))

def similar(w1, w2):
    from difflib import SequenceMatcher
    
    s = SequenceMatcher(None, w1, w2)
    return int(round(s.ratio()*100))

def sort_subtitles(save_all_data,video_data):
    highest_rating=0

    release_names=['bluray','hdtv','dvdrip','bdrip','web-dl','hdcam','hdrip','webrip']
    all_data=[]
    all_eng=[]
    Quality=(xbmc.getInfoLabel("VideoPlayer.VideoResolution"))+'p'
    for save_data_value in save_all_data:
          json_value=json.loads(json.dumps(save_data_value))
          
         
          
          if 'label' in json_value and 'label2' in json_value and 'iconImage' in json_value and 'thumbnailImage' in json_value and 'sync' in json_value and 'hearing_imp' in json_value:
           array_original=video_data['file_original_path'].strip().replace("_",".").replace(" ",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")
           array_original=[line.strip().lower() for line in array_original]
           array_subs=json_value['label2'].replace(json_value['site_id'],'').strip().replace("_",".").replace(" ",".").split(".")
          
           #array_subs.pop(0)
           array_subs=[line.strip().lower() for line in array_subs]
           array_subs=[str(x).lower() for x in array_subs if x != '']
           array_subs_original=array_subs

           array_original=[str(x).lower() for x in array_original if x != '']
           if Quality not in array_original and Quality in array_subs:
             array_original.append(Quality)

           for item_2 in release_names:
            if item_2 in array_original and item_2 in array_subs:
              array_original.append(item_2)
              array_original.append(item_2)
              array_original.append(item_2)
              array_subs.append(item_2)
              array_subs.append(item_2)
              array_subs.append(item_2)
           
           precent=similar(array_original,array_subs)

           #if precent==0:
           
           array_original=video_data['Tagline'].strip().replace("_",".").replace(" ",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")
           

           #array_subs.pop(0)
           
           if Quality not in array_original and Quality in array_subs:
               array_original.append(Quality)
           array_subs=[str(x).lower() for x in array_subs if x != '']
           array_original=[str(x).lower() for x in array_original if x != '']

           for item_2 in release_names:
            if item_2 in array_original and item_2 in array_subs:
              array_original.append(item_2)
              array_original.append(item_2)
              array_original.append(item_2)
              array_subs.append(item_2)
              array_subs.append(item_2)
              array_subs.append(item_2)
           
           
           precent2=similar(array_original,array_subs)

           if precent2>precent:
              precent=precent2
    
           #if 'language=English' in json_value['url'] or 'language=Arabic' in json_value['url'] or 'language=Spanish' in json_value['url']:
           
           if 'language=Hebrew' not in json_value['url'] and 'language=he' not in json_value['url'] and ('language=' in  json_value['url'] or 'Hebrew' not in json_value['label']):
               
               all_eng.append((json_value['label'],'[COLOR %s]'%json_value['sub_color']+json_value['label2']+'[/COLOR]',json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],precent,json_value['sync'],json_value['hearing_imp'],json_value['filename']))
           else:

             all_data.append((json_value['label'],'[COLOR %s]'%json_value['sub_color']+json_value['label2']+'[/COLOR]',json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],precent,json_value['sync'],json_value['hearing_imp'],json_value['filename']))
      
    
    all_data=sorted(all_data, key=lambda x: x[5], reverse=True)
    all_eng=sorted(all_eng, key=lambda x: x[5], reverse=True)
    
    all_data=all_data+all_eng
    log.warning(all_data)
    return all_data
def c_get_subtitles(video_data):
    from resources.modules import general
    log.warning('Searching for:')
    log.warning(video_data)
    source_dir = os.path.join(addonPath, 'resources', 'sources')
    thread=[]
    all_sources=[]
    bsplayer.global_var=[]
    ktuvit.global_var=[]
    opensubtitles.global_var=[]
    subscene.global_var=[]
    wizdom.global_var=[]
    
    if Addon.getSetting('bsplayer')=='true':
        
        thread.append(Thread(bsplayer.get_subs,video_data))
        all_sources.append(('bsplayer',bsplayer))
        
    if Addon.getSetting('ktuvit')=='true':
        
        thread.append(Thread(ktuvit.get_subs,video_data))
        all_sources.append(('ktuvit',ktuvit))
        
    if Addon.getSetting('opensubtitles')=='true':
        
        thread.append(Thread(opensubtitles.get_subs,video_data))
        all_sources.append(('opensubtitles',opensubtitles))
        
    if Addon.getSetting('subscene')=='true':
        
        thread.append(Thread(subscene.get_subs,video_data))
        all_sources.append(('subscene',subscene))
        
    if Addon.getSetting('wizdom')=='true':
        
        thread.append(Thread(wizdom.get_subs,video_data))
        all_sources.append(('wizdom',wizdom))
        
    
            
            
            
    for td in thread:
      td.start()
      
    

    tt={}
    for i in range (0,40): 
      tt[i]="red"
    start_time = time.time()
    #while 1:
    num_live=0
    break_all=False
    ExcludeTime = int((Addon.getSetting('time_s')))
    
    while 1:
        elapsed_time = time.time() - start_time
        still_alive=0
        for threads in thread:
              
              if break_all:
                 
                 break
                                
              num_live=0
              string_dp=''

              still_alive=0
              for yy in range(0,len(thread)):
                if not thread[yy].is_alive():
                  num_live=num_live+1
                  tt[yy]="lightgreen"
                else:
                  still_alive=1
                  tt[yy]="red"
              
             
              
              zz=0
              f_result=[]
              for scraper,items in all_sources:
                 f_result=f_result+items.global_var
                 string_dp=string_dp+(' %s:[COLOR %s]%s[/COLOR] '%(scraper[:3].capitalize(),tt[zz],len( items.global_var)))
                 zz=zz+1
              general.show_msg=' אנא המתן '+ time.strftime("%H:%M:%S", time.gmtime(elapsed_time))+'\n'+ string_dp
              
        if still_alive==0:
            break
        
        
        if  elapsed_time>ExcludeTime: 
               
            for threads in thread:
                 if threads.is_alive():
                     break_all=True
                     threads.exit()
            break
        xbmc.sleep(10)
    
    
    general.show_msg="מסדר כתוביות"
    
    
    return f_result
def get_subtitles(video_data):
    from resources.modules import general
   
    
    
    
    general.show_msg='מחפש כתוביות'
    
    f_result=c_get_subtitles(video_data)
    
    
    xbmc.sleep(100)
    
    return f_result



  
def translate_subs(input_file,output_file):
    
    
    
    from resources.modules import general
    
    g_show_msg=general.show_msg
    progress_msg=general.progress_msg
    sourcelang='eng'
    general.show_msg='אנא המתן'+'\n'+'מתרגם'
    log.warning('אנא המתן'+'\n'+'מתרגם')
    url = 'https://www.googleapis.com/language/translate/v2?key={0}&q={1}&source={2}&target={3}'
    targetlang='he'
    api_key='AIzaSyCk5TfD_K1tU1AB2salwn2Lb_yZbesSmY8'
    import chardet

    # Open the file as binary data
    with open(input_file, 'rb') as f:
        # Join binary lines for specified number of lines
        rawdata = f.read()

    encoding=chardet.detect(rawdata)['encoding']
    log.warning('encoding:'+encoding)
    
   
    text=rawdata
    
    
    if encoding=='ISO-8859-7':
      text=text.decode('cp1253','ignore')
    elif encoding=='MacCyrillic':
      text=text.decode('cp1256','ignore')
    else:
      text=text.decode(encoding,'ignore')
      
    
    
    #from resources.modules.n_trans.t import translate_all
    
    #f_sub_pre=translate_all(text)
    #a+=1
    path=xbmc_tranlate_path('special://home/addons/%s/resources/modules/auto_translate'%MyScriptID)
    sys.path.append( path)
    Addon = xbmcaddon.Addon()
    all_text_p1=[]
    all_data=''
 
    counter=0
    
    if Addon.getSetting("translate_p")== '0':
        
        from resources.modules.auto_translate.googletrans import Translator  
        
        
        translator = Translator()  

       
        split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
       
        ax2=split_string(text,3000)
        f_sub_pre=''
        xx=0
        
        general.progress_msg=0
        for items in ax2:
             general.show_msg=' מתרגם ' + encoding+'\n'+str(int(((xx* 100.0)/(len(ax2))) ))+'%'
             general.progress_msg=int(((xx* 100.0)/(len(ax2))) )
             if general.break_all:
                 break
             
             translation=translator.translate(items, dest='he').text
             
             f_sub_pre=f_sub_pre+translation
             xx+=1
        f_sub_pre=f_sub_pre.replace('\r','\n')
        #all_text=f_sub_pre.replace(': ',':').replace('"# ','"#').split('\n')
    else:
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Alt-Used': 't19.freetranslations.org',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            # Requests doesn't support trailers
            # 'TE': 'trailers',
        }

        base_url='https://t23.freetranslations.org/freetranslationsorg.php?p1=auto&p2=he&p3='
        
        split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
        f_sub_pre=''
        xx=0
        
        general.progress_msg=0
        ax2=split_string(text,1000)
       
        for items in ax2:
            
             translation=requests.get(base_url+items,headers=headers).text

             general.show_msg=' מתרגם ' + encoding+'\n'+str(int(((xx* 100.0)/(len(ax2))) ))+'%'
             general.progress_msg=int(((xx* 100.0)/(len(ax2))) )
             if general.break_all:
                 break
             
             f_sub_pre=f_sub_pre+translation
             xx+=1
        f_sub_pre=f_sub_pre
    f_all=f_sub_pre.replace('\r\r','\n')
    
    source_dir = os.path.join(addonPath, 'resources', 'modules')
    sys.path.append(source_dir)
    if not general.break_all:
        with open(output_file, mode="w", encoding="utf8") as f:
                 f.write(f_all)
                 
    from resources.modules import pysrt
    try:
        subs = pysrt.open(output_file)
        
        first_sub = subs[0]
        log.warning('Subs Ok')
        
    except Exception as e:
        log.warning('Error in sub:'+str(e))
        f_all=f_sub_pre.replace('\r\r','\n').replace('\n\n','\n')
    
    all_ch=['?','.','!',',']
    all_l=[]
    
    for line in f_all.splitlines():
        for ch in all_ch:
            found=False
            if line.endswith(ch):
               
                line=ch+line[:-1]
                all_l.append(line)
                found=True
                break
        if not found:
            all_l.append(line)
    f_all='\n'.join(all_l)
    '''
    for line in all_text:
       if '[' and ']' not in line:
        f_all=f_all+rtl(line.encode('utf-8'))+'\n'
       else:
        f_all=f_all+line.replace('] [','][')+'\n'
    '''
    if not general.break_all:
        with open(output_file, mode="w", encoding="utf8") as f:
                 f.write(f_all)
  
    return f_all

def download_sub(source,download_data,MySubFolder,language,filename):
    log.warning('Download sub')
    ext=['.srt','.sub','.sup','.idx']
    Addon=xbmcaddon.Addon()
    try:
        shutil.rmtree(MySubFolder)
    except: pass
    xbmcvfs.mkdirs(MySubFolder)
    
    
    if not os.path.exists(MySubFolder):
        os.makedirs(MySubFolder)
        

    
    source_dir = os.path.join(addonPath, 'resources', 'sources')
    sys.path.append(source_dir)
    impmodule = __import__(source)
    max_sub_cache=int(Addon.getSetting("subtitle_trans_cache"))
    f_count=0
    for filename_o in os.listdir(CachedSubFolder):
        
        f_count+=1

    if (f_count>max_sub_cache):
            for filename_o in os.listdir(CachedSubFolder):
                f = os.path.join(CachedSubFolder, filename_o)
                os.remove(f) 
    c_sub_file=os.path.join(CachedSubFolder,source+language+filename)
    found=False
    for items in ext:
        log.warning(c_sub_file+items)
        if os.path.exists(c_sub_file+items):
            sub_file=c_sub_file+items
            found=True
            log.warning('Found cache')
            break
    if not found:
        sub_file=impmodule.download(download_data,MySubFolder)
        
    if language!='Hebrew'  and Addon.getSetting("auto_translate")=='true':
        
        f_count=0
        for filename_o in os.listdir(TransFolder):
            
            f_count+=1
        if (f_count>max_sub_cache):
            for filename_o in os.listdir(TransFolder):
                f = os.path.join(TransFolder, filename_o)
                os.remove(f)
        trans_file=os.path.join(TransFolder, language+filename)
        
        if not os.path.exists(trans_file):
            translate_subs(sub_file,trans_file)
        sub_file=trans_file
    
    
    return sub_file