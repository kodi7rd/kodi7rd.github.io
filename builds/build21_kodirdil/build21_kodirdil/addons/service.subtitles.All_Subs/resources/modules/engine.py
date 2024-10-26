
import random
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
from urllib.parse import  unquote_plus, unquote, quote, quote_plus
from resources.modules.general import Thread,CachedSubFolder,TransFolder,user_dataDir
from resources.modules import cache
from resources.modules.general import DEFAULT_REQUEST_TIMEOUT
global trans_result
from concurrent import futures
trans_result=[]
iconx=xbmcaddon.Addon().getAddonInfo('icon')
MyScriptID = xbmcaddon.Addon().getAddonInfo('id')
break_all=False


from resources.sources import ktuvit
from resources.sources import wizdom
from resources.sources import opensubtitles
from resources.sources import yify
from resources.sources import subsource
from resources.sources import subscene
from resources.sources import bsplayer
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

def sort_subtitles(f_result,video_data):

    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    
    from resources.modules import general
    if Addon.getSetting("enable_autosub_notifications")=='true' or not xbmc.Player().isPlaying():
        # If searching subtitles from context menu - will show the message.
        general.show_msg = f"מסדר כתוביות 0/{len(f_result)}"
                     
    # Define the specific order for json_value['site_id']. In case of multiple subtitles with same percent - sort also by site_id using this order:
    site_id_order = ['[Ktuvit]', '[Wizdom]', '[OpenSubtitles]', '[YIFY]', '[SubSource]', '[Subscene]', '[BSPlayer]']
    
    # Get video quality from Kodi
    quality = f"{xbmc.getInfoLabel('VideoPlayer.VideoResolution')}p" if xbmc.Player().isPlaying() else None
    if quality and quality.lower()=="4kp":
        quality = "2160p"
    
    # List of release names
    release_names = ['blueray','bluray','blu-ray','bdrip','brrip','brip',
                      'hdtv','hdtvrip','pdtv','tvrip','hdrip','hd-rip',
                      'web','web-dl','web dl','web-dlrip','webrip','web-rip',
                      'dvdr','dvd-r','dvd-rip','dvdrip','cam','hdcam','cam-rip','camrip','screener','dvdscr','dvd-full',
                      'telecine','hdts','telesync']
    
    hebrew_subtitles = []
    english_subtitles = []
    other_languages_subtitles = []
    count = 0
    
    ###############################################################################################
    # Define functions before the for loop
    def append_subtitles(subtitles_list, json_value, percent):
        return subtitles_list.append((
            json_value['label'],
            '[COLOR %s]' % json_value['sub_color'] + json_value['label2'] + '[/COLOR]',
            json_value['iconImage'],
            json_value['thumbnailImage'],
            json_value['url'],
            percent,
            json_value['sync'],
            json_value['hearing_imp'],
            json_value['filename'],
            json_value['site_id']
        ))
      
      
    def remove_subtitle_or_video_extension_if_exists(file_name):
        
        # Define a list of common video file extensions
        video_file_extensions = ['mkv', 'mp4', 'm4p', 'avi', 'mov', 'mpeg', 'mpg', 'flv', 'wmv', 'm4v', 'webm', '3gp', 'ogg', 'ogv', 'rmvb', 'divx', 'vob', 'dat', 'mts', 'm2ts', 'ts', 'yuv']
        # Define a list of common video file extensions
        subtitle_file_extensions = ['srt', 'str', 'sub', 'sup', 'idx', 'ass', 'ssa', 'vtt', 'smi']
        
        # Extract the basename of the file from the path
        file_name_without_extension, file_extension = os.path.splitext(file_name)
    
        # Remove the dot and check the extension
        file_extension = file_extension.lstrip('.')
        
        # If the extension is in the list of video extensions, remove it
        if file_extension in video_file_extensions or file_extension in subtitle_file_extensions:
            return file_name_without_extension
            
        return file_name
        
        
    def clean_string_and_create_array(file_name):
    
        file_name = remove_subtitle_or_video_extension_if_exists(file_name)
        
        cleaned_file_name = (
            file_name.strip()
            .replace("_", ".")
            .replace(" ", ".")
            .replace("+", ".")
            .replace("/", ".")
            .replace("-", ".")
        )
        return [x.strip().lower() for x in cleaned_file_name.split(".") if x != '']
        
        
    def similar(w1, w2):
        from difflib import SequenceMatcher
        s = SequenceMatcher(None, w1, w2)
        return int(round(s.ratio()*100))
        
        
    def calculate_sync_percentage(video_name_array, subtitle_name_array):

        # Check and add missing quality
        if quality and quality not in video_name_array and quality in subtitle_name_array:
            video_name_array.append(quality)

        # Check for release names and extend arrays
        for release_name in release_names:
            if release_name in video_name_array and release_name in subtitle_name_array:
                video_name_array.extend([release_name] * 3)
                subtitle_name_array.extend([release_name] * 3)

        # Calculate similarity
        percent = similar(video_name_array, subtitle_name_array)

        return percent
    ###############################################################################################
    
    # Clean video file_original_path
    video_file_original_path_array = clean_string_and_create_array(video_data['file_original_path'])
    # Clean video Tagline
    video_tagline_array = clean_string_and_create_array(video_data['Tagline'])
    
    for result_value in f_result:
    
        if Addon.getSetting("enable_autosub_notifications")=='true' or not xbmc.Player().isPlaying():
            # If searching subtitles from context menu - will show the message.
            general.show_msg = f"מסדר כתוביות {count}/{len(f_result)}"
            count += 1
          
        json_value = json.loads(json.dumps(result_value))
        
        ################### Calculate Sync Percentage #################################################
        # Clean subtitle name
        subtitle_name_array = clean_string_and_create_array(json_value['filename'])
        
        # Video file_original_path sync percentage
        percent_from_file_original_path = calculate_sync_percentage(video_file_original_path_array, subtitle_name_array)
        
        # Video Tagline sync percentage
        percent_from_video_tagline = calculate_sync_percentage(video_tagline_array, subtitle_name_array)
        
        percent = max(percent_from_file_original_path, percent_from_video_tagline)
        ###############################################################################################
        
        
        ################### Append subtitle to corresponding language subs list #######################
        if 'language=Hebrew' in json_value['url'] or 'Hebrew' in json_value['label']:
            append_subtitles(hebrew_subtitles, json_value, percent)
       
        elif 'language=English' in json_value['url'] or 'English' in json_value['label']:
            append_subtitles(english_subtitles, json_value, percent)
           
        else:
            append_subtitles(other_languages_subtitles, json_value, percent)
        ###############################################################################################
    
    
    ################### Final Subtitles Sorting ###################################################
    def custom_sort(subtitles_list, site_id_order, by_language_name=False):
        # Sort also by language name (x[0]) if by_language_name is True
        if by_language_name:
            return sorted(subtitles_list, key=lambda x: (x[0], -x[5], site_id_order.index(x[9]) if x[9] in site_id_order else len(site_id_order)))
        # Sort by percent (-x[5]) and site_id (x[9]) only
        return sorted(subtitles_list, key=lambda x: (-x[5], site_id_order.index(x[9]) if x[9] in site_id_order else len(site_id_order)))

    # Sort languages
    hebrew_subtitles = custom_sort(hebrew_subtitles, site_id_order)
    english_subtitles = custom_sort(english_subtitles, site_id_order)
    other_languages_subtitles = custom_sort(other_languages_subtitles, site_id_order, by_language_name=True)

    # Combine all sorted subtitles list
    sorted_subtitles = []
    sorted_subtitles = hebrew_subtitles + english_subtitles + other_languages_subtitles
    ###############################################################################################

    return sorted_subtitles

