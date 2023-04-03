import sys,codecs
from requests import get
from os import path
from json import loads, load, dumps
from shutil import rmtree
from time import time
from unicodedata import normalize
from urllib.parse import unquote_plus, unquote, quote, urlparse, quote_plus
from xbmcaddon import Addon
from xbmcplugin import endOfDirectory, addDirectoryItem
from xbmcgui import ListItem, Dialog
from xbmcvfs import listdir, exists, mkdirs, translatePath
from xbmc import executebuiltin, getInfoLabel, executeJSONRPC, Player, log, getCondVisibility

##### burekas
import re
import PTN

myAddon = Addon()
myScriptID = myAddon.getAddonInfo('id')
myVersion = myAddon.getAddonInfo('version')
myProfile = myAddon.getAddonInfo('profile')
myTmp = translatePath(path.join(myProfile, 'temp', ''))
mySubFolder = translatePath(path.join(myTmp, 'subs'))
myName = myAddon.getAddonInfo('name')
myLang = myAddon.getLocalizedString

def wlog(msg):
	log((u"##**## [%s] %s" % ("Wizdom Subs", msg)), level=xbmc.LOGDEBUG)

def getDomain():
	try:
		myDomain = str(get('https://pastebin.com/raw/1vbRPSGh').text)
		return myDomain
	except Exception as err:
		wlog('Caught Exception: error in finding getDomain: %s' % format(err))
		return "wizdom.xyz" #"lolfw.com"

myDomain = getDomain() + "/api"

def convert_to_utf(file):
	try:
		with codecs.open(file, "r", "cp1255") as f:
			srt_data = f.read()

		with codecs.open(file, 'w', 'utf-8') as output:
			output.write(srt_data)
	except Exception as err:
		wlog('Caught Exception: error converting to utf: %s' % format(err))
		pass


def lowercase_with_underscores(str):
	return normalize('NFKD', str)


def download(id):
	try:
		rmtree(mySubFolder)
	except Exception as err:
		wlog('Caught Exception: error deleting folders: %s' % format(err))
		pass
	mkdirs(mySubFolder)
	subtitle_list = []
	exts = [".srt", ".sub", ".str"]
	archive_file = path.join(myTmp, 'wizdom.sub.'+id+'.zip')
	if not path.exists(archive_file):
		data = get("http://%s/"%format(myDomain)+"/files/sub/"+id, verify=False)
		open(archive_file, 'wb').write(data.content)
	executebuiltin(('Extract("%s","%s")' % (archive_file, mySubFolder)).encode('utf-8').decode(), True)
	for file_ in listdir(mySubFolder)[1]:
		file = path.join(mySubFolder, file_)
		if path.splitext(file)[1] in exts:
			subtitle_list.append(file)
	return subtitle_list

def getParams(arg):
	param = []
	paramstring = arg
	if len(paramstring) >= 2:
		params = arg
		cleanedparams = params.replace('?', '')
		if (params[len(params)-1] == '/'):
			params = params[0:len(params)-2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				param[splitparams[0]] = splitparams[1]

	return param

def getParam(name, params):
	try:
		return unquote_plus(params[name])
	except Exception as err:
		wlog('Caught Exception: error getting param: %s' % format(err))
		pass

def searchByIMDB(imdb, season=0, episode=0, version=0):
	filename = 'subs.search.wizdom.%s.%s.%s.json' % (imdb, season, episode)
	url = "http://%s/search?action=by_id&imdb=%s&season=%s&episode=%s&version=%s" % (
		myDomain, imdb, season, episode, version)

	wlog("wizdom searchByIMDB: %s" % url)
	json = cachingJSON(filename,url)
	#subs_rate = []  # TODO remove not in used
	if json != 0:
		for item_data in json:
			listitem = ListItem(label="Hebrew", label2=item_data["versioname"])
			listitem.setArt({'thumb': 'he'})
			listitem.setArt({'icon' : "%s" % ("{:.0f}".format(item_data["score"]/2))})
			if int(item_data["score"]) > 8:
				listitem.setProperty("sync", "true")
			url = "plugin://%s/?action=download&versioname=%s&id=%s&imdb=%s&season=%s&episode=%s" % (
					myScriptID, item_data["versioname"], item_data["id"],imdb, season, episode)
			addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)


