# -*- coding: utf-8 -*-
import xbmc
import sys, re
import resources.lib.common as common

module = '14tv'
moduleIcon = common.GetIconFullPath("14tv.png")
baseUrl = 'https://www.now14.co.il'

def GetCategoriesList(iconimage):
	sortString = common.GetLocaleString(30002) if sortBy == 0 else common.GetLocaleString(30003)
	name = "{0}: {1}".format(common.GetLocaleString(30001), sortString)
	common.addDir(name, "toggleSortingMethod", 4, iconimage, {"Title": name, "Plot": "{0}[CR]{1}[CR]{2} / {3}".format(name, common.GetLocaleString(30004), common.GetLocaleString(30002), common.GetLocaleString(30003))}, module=module, isFolder=False)
	name = common.GetLabelColor("כל התכניות", bold=True, color="none")
	common.addDir(name, '', 0, iconimage, infos={"Title": name, "Plot": "צפיה בתכניות ערוץ 14 עכשיו"}, module=module)

def GetSeriesList(iconimage):
	#text = common.OpenURL(baseUrl)
	text = common.OpenURL('{0}/tochniot_haarutz/%D7%94%D7%9E%D7%94%D7%93%D7%95%D7%A8%D7%94-%D7%94%D7%9E%D7%A8%D7%9B%D7%96%D7%99%D7%AA/'.format(baseUrl))
	match = re.compile 	('<main class="content vod-content">(.*?)<!-- End Up Section -->', re.S).findall(text)
	match = re.compile('<div class="mySlides fade">.*?<a href="(.*?)".*?src="\s*(.*?)".*?class="tochnit_name">(.*?)<', re.S).findall(match[0])
	grids_arr = []
	for link, iconimage, name in match:
		iconimage = GetQuoteUrl(iconimage)
		#name = common.unquote(common.encode(link[link.rfind('/')+1:], 'utf-8'))
		name = common.GetLabelColor(common.UnEscapeXML(name.replace('-', ' ')), keyColor="prColor", bold=True)
		if iconimage.startswith('http') == False:
			iconimage = '{0}{1}'.format(baseUrl, iconimage)
		grids_arr.append((name, '{0}{1}'.format(baseUrl, link), iconimage, {"Title": name}))
	grids_sorted = grids_arr if sortBy == 0 else sorted(grids_arr,key=lambda grids_arr: grids_arr[0])
	for name, link, image, infos in grids_sorted:
		common.addDir(name, link, 1, common.encode(image, 'utf-8'), infos=infos, module=module)

def GetQuoteUrl(url):
	b = url.rfind('/')
	e = url.rfind(".")
	n = url[b+1:e]
	url = url[:b+1] + common.quote(common.encode(n, 'utf-8')) + url[e:]
	return url

def GetEpisodesList(url, image):
	bitrate = common.GetAddonSetting('{0}_res'.format(module))
	text = common.OpenURL(url)
	episodes = re.compile('<div class="katan-unit(.*?)</div>\s*</div>\s*</div>', re.S).findall(text)
	for episode in episodes:
		match = re.compile('data-videoid="(.*?)".*?src=["\'](.*?)["\'].*?<div class="the-title">(.*?)</div>.*?<div class="episode_air_date"\s*?>(.*?)</div>', re.S).findall(episode)
		for videoid, iconimage, name, date in match:
			name = common.GetLabelColor('{0} - {1}'.format(common.UnEscapeXML(name.strip()), date), keyColor="chColor")
			iconimage = GetQuoteUrl(iconimage)
			if iconimage.startswith('/'):
				iconimage = '{0}{1}'.format(baseUrl, iconimage)
			link = 'https://cdn.ch20-cdnwiz.com/ch20/player.php?clipid={0}&autoplay=true&automute=false'.format(videoid.strip())
			common.addDir(name, link, 2, iconimage, infos={"Title": name, "Aired": date}, contextMenu=[(common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode=2&iconimage={3}&moredata=choose&module={4})'.format(sys.argv[0], common.quote_plus(link), name, common.quote_plus(iconimage), module)), (common.GetLocaleString(30023), 'RunPlugin({0}?url={1}&name={2}&mode=2&iconimage={3}&moredata=set_14tv_res&module={4})'.format(sys.argv[0], common.quote_plus(link), name, common.quote_plus(iconimage), module))], module=module, moreData=bitrate, isFolder=False, isPlayable=True)

def Play(name, url, iconimage, quality='best', live=None):
	userAgent = common.GetUserAgent()
	headers = {"User-Agent": userAgent}
	text = common.OpenURL(url, headers=headers)
	match = re.compile('src:\s*"(.*?)"').findall(text)
	if len(match) < 0:
		match = re.compile('source\s*src="(.*?)"').findall(text)
	if len(match) < 0:
		match = re.compile("hls.loadSource\('(.*?)'\)").findall(text)
	if len(match) < 0 and live is not None:
		match = [live]
	link = common.GetRedirect(match[0], headers=headers)
	if link is None:
		link = match[0]
	if not link.endswith('.mp4'):
		link = common.GetStreams(link, headers=headers, quality=quality)
	final = '{0}|User-Agent={1}'.format(link, userAgent)
	common.PlayStream(final, quality, name, iconimage)

def Watch(name, iconimage, quality='best'):
	url = '{0}/tochniot_meleot/%D7%A9%D7%99%D7%93%D7%95%D7%A8-%D7%97%D7%99/'.format(baseUrl)
	text = common.OpenURL(url, headers={"User-Agent": common.GetUserAgent()})
	match = re.compile('<div id="cdnwizPlayerWrapper.*?<iframe.*?src="(.*?)"', re.S).findall(text)
	Play(name, match[0], iconimage, quality, live='https://dvr.ch20-cdnwiz.com/hls/live.m3u8')

def Run(name, url, mode, iconimage='', moreData=''):
	global sortBy
	sortBy = int(common.GetAddonSetting('{0}SortBy'.format(module)))
	
	if mode == -1:
		GetCategoriesList(moduleIcon)
	if mode == 0:		#------------- Series: ---------------
		GetSeriesList(moduleIcon)
	elif mode == 1:		#------------- Episodes: -----------------
		GetEpisodesList(url, iconimage)
	elif mode == 2:		#------------- Playing episode  ----------
		Play(name, url, iconimage, moreData)
	elif mode == 3:		#--- Move to a specific episodes' page  --
		url, pages = url.split('?pages=')
		page = common.GetIndexFromUser(name, pages)
		if page > 1: 
			url = '{0}page/{1}/'.format(url, page)
		GetEpisodesList(url, iconimage)
	elif mode == 4:		#------------- Toggle Lists' sorting method -----
		common.ToggleSortMethod('14tvSortBy', sortBy)
	elif mode == 10:	#------------- Watch live channel  -------
		Watch(name, iconimage, moreData)
		
	common.SetViewMode('episodes')
