



import os,time
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import threading
from urllib.parse import  unquote_plus, unquote,  quote
from resources.modules import log

iconx=xbmcaddon.Addon().getAddonInfo('icon')
xbmc_tranlate_path=xbmcvfs.translatePath
user_dataDir = xbmc_tranlate_path(xbmcaddon.Addon().getAddonInfo("profile"))
if not os.path.exists(user_dataDir):
     os.makedirs(user_dataDir)
CachedSubFolder=xbmc_tranlate_path(os.path.join(user_dataDir, 'Cached_subs'))
if not os.path.exists(CachedSubFolder):
     os.makedirs(CachedSubFolder)
MySubFolder = xbmc_tranlate_path(os.path.join(user_dataDir, 'Downloaded_subs'))
MyScriptID = xbmcaddon.Addon().getAddonInfo('id')
TransFolder=xbmc_tranlate_path(os.path.join(user_dataDir, 'trans_subs'))
if not os.path.exists(TransFolder):
     os.makedirs(TransFolder)
MyScriptName = xbmcaddon.Addon().getAddonInfo('name')
addonPath = xbmc_tranlate_path(xbmcaddon.Addon().getAddonInfo("path"))
global with_dp,show_msg,progress_msg
show_msg=""
progress_msg=0
global break_all
break_all=False
with_dp=True
class OverlayText:
    def __init__(self):
        log.warning('(Overlay) Initialize overlay text')
        x, y, w, h,x2, y2, w2, h2,x3, y3, w3, h3 = self._calculate_the_size()

        self._shown       = False
        self._window     = xbmcgui.Window(12005)
        self._label      = xbmcgui.ControlLabel(x, y, w, h, '', alignment=0x00000002 | 0x00000004, font='font14')
        
        
        self._icon = xbmcgui.ControlImage(x2, y2, w2, h2, iconx)
        self._background = xbmcgui.ControlImage(x3, y3, w3, h3, os.path.join(addonPath,"resources","art","background.png"))
        self._background.setColorDiffuse("0xD0000000")

    def __enter__(self):
        return self

    def open(self):
        if not self._shown:
            self._window.addControls([self._background,self._icon, self._label])
            self._shown = True

    def isShowing(self):
        return self._shown

    def setText(self, text):
        if self._shown:
            self._label.setLabel(text)

    def _calculate_the_size(self):
        # get skin resolution
        #tree = ET.parse(os.path.join(xbmc_tranlate_path("special://skin/"), "addon.xml"))
        #res = tree.findall("./extension/res")[0]
        viewport_w =1920 #int(res.attrib["width"])
        viewport_h =1080 #int(res.attrib["height"])
        # Adjust size based on viewport, we are using 1080p coordinates
        
        
        # label
        w = int(int(1920.0 * 0.7) * viewport_w / 1920.0)
        h = int(150 * viewport_h / 1088.0)
        x = int((viewport_w - w) / 2)
        y = int(10)
        
        # icon
        w2 = 95#int(int(20.0 * 0.7) * viewport_w / 20.0)
        h2 = int(95 * viewport_h / 1088.0)
        x2 = 570
        y2 = int(30)
        
        # background
        w3 = 800#int(int(20.0 * 0.7) * viewport_w / 20.0)
        h3 = int(100 * viewport_h / 1088.0)
        x3 = 540
        y3 = int(30)
        
        
        return x, y, w, h,x2, y2, w2, h2,x3, y3, w3, h3

    def __exit__(self, *exc_info):
        self.close()
        return not exc_info[0]

    def __del__(self):
        self.close()

    def close(self):
        if hasattr(self, '_icon') and self._shown:
            self._window.removeControls([self._background,self._icon, self._label])
            self._shown = False


class Thread (threading.Thread):
   def __init__(self, target, *args):
    super().__init__(target=target, args=args)
   def run(self, *args):
      
      self._target(*self._args)
      return 0
   def exit(self):
        SystemExit()