def searchTMDB(type, query, year):
	tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'
	filename = 'subs.search.tmdb.%s.%s.%s.json' % (type,lowercase_with_underscores(query), year)
	if int(year) > 0:
		url = "http://api.tmdb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=en" % (
			type,tmdbKey, query, year)
	else:
		url = "http://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en" % (
			type,tmdbKey, query)

	#json_results = get_TMDB_data_popularity_and_votes_sorted(url,filename)
	json_results = get_TMDB_data_filtered(url,filename,query,type)    
    
	try:
		tmdb_id = int(json_results[0]["id"])
	except Exception as err:
		wlog('Caught Exception: error searchTMDB: %s' % format(err))
		return 0

	filename = 'subs.search.tmdb.externalIds.%s.%s.json' % (type,tmdb_id)
	url = "http://api.tmdb.org/3/%s/%s/external_ids?api_key=%s&language=en" % (type,tmdb_id, tmdbKey)
	wlog("searchTMDB external id: %s" % url)
	json = cachingJSON(filename,url) 

	try:
		imdb_id = json["imdb_id"]
	except Exception:
		wlog('Caught Exception: error searching movie: %s' % format(err))
		return 0

	return imdb_id

def getTVshowOriginalTitleByTMDBapi(source="notPlaying"): ###### burekas
    try:
        if (source=="notPlaying"):
            labelTVShowTitle = xbmc.getInfoLabel("ListItem.TVShowTitle")
            labelYear = xbmc.getInfoLabel("ListItem.Year")
        else:
            labelTVShowTitle = xbmc.getInfoLabel("VideoPlayer.TVShowTitle")
            labelYear = xbmc.getInfoLabel("VideoPlayer.Year")

        originalTitle = ''

        tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'
        filename = 'subs.search.tmdb.%s.%s.%s.json' % ("tv",lowercase_with_underscores(labelTVShowTitle), labelYear)
        
        if int(labelYear) > 0:
            #url = "http://api.tmdb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=en" % ("tv",tmdbKey, labelTVShowTitle, labelYear)
            url = "http://api.themoviedb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=en" % ("tv",tmdbKey, labelTVShowTitle, labelYear)
        else:
            #url = "http://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en" % ("tv",tmdbKey, labelTVShowTitle)
            url = "http://api.themoviedb.org/3/search/%s?api_key=%s&query=%s&language=en" % ("tv",tmdbKey, labelTVShowTitle)        
        
        wlog( "searchTMDB for original tv title: %s" % url)
        
        json_results = get_TMDB_data_popularity_and_votes_sorted(url,filename)
        
        '''
        json = cachingJSON(filename,url)

        resultsLen = len(json["results"])			
        itemIndex = -1
        voteCountMax = 0			
        popularityMax = 0						
        itemIndexMax = 0			
        for item in json['results']:
            itemIndex = itemIndex+1				
            if (item['vote_count'] > voteCountMax and item['popularity'] > popularityMax):
                voteCountMax = item['vote_count']
                popularityMax = item['popularity']						
                itemIndexMax = itemIndex
    
        if resultsLen > 0 :			
            #originalTitle = json["results"][itemIndexMax]["original_name"]
            originalTitle = json["results"][itemIndexMax]["name"]
		'''
        
        try:    originalTitle = json_results[0]["name"]
        except:
            wlog( "[%s]" % (e,))
            return ''         
               
        return originalTitle
    
    except Exception as err:
        wlog('Caught Exception: error searchTMDB: %s' % format(err))
        originalTitle = ''		
        return originalTitle

