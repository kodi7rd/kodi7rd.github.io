# KODI-RD-IL ADDITION
# -*- coding: utf-8 -*-
import sys
import time,xbmc

# from  resources.modules import cache
global global_var,stop_all#global
global_var=[]
stop_all=0

import re,requests

type=['tv','movie']

import urllib,base64,json,logging

import zlib
BASE_URL = "http://www.cinemast.org/he/cinemast/api/"

class URLHandler():
    def __init__(self):
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('Accept-Encoding', 'gzip'),
                                  ('Accept-Language', 'en-us,en;q=0.5'),
                                  ('Pragma', 'no-cache'),
                                  ('Cache-Control', 'no-cache'),
                                  ('User-Agent',
                                   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 Kodi/17.2 (KHTML, like Gecko) Chrome/49.0.2526.111 Safari/537.36')]

    def request(self, url, data=None, query_string=None, ajax=False, referrer=None, cookie=None):
        if data is not None:
            data = urllib.urlencode(data)
        if query_string is not None:
            url += '?' + urllib.urlencode(query_string)
        if ajax:
            self.opener.addheaders += [('X-Requested-With', 'XMLHttpRequest')]
        if referrer is not None:
            self.opener.addheaders += [('Referrer', referrer)]
        if cookie is not None:
            self.opener.addheaders += [('Cookie', cookie)]

        content = None
  
        #if data is not None and 'password' not in data:
        #    logging.warning("Post Data: %s" % (data))
        try:
            response = self.opener.open(url, data,timeout=5)
            content = None if response.code != 200 else response.read()

            if response.headers.get('content-encoding', '') == 'gzip':
                try:
                    content = zlib.decompress(content, 16 + zlib.MAX_WBITS)
                except zlib.error:
                    pass

            if response.headers.get('content-type', '') == 'application/json':
                content = json.loads(content, encoding="utf-8")

            response.close()
        except Exception as e:
            pass
            # Second parameter is the filename
        return content

def login( notify_success=True):
        
        urlHandler = URLHandler()
        email = Addon.getSetting("Email")
        password = Addon.getSetting("Password")
        if email=='' or password=='':
          __settings__.openSettings()
          email = Addon.getSetting("Email")
          password = Addon.getSetting("Password")
        post_data = {'username': email, 'password': password}
        content = urlHandler.request(BASE_URL + "login/", post_data)

        if content['result'] == 'success':
            if notify_success:
                notify(32010)

            del content["result"]
            return content
        else:
            notify(32009)
            return None
def get_user_token( force_update=False):
        # results =cache.get(login, 24, False, table='pages')
        results =login(False)
        '''
        if force_update:
            store.delete('credentials')
        
        results = store.get('credentials')
        if results:
            results = json.loads(results)
        else:
            results = login(False)
            if results:
                store.set('credentials', json.dumps(results))
        '''
        return results
def subcenter_search(item,mode_subtitle,subtitle_list,check_one):
        import re
        results = []
        
        id_collection=[]
    
        search_string = re.split(r'\s\(\w+\)$', item["tvshow"])[0] if item["tvshow"] else item["title"]

        
        user_token =  get_user_token()
        
        if user_token:
            query = {"q": search_string.encode("utf-8"), "user": user_token["user"], "token": user_token["token"]}
            if item["tvshow"]:
                query["type"] = "series"
                query["season"] = item["season"]
                query["episode"] = item["episode"]
            else:
                query["type"] = "movies"
                if item["year"]:
                    query["year_start"] = int(item["year"]) 
                    query["year_end"] = int(item["year"])

            search_result =  urlHandler.request( BASE_URL + "search/", query)
   
            if search_result is not None and search_result["result"] == "failed":
                # Update cached token
                user_token =  get_user_token(True)
                query["token"] = user_token["token"]
                search_result =  urlHandler.request( BASE_URL + "search/", query)

            if search_result is not None and search_result["result"] == "failed":
                #xbmc.executebuiltin((u'Notification(%s,%s)' % ('טייפון', 'בעיה בנתוני התחברות')).encode('utf-8'))
  
                return results



            if search_result is None or search_result["result"] != "success" or search_result["count"] < 1:
                
                    return results

            results = search_result# _filter_results(search_result["data"], search_string, item)

        ret = []
        ok=True
        lang=[]
        lang.append('he')
        results2=[]
      
        for result in results['data']:
            total_downloads = 0
            counter = 0
            
            subs_list = result
            
              
            if subs_list is not None:
               

                for language in subs_list['subtitles']:
                        
                        
                       if language in lang:
                    #if xbmc.convertLanguage(language, xbmc.ISO_639_2) in item["3let_language"]:
                        for current in subs_list['subtitles'][language]:
                          title = current["version"]
                          if title not in subtitle_list:
                            counter += 1
                            
                            subtitle_list.append(title)
                            if check_one==True:
                              break
        return subtitle_list
def get_login_cook():
    import requests
    headers = {
    'authority': 'www.ktuvit.me',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://www.ktuvit.me',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    
    'accept-language': 'en-US,en;q=0.9',
    
    }

    data = '{"request":{"Email":"hatzel6969@gmail.com","Password":"Jw1n9nPOZRAHw9aVdarvjMph2L85pKGx79oAAFTCsaE="}}'

    login_cook = requests.post('https://www.ktuvit.me/Services/MembershipService.svc/Login', headers=headers, data=data).cookies
    login_cook_fix={}
    for cookie in login_cook:

            login_cook_fix[cookie.name]=cookie.value
    return login_cook_fix
def FirstPlace_Search(item,imdb_id,subtitle_list,check_one=False):
    global links_first
    import requests


    # login_cook=cache.get(get_login_cook,1, table='subs')
    login_cook=get_login_cook()
    
    
    if "tvshow" in item:
        if item["tvshow"]:
            s_type='1'
            s_title=item["tvshow"]
        
    else:
        s_type='0'
        s_title=item["title"]
    
    if 1:
        headers = {
            'authority': 'www.ktuvit.me',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'content-type': 'application/json',
            'origin': 'https://www.ktuvit.me',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.ktuvit.me/Search.aspx',
            'accept-language': 'en-US,en;q=0.9',
            
        }

        data = '{"request":{"FilmName":"%s","Actors":[],"Studios":null,"Directors":[],"Genres":[],"Countries":[],"Languages":[],"Year":"","Rating":[],"Page":1,"SearchType":"%s","WithSubsOnly":false}}'%(s_title,s_type)
        
        response = requests.post('https://www.ktuvit.me/Services/ContentProvider.svc/SearchPage_search', headers=headers, data=data).json()
        
        j_data=json.loads(response['d'])['Films']
        f_id=''
        
        for itt in j_data:
            
            if imdb_id==itt['ImdbID']:
                
                f_id=itt['ID']
                
        if f_id!='':
            url='https://www.ktuvit.me/MovieInfo.aspx?ID='+f_id
            
            import requests
        else:
            
            return []
            
        if "tvshow" in item:
            if item["tvshow"]:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
                    'Accept': 'text/html, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Connection': 'keep-alive',
                    'Referer': url,
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                    'TE': 'Trailers',
                }

                params = (
                    ('moduleName', 'SubtitlesList'),
                    ('SeriesID', f_id),
                    ('Season', item["season"]),
                    ('Episode', item["episode"]),
                )

                response = requests.get('https://www.ktuvit.me/Services/GetModuleAjax.ashx', headers=headers, params=params, cookies=login_cook).content
        else:
            headers = {
                'authority': 'www.ktuvit.me',
                'cache-control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'referer': 'https://www.ktuvit.me/MovieInfo.aspx?ID='+f_id,
                'accept-language': 'en-US,en;q=0.9',
                
            }
            params = (
                ('ID', f_id),
            )
           
            response = requests.get('https://www.ktuvit.me/MovieInfo.aspx', headers=headers, params=params, cookies=login_cook).content
            
        
        regex='<tr>(.+?)</tr>'
        m_pre=re.compile(regex,re.DOTALL).findall(response.decode('utf-8'))
        z=0
        subtitle=' '
       
        for itt in m_pre:
      
            regex='<div style="float.+?>(.+?)<br />.+?data-subtitle-id="(.+?)"'
            m=re.compile(regex,re.DOTALL).findall(itt)
            if len(m)==0:
                continue
            nm=m[0][0].replace('\n','').replace('\r','').replace('\t','').replace(' ','')
            data='{"request":{"FilmID":"%s","SubtitleID":"%s","FontSize":0,"FontColor":"","PredefinedLayout":-1}}'%(f_id,m[0][1])

            subtitle_list.append(nm)
            if check_one==True:
                   break
            links_first=subtitle_list
           
            z=z+1
    return subtitle_list
    

