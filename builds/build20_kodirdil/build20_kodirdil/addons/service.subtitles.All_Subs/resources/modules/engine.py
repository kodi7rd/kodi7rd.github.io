
import random
import xbmc,xbmcgui,time,xbmcplugin
from resources.modules import log
import pkgutil,json,re
import os,sys,shutil
import xbmcvfs,xbmcaddon
xbmc_tranlate_path=xbmcvfs.translatePath
from urllib.parse import  unquote_plus, unquote,  quote
import threading
import urllib.parse
import chardet,unicodedata
global break_all
from urllib.parse import  unquote_plus, unquote, quote, quote_plus
from resources.modules.general import Thread,CachedSubFolder,TransFolder,user_dataDir
from resources.modules import cache
global trans_result
from concurrent import futures
trans_result=[]
iconx=xbmcaddon.Addon().getAddonInfo('icon')
MyScriptID = xbmcaddon.Addon().getAddonInfo('id')
#import requests
break_all=False


from resources.sources import bsplayer
from resources.sources import ktuvit
from resources.sources import opensubtitles
from resources.sources import subscene
from resources.sources import wizdom
global global_sub_size,global_progress
que=urllib.parse.quote_plus
unque=urllib.parse.unquote_plus
Addon=xbmcaddon.Addon()
addonPath = xbmc_tranlate_path(Addon.getAddonInfo("path"))
class Bing(object):
    def __init__(self):
        self.url = "http://api.microsofttranslator.com/v2/ajax.svc/TranslateArray2?"

    def translate(self, from_lan, to_lan,content,):
        data = {}
        #data['from'] = '"' + from_lan + '"'
        data['to'] = '"' + to_lan + '"'
        data['texts'] = '["'
        data['texts'] += content
        data['texts'] += '"]'
        data['options'] = "{}"
        data['oncomplete'] = 'onComplete_3'
        data['onerror'] = 'onError_3'
        data['_'] = '1430745999189'
        data = urllib.parse.urlencode(data).encode('utf-8')
        strUrl = self.url + data.decode() + "&appId=%22ABB1C5A823DC3B7B1D5F4BDB886ED308B50D1919%22"
        response = urllib.request.urlopen(strUrl)
        str_data = response.read().decode('utf-8')
        try:
            tmp, str_data = str_data.split('"TranslatedText":')
        except:
            print (str_data)
            return str_data
        translate_data = str_data[1:str_data.find('"', 1)]
        return translate_data
def similar(w1, w2):
    from difflib import SequenceMatcher
    
    s = SequenceMatcher(None, w1, w2)
    return int(round(s.ratio()*100))