# Prettify website source name for subs search dialog
def format_website_source_name(source):
    if source == "ktuvit":
        return "Ktuvit"
    if source == "wizdom":
        return "Wizdom"
    if source == "opensubtitles":
        return "OpenSubtitles"
    if source == "yify":
        return "YIFY"
    if source == "subsource":
        return "SubSource"
    if source == "subscene":
        return "Subscene"
    if source == "bsplayer":
        return "BSPlayer"
    return source
        
def c_get_subtitles(video_data):
    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    from resources.modules import general

    log.warning("DEBUG | c_get_subtitles | Searching for:")
    log.warning(f"DEBUG | c_get_subtitles | video_data={video_data}")

    source_dir = os.path.join(addonPath, 'resources', 'sources')
    thread=[]
    all_sources=[]
    ktuvit.global_var=[]
    wizdom.global_var=[]
    opensubtitles.global_var=[]
    yify.global_var=[]
    subsource.global_var=[]
    subscene.global_var=[]
    bsplayer.global_var=[]
    
    # Determine wether to search hebrew language
    search_language_hebrew_bool = (Addon.getSetting('language_hebrew') == 'true' or Addon.getSetting("all_lang") == 'true')
    
    # Israeli subtitles sources
    
    if Addon.getSetting('ktuvit')=='true' and search_language_hebrew_bool:
        thread.append(Thread(ktuvit.get_subs,video_data))
        all_sources.append(('ktuvit',ktuvit))
        
    if Addon.getSetting('wizdom')=='true' and search_language_hebrew_bool:
        thread.append(Thread(wizdom.get_subs,video_data))
        all_sources.append(('wizdom',wizdom))
        
    # Global subtitles sources
        
    if Addon.getSetting('opensubtitles')=='true':
        thread.append(Thread(opensubtitles.get_subs,video_data))
        all_sources.append(('opensubtitles',opensubtitles))
        
    if Addon.getSetting('yify')=='true':
        thread.append(Thread(yify.get_subs,video_data))
        all_sources.append(('yify',yify))
        
    if Addon.getSetting('subsource')=='true':
        thread.append(Thread(subsource.get_subs,video_data))
        all_sources.append(('subsource',subsource))
        
    if Addon.getSetting('subscene')=='true':
        thread.append(Thread(subscene.get_subs,video_data))
        all_sources.append(('subscene',subscene))
    
    if Addon.getSetting('bsplayer')=='true' and search_language_hebrew_bool:
        thread.append(Thread(bsplayer.get_subs,video_data))
        all_sources.append(('bsplayer',bsplayer))
        

    for td in thread:
      xbmc.sleep(100)
      td.start()
      

    tt={}
    for i in range (0,40): 
      tt[i]="red"
    start_time = time.time()
    num_live=0
    break_all=False
    ExcludeTime = int((Addon.getSetting('max_search_time')))
    

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