def cachingJSON(filename, url):
    from requests import get

    if (myAddon.getSetting( "json_cache" ) == "true"):
        json_file = path.join(myTmp, filename)
        if not path.exists(json_file) or not path.getsize(json_file) > 20 or (time()-path.getmtime(json_file) > 30*60):
            data = get(url, verify=False)
            open(json_file, 'wb').write(data.content)
        if path.exists(json_file) and path.getsize(json_file) > 20:
            with open(json_file,'r',encoding='utf-8') as json_data:
                json_object = load(json_data)
            return json_object
        else:
            return 0

    else:
        try:
          json_object = get(url).json()
        except:
          json_object = {}
          pass
        return json_object            

'''
##### burekas fix
# The url of ("search.php?action=guessit&filename=%s") is not working
# A new manual search is created instead
def ManualSearch(title):
	filename = "wizdom.manual.%s.json"%lowercase_with_underscores(title)
	url = "http://json.%s/search.php?action=guessit&filename=%s" % (
		myDomain, lowercase_with_underscores(title))
	wlog("ManualSearch:%s" % url)
	try:
		json = cachingJSON(filename,url)
		if json["type"] == "episode":
			imdb_id = searchTMDB("tv",str(json['title']), 0)
			if imdb_id:
				searchByIMDB(str(imdb_id), json['season'], json['episode'])    ##### burekas fix
		elif json["type"] == "movie":
			if "year" in json:
				imdb_id = searchTMDB("movie",str(json['title']), json['year'])
			else:
				imdb_id = searchTMDB("movie",str(json['title']), 0)
			if imdb_id:
				searchByIMDB(str(imdb_id), 0, 0)    ##### burekas fix
	except Exception as err:
		wlog('Caught Exception: error in manual search: %s' % format(err))
		pass
'''

##### burekas fix
# A new manual search
# a new way to get imdb id
def ManualSearch(title):    ##### burekas
	wlog("ManualSearch for: %s" % title)

	item = {}
	item['tvshow'], item['season'], item['episode'], item['dbtype'] = checkAndParseIfTitleIsTVshowEpisode(title)
	wlog("Parsed item tvshow result: " + item['tvshow'])

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
					wlog("item imdb_id %s" % (item['imdb_id']))         
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

		_season = item['season'].split("0")
		_episode = item['episode'].split("0")
		if _season[0] == '':
			item['season'] = _season[1]
		if _episode[0] == '':
			item['episode'] = _episode[1]

		item['imdb_id'] = searchForIMDBID(_query, item)                


	try:
		if item['imdb_id']:        
			if item['tvshow'] == 'NotTVShowEpisode':
				searchByIMDB(str(item['imdb_id']), 0, 0)    ##### burekas fix            
			else:
				searchByIMDB(str(item['imdb_id']), item['season'], item['episode'])    ##### burekas fix

	except Exception as err:
		wlog('Caught Exception: error in manual search: %s' % format(err))
		pass

def get_TMDB_data_popularity_and_votes_sorted(url,filename):    ##### burekas
    wlog("searchTMDB: %s" % url)
    json = cachingJSON(filename,url)
    json_results = json["results"]
    wlog("searchTMDB: json_results - " + repr(json_results))
    json_results.sort(key = lambda x:x["popularity"], reverse=True)
    json_results.sort(key = lambda x:x["vote_count"], reverse=True)    
    wlog("searchTMDB: json_results sorted - " + repr(json_results))

    return json_results
    
def get_TMDB_data_filtered(url,filename,query,type):    ##### burekas
    wlog("searchTMDB: %s" % url)
    wlog("query filtered: %s" % query)
    json = cachingJSON(filename,url)
    json_results = json["results"]
    wlog("searchTMDB: json_results - " + repr(json_results))
    if type=='tv':
        json_results.sort(key = lambda x:x["name"]==query, reverse=True)
    else:
        json_results.sort(key = lambda x:x["title"]==query, reverse=True)
    wlog("searchTMDB: json_results sorted - " + repr(json_results))

    return json_results    