def sort_subtitles(save_all_data,video_data):
    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    from resources.modules import general
    highest_rating=0
    if Addon.getSetting("enable_autosub_notifications")=='true' or not xbmc.Player().isPlaying():
        # If searching subtitles from context menu - will show the message.
        general.show_msg="מסדר כתוביות 0/"+str(len(save_all_data))
    release_names=['blueray','bluray','blu-ray','bdrip','brrip','brip',
                     'hdtv','hdtvrip','pdtv','tvrip','hdrip','hd-rip',
                     'web','web-dl','web dl','web-dlrip','webrip','web-rip',
                     'dvdr','dvd-r','dvd-rip','dvdrip','cam','hdcam','cam-rip','camrip','screener','dvdscr','dvd-full',
                     'telecine','hdts','telesync']
                     
    # Define the specific order for json_value['site_id']. In case of multiple subtitles with same precent - sort also by site_id using this order:
    site_id_order=['[Kt]', '[Wiz]', '[Ops]', '[SS]', '[Bs]']
    #########################################
    
    all_data=[]
    all_heb=[]
    all_eng=[]
    all_other_lang=[]
    Quality=(xbmc.getInfoLabel("VideoPlayer.VideoResolution"))+'p'
    count=0
    for save_data_value in save_all_data:
          if Addon.getSetting("enable_autosub_notifications")=='true' or not xbmc.Player().isPlaying():
            # If searching subtitles from context menu - will show the message.
            general.show_msg="מסדר כתוביות %d/%d"%(count,(len(save_all_data)))
          count+=1
          json_value=json.loads(json.dumps(save_data_value))
          
         
          
          if 'label' in json_value and 'label2' in json_value and 'iconImage' in json_value and 'thumbnailImage' in json_value and 'sync' in json_value and 'hearing_imp' in json_value:
          
           # Video file array
           array_original=video_data['file_original_path'].strip().replace("_",".").replace(" ",".").replace("+",".").replace("/",".").replace("-",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")
           array_original=[x.strip().lower() for x in array_original if x != '']
           
           # Subtitle name array
           array_subs=json_value['label2'].replace(json_value['site_id'],'').strip().replace(".srt",'').replace("_",".").replace(" ",".").replace("+",".").replace("/",".").replace("-",".").split(".")
           array_subs=[x.strip().lower() for x in array_subs if x != '']
           
           # Original subtitle name array
           array_subs_original=array_subs

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
           
           if ('תרגום מובנה' in json_value['label2']):
               precent=101
           else:
                precent=similar(array_original,array_subs)
           
           # Video Tagline array
           array_original=video_data['Tagline'].strip().replace("_",".").replace(" ",".").replace("+",".").replace("/",".").replace("-",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")
           array_original=[x.strip().lower() for x in array_original if x != '']
           
           # Original subtitle name array
           array_subs=array_subs_original
           
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
           
           
           precent2=similar(array_original,array_subs)

           if precent2>precent:
              precent=precent2
           
           if 'language=Hebrew' in json_value['url'] or 'Hebrew' in json_value['label']:
               all_heb.append((json_value['label'],'[COLOR %s]'%json_value['sub_color']+json_value['label2']+'[/COLOR]',json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],precent,json_value['sync'],json_value['hearing_imp'],json_value['filename'],json_value['site_id']))
           
           elif 'language=English' in json_value['url'] or 'English' in json_value['label']:
               all_eng.append((json_value['label'],'[COLOR %s]'%json_value['sub_color']+json_value['label2']+'[/COLOR]',json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],precent,json_value['sync'],json_value['hearing_imp'],json_value['filename'],json_value['site_id']))
               
           else:
               all_other_lang.append((json_value['label'],'[COLOR %s]'%json_value['sub_color']+json_value['label2']+'[/COLOR]',json_value['iconImage'],json_value['thumbnailImage'],json_value['url'],precent,json_value['sync'],json_value['hearing_imp'],json_value['filename'],json_value['site_id']))
      
    
    # Sort by precent (index 5) and then by site_id (index 9) using custom order specified in site_id_order.
    all_heb=sorted(all_heb, key=lambda x: (-x[5], site_id_order.index(x[9]) if x[9] in site_id_order else len(site_id_order)))
    
    all_eng=sorted(all_eng, key=lambda x: (-x[5], site_id_order.index(x[9]) if x[9] in site_id_order else len(site_id_order)))
    
    # For all other languages - Sort also by language, then by precent (index 5) and then by site_id (index 9) using custom order specified in site_id_order.
    all_other_lang=sorted(all_other_lang, key=lambda x: (x[0], -x[5], site_id_order.index(x[9]) if x[9] in site_id_order else len(site_id_order)))
    
    all_data=all_heb+all_eng+all_other_lang
 
    return all_data
def lowercase_with_underscores(_str):   ####### burekas
    return unicodedata.normalize('NFKD', _str).encode('utf-8','ignore').decode('utf-8')
    #return normalize('NFKD', (_str)).encode('utf-8', 'ignore')
    #return normalize('NFKD', str(str(str, 'utf-8'))).encode('utf-8', 'ignore')