def Caching(filename,url):
    

    try:
      x=requests.get(url).json()
    except:
      x={}
      pass
    return x
def GetJson(imdb,mode_subtitle,season=0,episode=0,version=0,check_one=False,global_var=[]):
    global links_wizdom
    filename = 'wizdom.imdb.%s.%s.%s.json'%(imdb,season,episode)
    url = "http://wizdom.xyz/api/search?action=by_id&imdb=%s&season=%s&episode=%s&version=%s"%(imdb,season,episode,version)
    
    # logging.warning(url)
    
    json_object = Caching(filename,url)
    
    # logging.warning('json_object:'+ str(json_object))
    
    subs_rate = []
    subtitle=' '
    x=0
    id_all_collection=[]
    subtitle_list=global_var
    
    if json_object!=0:
        for item_data in json_object:
       
            
            
            if item_data["id"] not in id_all_collection:
                id_all_collection.append(item_data["id"])
                if item_data["versioname"] in subtitle_list:
                    continue
                subtitle_list.append(item_data["versioname"])

                if check_one==True:
                              break
                links_wizdom=subtitle_list
                x=x+1

    if (json_object)==0:
      return 0,' ',subtitle_list
    else:
        
      return subtitle_list
def lowercase_with_underscores(str):
    from unicodedata import normalize
    return normalize('NFKD', (str)).encode('utf-8', 'ignore')