def show_results(show_dp=True):
    global break_all,progress_msg
    
    from resources.modules.general import with_dp
    show_dp=with_dp
    break_all=False
    log.warning('show_dp:'+str(show_dp))
    time_out=0
    if (show_dp):
        dp = xbmcgui.DialogProgress()
        dp.create("מחפש כתוביות")
                      
        while(1):
            from resources.modules.general import show_msg
            if (show_msg!="END"):
                dp.update(progress_msg,str(show_msg))
            if dp.iscanceled():
                break_all=True
                dp.close()
                break
            if (show_msg=="END"):
                break_all=True
                dp.close()
                break
            time.sleep(0.1)
            time_out+=1
            if (time_out>600):
                break_all=True
                dp.close()
                break
        dp.close()
        '''
        menu2 = infoDialog("plugin://%s/"%addon_id)
        menu2.doModal()
        del menu2
        '''
    else:
        try:
            cond=xbmc.Monitor().abortRequested()
        except:
            cond=xbmc.abortRequested
        log.warning(cond)
        close_overlay=False
        with OverlayText() as _overlay:
          
          while (not cond) and (xbmc.Player().isPlaying()):
            from resources.modules.general import show_msg
            _overlay.open()
            if close_overlay:
              break
             
                
             
                
            if _overlay.isShowing():
                if (show_msg!="END"):
                    _overlay.setText(show_msg)

            time.sleep(0.1)
            if (show_msg=="END"):
                close_overlay=True
                _overlay.close()
                
def notify(msg_id, times=500, icon=iconx,sound=False):
        xbmcgui.Dialog().notification(MyScriptName, msg_id, icon, int(times), sound)
        

def take_title_from_focused_item():
    labelType = xbmc.getInfoLabel("ListItem.DBTYPE")  # movie/tvshow/season/episode
    labelMovieTitle = xbmc.getInfoLabel("ListItem.OriginalTitle")
    labelYear = xbmc.getInfoLabel("ListItem.Year")
    labelTVShowTitle = xbmc.getInfoLabel("ListItem.TVShowTitle")
    labelSeason = xbmc.getInfoLabel("ListItem.Season")
    labelEpisode = xbmc.getInfoLabel("ListItem.Episode")
    isItMovie = xbmc.getCondVisibility("Container.Content(movies)") or labelType == 'movie'
    isItEpisode = xbmc.getCondVisibility("Container.Content(episodes)") or labelType == 'episode'

    title = 'SearchFor...'
    if isItMovie and labelMovieTitle and labelYear:
        title = labelMovieTitle + " " + labelYear
    elif isItEpisode and labelTVShowTitle and labelSeason and labelEpisode:
        title = ("%s S%.2dE%.2d" % (labelTVShowTitle, int(labelSeason), int(labelEpisode)))

    return title
def clean_name(name):

  
      return name.lower().replace('%20',' ').replace('%3a',':').replace('%27',"'").replace('  ',' ')