def get_TMDB_data_filtered(url,filename,query,type):    ##### burekas
    myLogger=log.warning
    myLogger("searchTMDB: %s" % url)
    myLogger("query filtered: %s" % query)
    json = caching_json(filename,url)
    json_results = json["results"]
    myLogger("searchTMDB: json_results - " + repr(json_results))
    if type=='tv':
        json_results.sort(key = lambda x:x["name"]==query, reverse=True)
    else:
        json_results.sort(key = lambda x:x["title"]==query, reverse=True)
    myLogger("searchTMDB: json_results sorted - " + repr(json_results))

    return json_results      

def checkAndParseIfTitleIsTVshowEpisode(manualTitle): 

        manualTitle = manualTitle.replace("%20", " ")

        matchShow = re.search(r'(?i)^(.*?)\sS\d', manualTitle)
        if matchShow == None:
            return ["NotTVShowEpisode", "0", "0",'']
        else:
            tempShow = matchShow.group(1)
        
        matchSnum = re.search(r'(?i)%s(.*?)E' %(tempShow+" s"), manualTitle)
        if matchSnum == None:
            return ["NotTVShowEpisode", "0", "0",'']
        else:
            tempSnum = matchSnum.group(1)
        
        matchEnum = re.search(r'(?i)%s(.*?)$' %(tempShow+" s"+tempSnum+"e"), manualTitle)
        if matchEnum == None:
            return ["NotTVShowEpisode", "0", "0",'']
        else:
            tempEnum = matchEnum.group(1)

        return [tempShow, tempSnum, tempEnum, 'episode']


def searchForIMDBID(query,item):  ##### burekas 
    import requests                       
    from resources.modules import PTN
    myLogger=log.warning
    year=item["year"]
    info=(PTN.parse(query))
    tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'

    if item["tvshow"] and item['dbtype'] == 'episode':   
        type_search='tv'
            
        url="https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en&append_to_response=external_ids"%(type_search,tmdbKey,quote_plus(item['tvshow']))
        x=requests.get(url).json()
        try:
            tmdb_id = int(x['results'][0]["id"])
        except:
            myLogger( "[%s]" % (e,))
            return 0        

        
        url = "https://api.tmdb.org/3/%s/%s?api_key=%s&language=en&append_to_response=external_ids"%(type_search,tmdb_id,tmdbKey)
        x=requests.get(url).json()
        log.warning(url)
        log.warning(x)
        try:    imdb_id = x['external_ids']["imdb_id"]
        except Exception as e:    
            myLogger( "[%s]" % (e,))
            return 0        
        
        log.warning(imdb_id)
        return imdb_id
   
    elif info['title']: # and item['dbtype'] == 'movie':
        type_search='movie'
        filename = 'subs.search.tmdb.%s.%s.%s.json'%(type_search,lowercase_with_underscores(query),year)        
        if int(year) > 0:
            url = "https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=en"%(type_search,tmdbKey,quote(info['title']),year)
        else:
            url = "https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en"%(type_search,tmdbKey,quote(info['title']))

        #json_results = get_TMDB_data_popularity_and_votes_sorted(url,filename)
        json_results = get_TMDB_data_filtered(url,filename,item['title'],type_search)
        
        try:
            tmdb_id = int(json_results[0]["id"])
        except:
            myLogger( "[%s]" % (e,))
            return 0

        filename = 'subs.search.tmdb.fulldata.%s.%s.json'%(type_search,tmdb_id)
        url = "https://api.tmdb.org/3/%s/%s?api_key=%s&language=en&append_to_response=external_ids"%(type_search,tmdb_id,tmdbKey)
        myLogger("searchTMDB fulldata id: %s" % url)        
        json = caching_json(filename,url)
        
        try:    imdb_id = json['external_ids']["imdb_id"]
        except:
            myLogger( "[%s]" % (e,))
            return 0

        return imdb_id
