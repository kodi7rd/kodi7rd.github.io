
import xbmcaddon,os,xbmc,xbmcgui,urllib,re,xbmcplugin,sys,logging,json,contextlib,zipfile
try:
    from urllib import urlretrieve
except:
    from urllib.request import urlretrieve
from os import path
MyAddon = xbmcaddon.Addon()
MyScriptID = MyAddon.getAddonInfo('id')
__USERAGENT__ = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11'
from xbmcaddon import Addon
from xbmcvfs import listdir, exists, mkdirs

MyAddon = Addon()
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
if KODI_VERSION<=18:
    xbmc_tranlate_path=xbmc.translatePath
else:
    import xbmcvfs
    xbmc_tranlate_path=xbmcvfs.translatePath
    
__profile__ = (xbmc_tranlate_path(MyAddon.getAddonInfo('profile')))
MyTmp = (xbmc_tranlate_path(os.path.join(__profile__, 'temp_wizdom')))
MySubFolder = xbmc_tranlate_path(path.join(MyTmp, 'subs')).encode('utf-8')
import socket
socket.setdefaulttimeout(30)
def read_html(url_link):
    socket.setdefaulttimeout(30)

    req = urllib2.Request(url_link)
    req.add_header('User-agent',__USERAGENT__)# 'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30')
    html = urllib2.urlopen(req).read()
    xbmc.sleep(100)
    return html
def convert_to_utf(file):
	try:
		with codecs.open(file, "r", "cp1255") as f:
			srt_data = f.read()

		with codecs.open(file, 'w', 'utf-8') as output:
			output.write(srt_data)
	except: pass
def download(id,mode_subtitle):
		socket.setdefaulttimeout(30)


		try:
			rmtree(MyTmp)
		except: pass
		mkdirs(MyTmp)
		try:
			rmtree(MySubFolder)
		except: pass
		mkdirs(MySubFolder)



		subtitle_list = []
		exts = [".srt", ".sub", ".str"]
	
		if 'yify$$$' in id:
			archive_file = path.join(MyTmp, 'yify.sub.'+id.replace('yify$$$','').replace('/subtitles/','')+'.zip')
			
			
			if not path.exists(archive_file):
				urlretrieve("https://yifysubtitles.me/subtitle/"+id.replace('yify$$$','').replace('/subtitles/','')+".zip", archive_file)


		#executebuiltin(('XBMC.Extract("%s","%s")' % (archive_file, MySubFolder)).encode('utf-8'), True)
		with contextlib.closing(zipfile.ZipFile(archive_file , "r")) as z:
			z.extractall(MySubFolder)
		for file_ in listdir(MySubFolder)[1]:
			ufile = file_.decode('utf-8')
			file_ = path.join(MySubFolder, ufile)
			if path.splitext(ufile)[1] in exts:
				convert_to_utf(file_)
				subtitle_list.append(file_)

		if mode_subtitle>1:
		  return subtitle_list," "
		else:
		 if len (subtitle_list)>0:
		   sub_result=subtitle_list[0]
		 else:
		   sub_result='0'
		 #xbmc.Player().setSubtitles(subtitle_list[0])
		 return True,sub_result


def get_imdb_subtitles(imdb_id,counter,mode_subtitle):
     socket.setdefaulttimeout(30)

     url = 'https://yifysubtitles.me/movie-imdb/'+imdb_id
     html=read_html(url)
     regex='<td class="rating-cell"><span class="label">(.+?)</span></td><td class="flag-cell"><span class="flag flag-il"></span><span class="sub-lang">(.+?)</span></td><td><a href="(.+?)"><span class="text-muted">subtitle</span>(.+?)<'
     match=re.compile(regex).findall(html)
     subtitle_list=[]
     subs_id=''
     subtitle=''
     for rating,lang,link,name in match:

         if lang=='Hebrew':
              lang_flag='he'
         elif lang=='English':
              lang_flag='eng'
         subs_id=link.split('//')[-1]+'yify$$$'
         json_data={'url': "plugin://%s/?action=download&versioname=%s&id=%s" % (MyScriptID, '999', subs_id),
                 'label':lang,
                 'label2':'[COLOR lightcoral]'+str(counter)+'. '+name+'[/COLOR]',
                 'iconImage':'',
                 'thumbnailImage':lang_flag,
                 'hearing_imp':"false",
                 'sync': "false"}
                  
         if mode_subtitle<2:
          subtitle_list.append(json_data)
          ok,subtitle=download(subs_id,mode_subtitle)

          return subtitle_list,counter,'STOP',subtitle
         counter=counter+1
         subtitle_list.append(json_data)
     return subtitle_list,counter,subs_id,subtitle
def search_yify(item,imdb_id,mode_subtitle):
   socket.setdefaulttimeout(30)

   subtitle_list=[]
   counter=0
   subtitle=''
   if 'tt' in imdb_id:
     subtitle_list,counter,subs_id,subtitle=get_imdb_subtitles(imdb_id,counter,mode_subtitle)
     return len(subtitle_list),subtitle,subtitle_list
   else:
     url='https://yifysubtitles.me/front/search?Search='+urllib.quote_plus(str(item['title']))
     html=read_html(url)
     json_data=json.loads(html)

     for part in json_data:
       
       subtitle_list2,counter,subs_id,subtitle=(get_imdb_subtitles(part['imdb'],counter,mode_subtitle))
       

       for sub in subtitle_list2:
         
         subtitle_list.append(sub)

       if subs_id=='STOP':
          break
     return len(subtitle_list),subtitle,subtitle_list
    