#################### PUNCTUATION FIX ###########################################################
def fix_sub_punctuation_text(original_subtitle_lines):

    # Remove <i> </i> tags
    original_subtitle_lines = original_subtitle_lines.replace('<i>', '').replace('</i>', '')

    import re
    punctuation_regex = re.compile(r'[.,?!:…]+$') # "…" is not three regular dots, but single Ellipsis character. https://en.wikipedia.org/wiki/Ellipsis
    hyphen_mark = '-'
    modified_lines = []
        
    # Helper function to check if a line contains Hebrew characters
    def is_hebrew(line):
        hebrew_unicode_range = (0x0590, 0x05FF)
        for char in line:
            if hebrew_unicode_range[0] <= ord(char) <= hebrew_unicode_range[1]:
                return True
        return False
    ###############################################################
    
    # Helper function to fix punctuation in a text line
    def fix_punctuation_in_text(text):

        # Check for hyphen at the start of the line
        starts_with_hyphen = text.startswith(hyphen_mark)
        
        # Temporary remove hyphen
        if starts_with_hyphen: text = text.lstrip(hyphen_mark)
    
        match = punctuation_regex.search(text)
        # From: "קרובים יותר ממה שהיינו אי פעם."
        # To: ".קרובים יותר ממה שהיינו אי פעם"
        if match:
            # Move punctuation to the beginning
            text =  match.group(0) + text[:match.start()]
        
        # From: "-קח את זה"
        # To: "קח את זה-"
        # Bring back hyphen to end of text
        if starts_with_hyphen: text += hyphen_mark
            
        return text
    ###############################################################
        
    for line in original_subtitle_lines.splitlines():
        if is_hebrew(line):
            # Fix punctuation for the entire line
            line = fix_punctuation_in_text(line.rstrip())
        modified_lines.append(line)
                
    return '\n'.join(modified_lines)