def getIMDB(title):    
    

    item = {}
    item['tvshow'], item['season'], item['episode'], item['dbtype'] = checkAndParseIfTitleIsTVshowEpisode(title)
    

    if item['tvshow'] == 'NotTVShowEpisode':
        item['title'] = title
        item['tvshow'] = ''          
        _query = item['title'].rsplit(' ', 1)[0]    

        try:
            item['year'] = item['title'].rsplit(' ', 1)[1]
            item['title'] = _query            
            if item['year'].isdigit():
                if int(item['year']) > 1900:
                    item['imdb_id'] = searchForIMDBID(_query, item)               
                        
                else:
                    #item['year'] is not present a year
                    item['imdb_id'] = ''
            else:
                item['imdb_id'] = '' 
        except:  
            item['imdb_id'] = ''        

    else:  # TVShowEpisode
        item['year'] = '0000'
        _query = item['tvshow']    
        item['title'] = _query
        item['TVshowtitle']= _query
        item['OriginalTitle']= _query
        
        _season = item['season'].split("0")
        _episode = item['episode'].split("0")
        if _season[0] == '':
            item['season'] = _season[1].replace('.','')
        if _episode[0] == '':
            item['episode'] = _episode[1]

        item['imdb_id'] = searchForIMDBID(_query, item)                
        item['imdb']=item['imdb_id']
    try:
        if item['imdb_id']:        
            return item
        else:
            return 0

    except Exception as err:
        log.warning('Caught Exception: error in manual search: %s' % format(err))
        pass

# Prettify website source name for subs search dialog
def format_website_source_name(source):
    if source == "ktuvit":
        return "Ktuvit"
    elif source == "wizdom":
        return "Wizdom"
    elif source == "bsplayer":
        return "BSPlayer"
    elif source == "subscene":
        return "Subscene"
    elif source == "opensubtitles":
        return "OpenSubtitles"
    else:
        return source
        
def c_get_subtitles(video_data):
    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    from resources.modules import general
    log.warning('Searching for:')
    log.warning(video_data)
    if 'tt' not in video_data.get('imdb',''):
        video_data=getIMDB(video_data['title'])
        
    log.warning(video_data)
    source_dir = os.path.join(addonPath, 'resources', 'sources')
    thread=[]
    all_sources=[]
    bsplayer.global_var=[]
    ktuvit.global_var=[]
    opensubtitles.global_var=[]
    subscene.global_var=[]
    wizdom.global_var=[]
        
    if Addon.getSetting('ktuvit')=='true' and (Addon.getSetting('language_hebrew')=='true' or Addon.getSetting("all_lang")=='true'):
        
        thread.append(Thread(ktuvit.get_subs,video_data))
        all_sources.append(('ktuvit',ktuvit))
        
    if Addon.getSetting('wizdom')=='true' and (Addon.getSetting('language_hebrew')=='true' or Addon.getSetting("all_lang")=='true'):
        
        thread.append(Thread(wizdom.get_subs,video_data))
        all_sources.append(('wizdom',wizdom))
        
    if Addon.getSetting('opensubtitles')=='true':
        
        thread.append(Thread(opensubtitles.get_subs,video_data))
        all_sources.append(('opensubtitles',opensubtitles))
        
    if Addon.getSetting('subscene')=='true':
        
        thread.append(Thread(subscene.get_subs,video_data))
        all_sources.append(('subscene',subscene))
    
    if Addon.getSetting('bsplayer')=='true' and (Addon.getSetting('language_hebrew')=='true' or Addon.getSetting("all_lang")=='true'):
        
        thread.append(Thread(bsplayer.get_subs,video_data))
        all_sources.append(('bsplayer',bsplayer))
        
    
            
            
            
    for td in thread:
      xbmc.sleep(100)
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
                 string_dp=string_dp+(' %s:[COLOR %s]%s[/COLOR] '%(format_website_source_name(scraper),tt[zz],len( items.global_var)))
                 zz=zz+1
              if Addon.getSetting("enable_autosub_notifications")=='true' or not xbmc.Player().isPlaying():
                # If searching subtitles from context menu - will show the message.
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
    
    if Addon.getSetting("enable_autosub_notifications")=='true' or not xbmc.Player().isPlaying():
        # If searching subtitles from context menu - will show the message.
        general.show_msg="מסדר כתוביות"
    
    
    return f_result