def get_video_data():
    

    
    
    video_data={}
    if xbmc.Player().isPlaying():
        
        video_data['title']=xbmc.getInfoLabel("VideoPlayer.Title")
        video_data['OriginalTitle']=xbmc.getInfoLabel("VideoPlayer.OriginalTitle")
        tag_fen=xbmcgui.Window(10000).getProperty("subs.player_filename")
        log.warning('tag_fen:'+tag_fen)
        video_data['Tagline']=xbmc.getInfoLabel("VideoPlayer.Tagline")
        if tag_fen!="":
            video_data['Tagline']=tag_fen
        
        video_data['UniqueID']=xbmc.getInfoLabel("VideoPlayer.UniqueID(imdb)")
        video_data['IMDBNumber']=xbmc.getInfoLabel("VideoPlayer.IMDBNumber")
        video_data['year']=xbmc.getInfoLabel("VideoPlayer.Year")
        video_data['TVshowtitle']=xbmc.getInfoLabel("VideoPlayer.TVshowtitle")
        video_data['season']=xbmc.getInfoLabel("VideoPlayer.Season")
        if video_data['season']=='' or str(video_data['season'])=='0':
            video_data['season']=0
        video_data['episode']=xbmc.getInfoLabel("VideoPlayer.Episode")
        if video_data['episode']=='' or str(video_data['episode'])=='0':
            video_data['episode']=0
            
        if 'tt' in video_data['UniqueID']:
            video_data['imdb']=video_data['UniqueID']
        else:
            video_data['imdb']=video_data['IMDBNumber']
        
        
        video_data['file_original_path'] = unquote((xbmc.Player().getPlayingFile()))  # Full path of a playing file
        video_data['file_original_path'] = video_data['file_original_path'].split("?")
        video_data['file_original_path'] = os.path.basename(video_data['file_original_path'][0])[:-4]
        video_data['mpaa']=xbmc.getInfoLabel("VideoPlayer.mpaa")
    else:
        log.warning('Xbmc NOT Playing')
        video_data['imdb'] = xbmc.getInfoLabel("ListItem.IMDBNumber")
        video_data['year'] = xbmc.getInfoLabel("ListItem.Year")
        video_data['season'] = xbmc.getInfoLabel("ListItem.Season")
        video_data['episode'] = xbmc.getInfoLabel("ListItem.Episode")
        
        

        
        if str(video_data['season'])=='' or str(video_data['season'])<str(1):
            video_data['season'] = 0


        if str(video_data['episode'])=='' or int(video_data['episode'])<1:
            video_data['episode'] = 0
        if str(video_data['season']) == '0' or str(video_data['episode']) == '0':
          video_data['tvshow'] =''

        else:
          video_data['tvshow'] =take_title_from_focused_item()
        
        video_data['title'] = take_title_from_focused_item().replace("%20"," ")

        
        
        labelType = xbmc.getInfoLabel("ListItem.DBTYPE")  #movie/tvshow/season/episode    
        isItMovie = labelType == 'movie' or xbmc.getCondVisibility("Container.Content(movies)")
        isItEpisode = labelType == 'episode' or xbmc.getCondVisibility("Container.Content(episodes)")

        if isItMovie:
            video_data['title'] = xbmc.getInfoLabel("ListItem.OriginalTitle").replace("%20"," ")
        elif isItEpisode:
            video_data['title'] = xbmc.getInfoLabel("ListItem.TVShowTitle").replace("%20"," ")  
        video_data['file_original_path'] =video_data['title']
        video_data['OriginalTitle']=video_data['title']
        video_data['TVshowtitle']=video_data['tvshow']
        video_data['Tagline']=video_data['title']
        video_data['mpaa']=""
    video_data['title']=clean_name(video_data['title'])
    video_data['OriginalTitle']=clean_name(video_data['OriginalTitle'])
    
    return video_data
def save_file_name(filename):
    try:
        from sqlite3 import dbapi2 as database
    except:
        from pysqlite2 import dbapi2 as database
    cacheFile=os.path.join(user_dataDir,'database.db')
    dbcon = database.connect(cacheFile)
    dbcur = dbcon.cursor()
    dbcur.execute("CREATE TABLE IF NOT EXISTS %s ( ""name TEXT );" % ('list_sub'))

    dbcur.execute("SELECT * FROM list_sub ")
    list_sub = dbcur.fetchall()
    if filename not in list_sub :         
         dbcur.execute("INSERT INTO list_sub Values ('%s')"%(filename))
    dbcon.commit()
    dbcon.close()
def get_db_data(f_result):
    try:
      from sqlite3 import dbapi2 as database
    except:
      from pysqlite2 import dbapi2 as database
    cacheFile=os.path.join(user_dataDir,'database.db')
    dbcon = database.connect(cacheFile)
    dbcur = dbcon.cursor()
    dbcur.execute("CREATE TABLE IF NOT EXISTS %s ( ""name TEXT );" % ('list_sub'))
    dbcur.execute("SELECT * FROM list_sub")
    list_sub = dbcur.fetchall()
    dbcur.close()
    dbcon.close()
    all_subs={}
    last_sub_index=''
    x=0
    for i in list_sub:
        all_subs[i[0]]=x
        x+=1
    max_index=0
    for items in f_result:
        
        c_sub_name=items[8]
        
        try:
            val=all_subs[c_sub_name]
            a_index=val
            if a_index>max_index:
                last_sub_index=c_sub_name
                max_index=a_index
        except:
            pass
    return last_sub_index,all_subs
    