def fix_sub_punctuation_and_write(sub_file):

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
        
        with open(sub_file, mode="w", encoding="utf8") as f:
                 f.write(text)

        return sub_file
    except Exception as e:
        log.warning(f"Exception in fix_sub_punctuation_and_write | Exception: {str(e)}")
        return None

#################### HEARING IMPAIRED TAGS REMOVE ###########################################################
def remove_hi_tags_and_write(sub_file):
    
    def remove_hi_subs(subtitle_content):

        import re

        # Remove unwanted characters and patterns from a line.
        def clean_line(line):
            # Remove music notation symbols (♪)
            line = re.sub(r'[♪]+\s?', '', line)
            # Remove text within square brackets (e.g., [door slams], [music playing])
            line = re.sub(r'\[[^\]]*\]\s?', '', line)
            # Remove text within parentheses (e.g., (whispering), (background noise))
            line = re.sub(r'\([^\)]*\)\s?', '', line)
            return line
        
        # Initialize a list to hold processed lines
        final_lines = []
        
        for original_line in subtitle_content.splitlines():
            cleaned_line = clean_line(original_line)
            
            # Check if the line was modified
            if original_line != cleaned_line:
                
                # Strip leading and trailing whitespace
                cleaned_line = cleaned_line.strip()
                
                # Skip empty lines or lines that are just isolated "-" or ":"
                if cleaned_line and not re.match(r'^\s*[-:]\s*$', cleaned_line):
                    final_lines.append(cleaned_line)

            else:
                final_lines.append(original_line)

        # Join lines back with newlines
        return "\n".join(final_lines)

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
        
        text = remove_hi_subs(text)
        
        with open(sub_file, mode="w", encoding="utf8") as f:
                 f.write(text)

        return sub_file
    except Exception as e:
        log.warning(f"Exception in remove_hi_tags_and_write | Exception: {str(e)}")
        return None

#################### MACHINE TRANSLATE WEBSITES #######################################

#################### BING WEB #########################################################
def bing_web_send_translate(bing_translator_class, text):
    from resources.modules import general
    global global_sub_size,global_progress
    
    from_lang = 'auto-detect'
    to_lang = 'he'
    translation = bing_translator_class.translate(text, from_lang, to_lang)['translations'][0]['text']
    
    global_progress+=1
    general.show_msg=f"Bing Web מתרגם | {str(int(((global_progress* 100.0)/(global_sub_size)) ))}%"
    general.progress_msg=int(((global_progress* 100.0)/(global_sub_size)) )
    return translation
    
def bing_web_machine_translate(text, encoding):
    from resources.modules import general
    global global_sub_size,global_progress
    split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
    ax2=split_string(text,1000)
    global_sub_size=len(ax2)
    global_progress=0
    log.warning('DEBUG | bing_web_machine_translate | Starting Bing Web Translation')

    general.show_msg=f"Bing Web מתרגם {encoding}"
    
    from resources.modules.auto_translate.bing_web import BingTranslator
    # Initalize Bing Web class session
    bing_translator_class = BingTranslator()
    
    with futures.ThreadPoolExecutor() as executor:  # optimally defined number of threads
        res = [executor.submit(bing_web_send_translate, bing_translator_class, text) for text in split_string(text,1000)] # 1000 is max chars limit for bing web
        futures.wait(res)

    general.progress_msg=0

    f_sub_pre = '\n'.join((r.result() for r in res))

    f_sub_pre=f_sub_pre.replace('\r\n','\n') # Fix Subscene bug - replace CRLF with LF
    f_sub_pre=f_sub_pre.replace('\r','\n') # Replace CR with LF
    
    return f_sub_pre

