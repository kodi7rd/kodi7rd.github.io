import xbmcaddon
global global_var,stop_all,site_id,sub_color#global
global_var=[]
from resources.modules import log
import requests,json,re
from resources.modules import cache
import xbmcvfs
import zipfile
import shutil,os
from urllib.request import urlretrieve
from resources.modules.extract_sub import extract
import urllib
import urllib.parse

que=urllib.parse.quote_plus
Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')

xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_wizdom'))



site_id='[Wiz]'
sub_color='white'

def get_subs(item):
    global global_var
    log.warning('Searching Wizdom')
    imdb=item['imdb']
    season=item['season']
    episode=item['episode']
    title=item['OriginalTitle']
    url = "http://wizdom.xyz/api/search?action=by_id&imdb=%s&season=%s&episode=%s&version=%s" % (imdb, season, episode, title)
    try:
      x=requests.get(url).json()
    except:
      x={}
      pass
    json_object = x
    
    subs_rate = []
    subtitle=' '
    x=0
    id_all_collection=[]
    subtitle_list=[]
    if json_object!=0:
        for item_data in json_object:
            download_data={}
            download_data['id']=item_data["id"]
            url = "plugin://%s/?action=download&filename=%s&id=%s&download_data=%s&source=wizdom&language=Hebrew" % (
                    MyScriptID, que(item_data["versioname"]), item_data["id"],que(json.dumps(download_data)))
          
            json_data={'url':url,
                             'label':"Hebrew",
                             'label2':site_id+item_data["versioname"],
                             'iconImage':"%s"%(item_data["score"]/2),
                             'thumbnailImage':"he",
                             'hearing_imp':'false',
                             'site_id':site_id,
                             'sub_color':sub_color,
                             'filename':item_data["versioname"],
                             'sync': 'false'}
            if item_data["id"] not in id_all_collection:
                id_all_collection.append(item_data["id"])
          
                
                subtitle_list.append(json_data)
                links_wizdom=subtitle_list
                x=x+1
                global_var=subtitle_list
def download(download_data,MySubFolder):
    
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)
    id=str(download_data['id'])
    archive_file = os.path.join(MyTmp, 'wizdom.sub.'+id+'.zip')
    
  
    urlretrieve("http://wizdom.xyz/api/files/sub/"+id, archive_file)
    
    
    sub_file=extract(archive_file,MySubFolder)
    return sub_file