def checkAndParseIfTitleIsTVshowEpisode(manualTitle):  ##### burekas
    try:
        pattern = re.compile(r"%20|_|-|\+|\.")
        replaceWith = " "
        manualTitle = re.sub(pattern, replaceWith, manualTitle)

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

    except Exception as err:
        log( "checkAndParseIfTitleIsTVshowEpisode error: '%s'" % err)                
        return ["NotTVShowEpisode", "0", "0",'']

def searchForIMDBID(query,item):  ##### burekas 
    import requests                       
    year=item["year"]
    info=(PTN.parse(query))
    tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'
    imdb_id = 0    

    if item["tvshow"] and item['dbtype'] == 'episode':    
        type_search='tv'
        filename = 'subs.search.tmdb.%s.%s.%s.json'%(type_search,lowercase_with_underscores(item['tvshow']),year)        
        url="https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&language=en&append_to_response=external_ids"%(type_search,tmdbKey,quote_plus(item['tvshow']))
          #url="https://api.tmdb.org/3/search/%s?api_key=%s&query=%s&year=%s&language=he&append_to_response=external_ids"%(type_search,tmdbKey,quote_plus(item['tvshow']),year)
          
          #url='https://www.omdbapi.com/?apikey=8e4dcdac&t=%s&year=%s'%(item["tvshow"],item["year"])
       
        #json_results = get_TMDB_data_popularity_and_votes_sorted(url,filename)
        json_results = get_TMDB_data_filtered(url,filename,item['tvshow'],type_search)

        try:    tmdb_id = int(json_results[0]["id"])
        except:
            wlog( "[%s]" % (e,))
            return 0        

        filename = 'subs.search.tmdb.fulldata.%s.%s.json'%(type_search,tmdb_id)
        url = "https://api.tmdb.org/3/%s/%s?api_key=%s&language=en&append_to_response=external_ids"%(type_search,tmdb_id,tmdbKey)
        wlog("searchTMDB fulldata id: %s" % url)
        json = cachingJSON(filename,url)
        
        try:    imdb_id = json['external_ids']["imdb_id"]
        except:    
            wlog( "[%s]" % (e,))
            return 0        
                  
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

        try:    tmdb_id = int(json_results[0]["id"])
        except:
            wlog( "[%s]" % (e,))
            return 0

        filename = 'subs.search.tmdb.fulldata.%s.%s.json'%(type_search,tmdb_id)
        url = "https://api.tmdb.org/3/%s/%s?api_key=%s&language=en&append_to_response=external_ids"%(type_search,tmdb_id,tmdbKey)
        wlog("searchTMDB fulldata id: %s" % url)        
        json = cachingJSON(filename,url)
        
        try:    imdb_id = json['external_ids']["imdb_id"]
        except:
            wlog( "[%s]" % (e,))
            return 0

        return imdb_id
    
def get_now_played():
    """
    Get info about the currently played file via JSON-RPC

    :return: currently played item's data
    :rtype: dict
    """
    request = dumps({
        'jsonrpc': '2.0',
        'method': 'Player.GetItem',
        'params': {
            'playerid': 1,
            'properties': ['showtitle', 'season', 'episode']
         },
        'id': '1'
    })
    item = loads(xbmc.executeJSONRPC(request))['result']['item']
    item['file'] = xbmc.Player().getPlayingFile()  # It provides more correct result
    return item

def get_more_data(filename):
    title, year = xbmc.getCleanMovieTitle(filename)
    wlog("CleanMovieTitle: title - %s, year - %s " %(title, year)) 
    tvshow=' '
    season=0
    episode=0
    try:
        yearval = int(year)
    except ValueError:
        yearval = 0
        
    patterns = [
                '\WS(?P<season>\d\d)E(?P<episode>\d\d)',
                '\W(?P<season1>\d)x(?P<episode1>\d\d)'
                ]
                
    for pattern in patterns:
        pattern = r'%s' % pattern
        match = re.search(pattern, filename, flags=re.IGNORECASE)
        wlog("regex match: " + repr(match)) 

        if match is None:
            continue
        else:
            title = title[:match.start('season') - 1].strip()
            season = match.group('season').lstrip('0')
            episode = match.group('episode').lstrip('0')
            wlog("regex parse: title = %s , season = %s, episode = %s " %(title,season,episode))
            return title,yearval,season,episode
    
    return title,yearval,season,episode     