#################### GOOGLE ###########################################################
def google_send_translate(items):
    from resources.modules import general
    global global_sub_size,global_progress
    from resources.modules.auto_translate.googletrans import Translator  
        
        
    translator = Translator()  
    translation=translator.translate(items, dest='he').text
    
    global_progress+=1
    general.show_msg=f"Google Translate מתרגם | {str(int(((global_progress* 100.0)/(global_sub_size)) ))}%"
    general.progress_msg=int(((global_progress* 100.0)/(global_sub_size)) )
    return translation
    
def google_machine_translate(text, encoding):
    from resources.modules import general
    global global_sub_size,global_progress
    split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
    ax2=split_string(text,3000)
    global_sub_size=len(ax2)
    global_progress=0
    log.warning('Start Google')

    general.show_msg=f"Google Translate מתרגם {encoding}"
    with futures.ThreadPoolExecutor() as executor:  # optimally defined number of threads
        res = [executor.submit(google_send_translate, txt) for txt in split_string(text,3000)]
        futures.wait(res)

    general.progress_msg=0

    f_sub_pre = '\n'.join((r.result() for r in res))

    f_sub_pre=f_sub_pre.replace('\r\n','\n') # Fix Subscene bug - replace CRLF with LF
    f_sub_pre=f_sub_pre.replace('\r','\n') # Replace CR with LF
    
    return f_sub_pre


#################### YANDEX ###########################################################
def yandex_get_random_number():
    import random
    result=22
    while (result == 20) or (result == 21) or (result == 22):
        result=int(random.random()*22+1)
    return result
    
def yandex_get_translated(base_url,items,counter,headers):
    import requests
    global trans_result
    translation='Error code'
    count_error=0
    while ('Error code' in translation or 'Resource Limit Is Reached' in translation or 'Access denied' in translation or 'onError_3' in translation):
        try:
            translation=requests.get(base_url+(items),headers=headers).text
        except:
            num=yandex_get_random_number()
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
    
def yandex_machine_translate(text, encoding):
    global trans_result
    from resources.modules import general
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Alt-Used': 't19.freetranslations.org',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    num=yandex_get_random_number()
    base_url='https://t%s.freetranslations.org/freetranslationsorg.php?p1=auto&p2=he&p3='%str(num)


    split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
    f_sub_pre=''
    xx=0

    general.progress_msg=0
    ax2=split_string(text,500)
    thread=[]
    counter=0
    for items in ax2:
         thread.append(Thread(yandex_get_translated,base_url,items.replace('ה',''),counter,headers))
         counter+=1
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
        
    return f_sub_pre


#################### BING API #########################################################
def bing_c_get_keys():
    import requests
    x=requests.get('https://kodi7rd.github.io/repository/other/DarkSubs_Bing/darksubs_bing_api.json', timeout=DEFAULT_REQUEST_TIMEOUT).json()
    return x
    
def bing_get_last_key():
    try:
        last_key_file=os.path.join(user_dataDir,'last_bing_key.txt')
        file = open(last_key_file, 'r') 
        file_data= file.read()
        file.close()
    
        file_data=int(file_data)
    except:
        x=bing_c_get_keys()
        file_data = random.randint(0, len(x) - 1) # Generate random number from 0 to keys count
    return file_data
    
def bing_set_last_key(count_key):
    try:
        last_key_file=os.path.join(user_dataDir,'last_bing_key.txt')
        file = open(last_key_file, 'w') 
        file.write(str(count_key))
        file.close()
    except:
        pass
    
def bing_select_key(count_key):
    x=cache.get(bing_c_get_keys, 24,table='subs')
    
    
    return x[count_key]['bing_translator_name'],x[count_key]['bing_api_key'],x[count_key]['bing_region'],len(x)
    
def bing_api_machine_translate(text, encoding):
    from resources.modules import general
    general.show_msg='Bing מתרגם'
    import requests, uuid, json
    
    
    count_key=bing_get_last_key()
    # Add your key and endpoint
    nm,key,location,amount = bing_select_key(count_key)
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
                
                bing_set_last_key(count_key)
                break
            except:
                general.show_msg=str(response)
                
                count_key = random.randint(0, amount - 1) # Generate random number from 0 to keys count
                nm,key,location,amount = bing_select_key(count_key)
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
        
    return f_sub_pre
    
      