def get_subtitles(video_data):
    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    from resources.modules import general
   
    
    
    if Addon.getSetting("enable_autosub_notifications")=='true' or not xbmc.Player().isPlaying():
        # If searching subtitles from context menu - will show the message.
        general.show_msg='מחפש כתוביות'
    
    f_result=c_get_subtitles(video_data)
    
    
    xbmc.sleep(100)
    
    
    
    return f_result


def get_random_number():
    import random
    result=22
    while (result == 20) or (result == 21) or (result == 22):
        result=int(random.random()*22+1)
    return result
def get_translated(base_url,items,counter,headers):
    import requests
    global trans_result
    translation='Error code'
    count_error=0
    while ('Error code' in translation or 'Resource Limit Is Reached' in translation or 'Access denied' in translation or 'onError_3' in translation):
        try:
            translation=requests.get(base_url+(items),headers=headers).text
        except:
            num=get_random_number()
            base_url='https://t%s.freetranslations.org/freetranslationsorg.php?p1=auto&p2=he&p3='%str(num)
            try:
                translation=requests.get(base_url+(items),headers=headers,timeout=2).text
            except:
                translation='Error code'
        if ('Error code' in translation or 'Resource Limit Is Reached' in translation or 'Access denied' in translation or 'onError_3' in translation):
            
            bing=Bing()
            log.warning('Error Found')
            
            x=bing.translate('en', 'he',que(items))
            translation=unque(x)
      
            if ('onError_3' in translation):
                time.sleep(1)
                count_error+=1
                if (count_error>5):
                    log.warning('Error 5')
                    break
                
    if ('Error code' in translation or 'Resource Limit Is Reached' in translation or 'Access denied' in translation):
        translation='Error now:'+str(count_error)
    trans_result.append((translation,counter))
def c_get_bing_keys():
    import requests
    
    x=requests.get('https://kodi7rd.github.io/repository/other/DarkSubs_Bing/darksubs_bing_api.json').json()
    return x
def get_last_key():
    try:
        last_key_file=os.path.join(user_dataDir,'last_bing_key.txt')
        file = open(last_key_file, 'r') 
        file_data= file.read()
        file.close()
    
        file_data=int(file_data)
    except:
        if Addon.getSetting("bing_translate_keys_method") == '1':
            x=c_get_bing_keys()
            file_data = random.randint(0, len(x) - 1) # Generate random number from 0 to keys count
        else:
            file_data=0
    return file_data
def set_last_key(count_key):
    try:
        last_key_file=os.path.join(user_dataDir,'last_bing_key.txt')
        file = open(last_key_file, 'w') 
        file.write(str(count_key))
        file.close()
    except:
        pass
    
def select_key(count_key):
    x=cache.get(c_get_bing_keys, 24,table='subs')
    
    
    return x[count_key]['bing_translator_name'],x[count_key]['bing_api_key'],x[count_key]['bing_region'],len(x)

def fix_sub_punctuation_text(f_all):

    all_ch=['?','.','!',',']
    all_l=[]

    for line in f_all.splitlines():

        line_contains_html_i_tag = False
        # Check if the line contains html <i> tags
        if '<i>' in line and '</i>' in line:
            line_contains_html_i_tag = True
            # Find the start and end positions of the <i> tag
            start_index = line.find('<i>') + len('<i>')
            end_index = line.find('</i>')
            # Extract the text inside the <i> tag
            line_without_html_i_tag = line[start_index:end_index]
        
        if line_contains_html_i_tag:
            for ch in all_ch:
                found=False
                if line_without_html_i_tag.endswith(ch):
                   
                    line_without_html_i_tag=ch+line_without_html_i_tag[:-1]
                    # Create the original line by combining the modified text (line_without_html_i_tag) with the <i> tags
                    line = line[:start_index] + line_without_html_i_tag + line[end_index:]
                    all_l.append(line)
                    found=True
                    break
            if not found:
                all_l.append(line)
        
        else:
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
    return f_all