# ---- main -----
if not exists(myTmp):
	mkdirs(myTmp)

action = None
if len(sys.argv) >= 2:
	params = getParams(sys.argv[2])
	action = getParam("action", params)

wlog("Version:%s" % myVersion)
wlog("Action:%s" % action)

if action == 'search':
	item = {}

	wlog("isPlaying:%s" % Player().isPlaying())
	if Player().isPlaying():
		item['year'] = getInfoLabel("VideoPlayer.Year")  # Year

		item['season'] = str(getInfoLabel("VideoPlayer.Season"))  # Season
		if item['season'] == '' or int(item['season']) < 1:
			item['season'] = 0
		item['episode'] = str(getInfoLabel("VideoPlayer.Episode"))  # Episode
		if item['episode'] == '' or int(item['episode']) < 1:
			item['episode'] = 0

		if item['episode'] == 0:
			item['title'] = lowercase_with_underscores(getInfoLabel("VideoPlayer.Title"))  # no original title, get just Title
		else:
			item['title'] = getTVshowOriginalTitleByTMDBapi('playing') #lowercase_with_underscores(getInfoLabel("VideoPlayer.TVshowtitle"))  # Show
		if item['title'] == "":
			item['title'] = lowercase_with_underscores(getInfoLabel("VideoPlayer.OriginalTitle"))  # try to get original title
		item['file_original_path'] = unquote(Player().getPlayingFile())  # Full path of a playing file
		item['file_original_path'] = item['file_original_path'].split("?")
		item['file_original_path'] = path.basename(item['file_original_path'][0])[:-4]
        
		if not (item['title'] and item['year']) :
			now_play_data = get_now_played()
			item['title'],item['year'],item['season'],item['episode']=get_more_data(now_play_data['label'])            
		
	else:   # Take item params from window when kodi is not playing
		labelIMDB = getInfoLabel("ListItem.IMDBNumber")
		item['year'] = getInfoLabel("ListItem.Year")
		item['season'] = getInfoLabel("ListItem.Season")
		item['episode'] = getInfoLabel("ListItem.Episode")
		item['file_original_path'] = ""
		labelType = getInfoLabel("ListItem.DBTYPE")  # movie/tvshow/season/episode
		isItMovie = labelType == 'movie' or getCondVisibility("Container.Content(movies)")
		isItEpisode = labelType == 'episode' or getCondVisibility("Container.Content(episodes)")

		if isItMovie:
			item['title'] = getInfoLabel("ListItem.OriginalTitle")
		elif isItEpisode:
			item['title'] = getTVshowOriginalTitleByTMDBapi('notPlaying') #getInfoLabel("ListItem.TVShowTitle")
		else:
			item['title'] = "SearchFor..."  # In order to show "No Subtitles Found" result.
	
	wlog("item:%s" % item)
	imdb_id = 0
	try:
		if Player().isPlaying():	# Enable using subtitles search dialog when kodi is not playing
			playerid_query = '{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
			playerid = loads(executeJSONRPC(playerid_query))['result'][0]['playerid']
			imdb_id_query = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": {"playerid": ' + \
				str(playerid) + ', "properties": ["imdbnumber"]}, "id": 1}'
			imdb_id = loads(executeJSONRPC(imdb_id_query))['result']['item']['imdbnumber']
			wlog("imdb JSONPC:%s" % imdb_id)
		else:
			if labelIMDB:
				imdb_id = labelIMDB
			else:
				if isItMovie:
					imdb_id = "ThisIsMovie"  # Search the movie by item['title'] for imdb_id
				elif isItEpisode:
					imdb_id = "ThisIsEpisode"  # Search by item['title'] for tvdb_id
				else:
					imdb_id = "tt0"  # In order to show "No Subtitles Found" result => Doesn't recognize movie/episode
	except Exception as err:
		wlog('Caught Exception: error in imdb id: %s' % format(err))		
		pass

	if imdb_id[:2] == "tt":  # Simple IMDB_ID
		searchByIMDB(imdb_id, item['season'], item['episode'], item['file_original_path'])
	else:
		# Search TV Show by Title
		if item['season'] or item['episode']:
			try:
				item['show'] = item['title']
				imdb_id = searchTMDB("tv",quote(item['title']),0)
				wlog("Search TV [IMDB %s] [%s]" % (imdb_id, item['title']))
				if imdb_id[:2] == "tt":
					searchByIMDB(imdb_id, item['season'], item['episode'], item['file_original_path'])
			except Exception as err:
				wlog('Caught Exception: error in tv search: %s' % format(err))
				pass
		# Search Movie by Title+Year
		else:
			try:
				imdb_id = searchTMDB("movie",query=item['title'], year=item['year'])
				wlog("Search IMDB:%s" % imdb_id)
				if not imdb_id[:2] == "tt":
					imdb_id = searchTMDB("movie",query=item['title'], year=(int(item['year'])-1))
					wlog("Search IMDB(2):%s" % imdb_id)
				if imdb_id[:2] == "tt":
					searchByIMDB(imdb_id, 0, 0, item['file_original_path'])
			except Exception as err:
				wlog('Caught Exception: error in movie search: %s' % format(err))
				pass

	# Search Local File
	if not imdb_id:
		ManualSearch(item['title'])
	endOfDirectory(int(sys.argv[1]))
	if myAddon.getSetting("Debug") == "true":
		if imdb_id[:2] == "tt":
			Dialog().ok("Debug "+myVersion, str(item), "imdb: "+str(imdb_id))
		else:
			Dialog().ok("Debug "+myVersion, str(item), "NO IDS")