def get_links(tv_movie,original_title,name,season_n,episode_n,season,episode,show_original_year,id,check_one=False):
    global global_var,stop_all
    import xbmcvfs
    xbmc_tranlate_path=xbmcvfs.translatePath
    import xmlrpc.client as xc
    xmlserver=xc.Server
    langs = []
    langDict = {'Hebrew': 'heb'}
    
    try:
        try: langs = langDict['Hebrew'].split(',')
        except: langs.append(langDict['Hebrew'])
    except: pass

    item={}
 
    da=[]
    da.append((tv_movie,original_title,name,season_n,episode_n,season,episode,show_original_year,id,check_one))

    
    if tv_movie=='movie':
      item["movie"]=original_title.replace("%20"," ").replace("%27","'")
    else:
      item["tvshow"]=original_title.replace("%20"," ").replace("%27","'")
    if tv_movie=='tv':
      imdbid_data='https://api.themoviedb.org/3/tv/%s?api_key=34142515d9d23817496eeb4ff1d223d0&append_to_response=external_ids'%id
    else:
      imdbid_data='https://api.themoviedb.org/3/movie/%s?api_key=34142515d9d23817496eeb4ff1d223d0&append_to_response=external_ids'%id

    x=requests.get(imdbid_data).json()
    
    try:
        imdbid=x['external_ids']['imdb_id']
        if imdbid==None:
          imdbid=''
    except:
      imdbid=''
    
    item['title']=original_title.replace("%20"," ").replace("%27","'")
  
    item["season"]=season#.replace('%20','0')
    item["episode"]=episode#.replace('%20','0')
    item["year"]=show_original_year
    subtitle_list=[]


    fixed_list=[]
    global_var1=''
    global_var2=''
    global_var3=''
    try:
        global_var1=(FirstPlace_Search(item,imdbid,subtitle_list,check_one))

    except Exception as e:
        # logging.warning('Error in screwzira:'+str(e))
        pass
    
    # if check_one==True:
      
      # if len (global_var)>0:
        # return global_var
    
    try:
        global_var2=GetJson(imdbid,'1',season=season,episode=episode,version=lowercase_with_underscores(item['title']),check_one=check_one,global_var=global_var)
    except Exception as e:
        # logging.warning('Error in wizdom:'+str(e))
        pass
    # try:
        # for items in result:
            # fixed_list.append((items['MovieReleaseName']))

        # global_var3=fixed_list
    # except Exception as e:
        # log.warning('Error in opensubtitles:'+str(e))
        # pass
    
    global_var=global_var1+global_var2#+global_var3
    return global_var