def fix_sub_punctuation_and_write(sub_file, separate_punct_file=False):

    try:
        # Open the file as binary data
        import chardet
        with open(sub_file, 'rb') as f:
            # Join binary lines for specified number of lines
            text = f.read()

        encoding=chardet.detect(text)['encoding']
        log.warning(f"PUNCT | encoding={encoding}")
        with open(sub_file, 'r', encoding=encoding) as f:
            # Join binary lines for specified number of lines
            text = f.read()
        
        text = fix_sub_punctuation_text(text)
        
        if separate_punct_file: sub_file = f"{sub_file}_punctuation_fix"
        with open(sub_file, mode="w", encoding="utf8") as f:
                 f.write(text)

        return sub_file
    except:
        return None
        pass

def send_translate(items):
    from resources.modules import general
    global global_sub_size,global_progress
    from resources.modules.auto_translate.googletrans import Translator  
        
        
    translator = Translator()  
    translation=translator.translate(items, dest='he').text
    global_progress+=1
    general.show_msg=f"Google Translate מתרגם  | {str(int(((global_progress* 100.0)/(global_sub_size)) ))}%"
    general.progress_msg=int(((global_progress* 100.0)/(global_sub_size)) )
    return translation
        
def translate_subs(input_file,output_file):
    global trans_result
    trans_result=[]
    
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
    
    if Addon.getSetting("translate_p")== '0': # Google
        global global_sub_size,global_progress
        split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
        ax2=split_string(text,3000)
        global_sub_size=len(ax2)
        global_progress=0
        log.warning('Start Google')
        
        general.show_msg=f"Google Translate מתרגם {encoding}"
        with futures.ThreadPoolExecutor() as executor:  # optimally defined number of threads
            res = [executor.submit(send_translate, txt) for txt in split_string(text,3000)]
            futures.wait(res)
        
        
        
        f_sub_pre=''
        xx=0
        
        general.progress_msg=0
        
        translation = '\n'.join((r.result() for r in res))
        f_sub_pre=translation
        
        f_sub_pre=f_sub_pre.replace('\r\n','\n') # Fix Subscene bug - replace CRLF with LF
        f_sub_pre=f_sub_pre.replace('\r','\n') # Replace CR with LF
        #all_text=f_sub_pre.replace(': ',':').replace('"# ','"#').split('\n')
    elif Addon.getSetting("translate_p")== '1': # Yandex
        
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
        num=get_random_number()
        base_url='https://t%s.freetranslations.org/freetranslationsorg.php?p1=auto&p2=he&p3='%str(num)
        
        
        split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
        f_sub_pre=''
        xx=0
        
        general.progress_msg=0
        ax2=split_string(text,500)
        thread=[]
        counter=0
        for items in ax2:
             thread.append(Thread(get_translated,base_url,items.replace('ה',''),counter,headers))
             counter+=1

             # general.show_msg=f"YANDEX מתרגם {encoding} | {str(int(((xx* 100.0)/(len(ax2))) ))}%"
             # general.progress_msg=int(((xx* 100.0)/(len(ax2))) )
             if general.break_all:
                 break
             xx+=1
        for td in thread:
            td.start()
        while 1:
            
            still_alive=0
            for threads in thread:
                  
                  if general.break_all:
                     
                     break
                                    
                  num_live=0
                  string_dp=''

                  still_alive=0
                  for yy in range(0,len(thread)):
                    if not thread[yy].is_alive():
                      num_live=num_live+1
                      
                    else:
                      still_alive=1
            general.show_msg=f"Yandex מתרגם {encoding} | {str(int(((num_live* 100.0)/(len(thread))) ))}%"
            general.progress_msg=int(((num_live* 100.0)/(len(thread))) )
                      
                  
                 
                  
                  
                  
            if still_alive==0:
                    break
        translation=sorted(trans_result, key=lambda x: x[1], reverse=False)
        for sub_title,index in translation:
            f_sub_pre=f_sub_pre+sub_title
             
    elif Addon.getSetting("translate_p")== '2': #Bing
        general.show_msg='Bing מתרגם ' 
        import requests, uuid, json
        
        
        count_key=get_last_key()
        # Add your key and endpoint
        nm,key,location,amount = select_key(count_key)
        endpoint = "https://api.cognitive.microsofttranslator.com"

        # location, also known as region.
        # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
        

        path = '/translate'
        constructed_url = endpoint + path

        params = {
            'api-version': '3.0',
            #'from': 'en',
            'to': ['he']
        }

        headers = {
            'Ocp-Apim-Subscription-Key': key,
            # location required if you're using a multi-service or regional (not global) resource.
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
       
        ax2=split_string(text,50000)
        f_sub_pre=''
        xx=0
        
        general.progress_msg=0
        for items in ax2:
            
            general.progress_msg=int(((xx* 100.0)/(len(ax2))) )
            if general.break_all:
                 break
            body = [{
                'text': items
            }]
            count_test=0
            while count_test<amount:
                general.show_msg=f"Bing מתרגם {encoding} | {nm} {str(count_key)}/{str(amount)} | {str(int(((xx* 100.0)/(len(ax2))) ))}%"
                request = requests.post(constructed_url, params=params, headers=headers, json=body)
                response = request.json()
                try:
                    f_sub_pre=f_sub_pre+response[0]['translations'][0]['text']
                    
                    set_last_key(count_key)
                    break
                except:
                    general.show_msg=str(response)
                    
                    if Addon.getSetting("bing_translate_keys_method") == '1':
                        count_key = random.randint(0, amount - 1) # Generate random number from 0 to keys count
                    else:
                        count_key+=1
                        if (count_key>amount):
                            count_key=0
                    nm,key,location,amount = select_key(count_key)
                    log.warning(f"DarkSubs Bing API: bing_translator_name={nm} | bing_api_key={key} | total_keys_amount={amount}")
                    headers = {
                        'Ocp-Apim-Subscription-Key': key,
                        # location required if you're using a multi-service or regional (not global) resource.
                        'Ocp-Apim-Subscription-Region': location,
                        'Content-type': 'application/json',
                        'X-ClientTraceId': str(uuid.uuid4())
                    }
                    count_test+=1
             
             
             
            xx+=1
            # You can pass more than one object in body.
            
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
   
    # Auto punctuation fix for external translated English to Hebrew subtitles. 
    if Addon.getSetting("auto_fix_sub_punctuation")=='true':
        f_all = fix_sub_punctuation_text(f_all)
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
    log.warning('filename: ')
    log.warning(filename)
    from resources.modules import general
    try:
        x=int(download_data['url'])
        log.warning(x)
        xbmc.Player().setSubtitleStream(x)
        return 'HebSubEmbeddedSelected'
    except:
        pass
    
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
        try:
            sub_file=impmodule.download(download_data,MySubFolder)
        except Exception as e:
            log.warning(f"Exception downloading sub, configuring general.break_all=True... | Exception: {str(e)}")
            general.break_all=True
            return 'FaultSubException'
        
    # Auto punctuation fix for external Hebrew subtitles.
    if language=='Hebrew' and Addon.getSetting("auto_fix_sub_punctuation")=='true':
        try:
            fix_sub_punctuation_and_write(sub_file)
        except Exception as e:
            log.warning(f"Exception in fix_sub_punctuation_and_write | Exception: {str(e)}")
            pass
    
    elif language!='Hebrew' and Addon.getSetting("auto_translate")=='true':
        
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
    log.warning(f"general.break_all: {general.break_all}")
    # if general.break_all:
        # return 'HebSubEmbeddedSelected'
        # return 'FaultSubException'
    return sub_file