elif action == 'manualsearch':
	searchstring = getParam("searchstring", params)
	ManualSearch(searchstring)
	endOfDirectory(int(sys.argv[1]))

elif action == 'download':
	id = getParam("id", params)
	wlog("Download ID:%s" % id)
	subs = download(id)
	for sub in subs:
		listitem = ListItem(label=sub)
		addDirectoryItem(handle=int(sys.argv[1]), url=sub, listitem=listitem, isFolder=False)
	endOfDirectory(int(sys.argv[1]))
	Ap = 0

	# Upload AP
	try:
		if Player().isPlaying() and urlparse(Player().getPlayingFile()).hostname[-11:]=="tvnow.best": #"tv4.live"
			Ap = 1
	except:
		pass

	if Ap==1 and myAddon.getSetting("uploadAP") == "true":
		try:
			response = get("https://subs2.apollogroup.tv/kodi.upload.php?status=1&imdb=%s&season=%s&episode=%s"%(getParam("imdb", params),getParam("season", params),getParam("episode", params)))
			ap_object = loads(response.text)["result"]
			if "Hebrew" not in ap_object["lang"]:
				xbmc.sleep(30*1000)
				i = Dialog().yesno("Apollo Upload Subtitle","Media version %s"%ap_object["version"],"This subtitle is 100% sync and match?")
				if i == 1:
					response = get("https://subs2.apollogroup.tv/kodi.upload.php?upload=1&lang=he&subid=%s&imdb=%s&season=%s&episode=%s"%(getParam("id", params),getParam("imdb", params),getParam("season", params),getParam("episode", params)))
					ap_upload = loads(response.text)["result"]
					if "error" in ap_upload:
						Dialog().ok("Apollo Error","%s"%ap_upload["error"])
					else:
						Dialog().ok("Apollo","Sub uploaded. Thank you!")
		except:
			pass

elif action == 'clean':
	try:
		rmtree(myTmp)
	except Exception as err:
		wlog('Caught Exception: deleting tmp dir: %s' % format(err))
		pass
	executebuiltin((u'Notification(%s,%s)' % (myName, myLang(32004))))