#################### MACHINE TRANSLATE ################################################
def machine_translate_subs(input_file,output_file):
    global trans_result
    trans_result=[]
    
    from resources.modules import general
    
    g_show_msg=general.show_msg
    progress_msg=general.progress_msg
    general.show_msg='אנא המתן'+'\n'+'מתרגם'
    log.warning('אנא המתן'+'\n'+'מתרגם')

    # Open the file as binary data
    with open(input_file, 'rb') as f:
        # Join binary lines for specified number of lines
        text = f.read()

    import chardet
    encoding=chardet.detect(text)['encoding']
    log.warning('encoding:'+encoding)
    
    if encoding=='ISO-8859-7':
      text=text.decode('cp1253','ignore')
    elif encoding=='MacCyrillic':
      text=text.decode('cp1256','ignore')
    else:
      text=text.decode(encoding,'ignore')

    path=xbmc_tranlate_path('special://home/addons/%s/resources/modules/auto_translate'%MyScriptID)
    sys.path.append(path)
    
    # For settings changes to take effect.
    Addon=xbmcaddon.Addon()
    
    # Google https://translate.google.com
    if Addon.getSetting("translate_p")=='0':
        f_sub_pre = google_machine_translate(text, encoding)
        
    # Bing Web https://www.bing.com/Translator
    elif Addon.getSetting("translate_p")=='1':
        f_sub_pre = bing_web_machine_translate(text, encoding)
        
    # Yandex
    elif Addon.getSetting("translate_p")=='2':
        f_sub_pre = yandex_machine_translate(text, encoding)
             
    # Bing API - Currently unused.
    # elif Addon.getSetting("translate_p")=='2':
        # f_sub_pre = bing_api_machine_translate(text, encoding)
            
    
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
        return 'EmbeddedSubSelected'
    except:
        pass
    
    ext=[".idx",".sup",".srt",".sub",".str",".ass"]
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
    c_sub_file=os.path.join(CachedSubFolder, f"{source}_{language}_{filename}")
    found_in_cache=False
    for items in ext:
        log.warning(c_sub_file+items)
        if os.path.exists(c_sub_file+items):
            sub_file=c_sub_file+items
            found_in_cache=True
            log.warning('Found cache')
            break
    if not found_in_cache:
        try:
            sub_file=impmodule.download(download_data,MySubFolder)
        except Exception as e:
            log.warning(f"Exception downloading sub, configuring general.break_all=True... | Exception: {str(e)}")
            general.break_all=True
            return 'FaultSubException'
        
    # Auto punctuation fix for external Hebrew subtitles.
    if 'Hebrew' in language:
        if Addon.getSetting("auto_fix_sub_punctuation")=='true':
            try:
                fix_sub_punctuation_and_write(sub_file)
            except Exception as e:
                log.warning(f"Exception in fix_sub_punctuation_and_write | Exception: {str(e)}")
                pass
    
    elif Addon.getSetting("auto_translate")=='true':
        f_count=0
        for filename_o in os.listdir(TransFolder):
            
            f_count+=1
        if (f_count>max_sub_cache):
            for filename_o in os.listdir(TransFolder):
                f = os.path.join(TransFolder, filename_o)
                os.remove(f)
        trans_file=os.path.join(TransFolder, filename)
        already_translated=True
        if not os.path.exists(trans_file):
            already_translated=False
            machine_translate_subs(sub_file,trans_file)
        sub_file=trans_file
            
    # Remove HI (Hearing Impaired) subtitle tags for non-Hebrew subs.
    hearing_imp = download_data.get('hearing_imp', 'false')
    if hearing_imp=='true' and Addon.getSetting("auto_remove_hi_tags")=='true':
        if Addon.getSetting("enable_autosub_notifications")=='true':
            from resources.modules.general import notify
            notify("כתובית לכבדי שמיעה נבחרה, מנקה...")
        try:
            remove_hi_tags_and_write(sub_file)
        except Exception as e:
            log.warning(f"Exception in remove_hi_tags_and_write | Exception: {str(e)}")
            pass
            
    log.warning(f"general.break_all: {general.break_all}")
    return sub_file