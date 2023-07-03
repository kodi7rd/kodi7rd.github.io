import xbmc,xbmcaddon,json,os
Addon=xbmcaddon.Addon()
from resources.modules import log
from resources.modules.engine import download_sub
from urllib.parse import parse_qsl
from resources.modules.general import user_dataDir,MySubFolder,save_file_name,get_db_data,Thread
import urllib.parse

unque=urllib.parse.unquote_plus

def MySubs(title,list,f_list,video_data,all_subs,last_sub_index):
    from  resources.modules import pyxbmct

    class MySubs(pyxbmct.AddonDialogWindow):
        
        def __init__(self, title,list,f_list,video_data,all_subs,last_sub_index):
        
            super(MySubs, self).__init__(title)
            self.list_o=list
            self.title=title
            try:
                self.start_time= xbmc.Player().getTime()
            except:
                self.start_time=0
            wd=int(Addon.getSetting("subs_width"))
            hd=int(Addon.getSetting("subs_hight"))
            px=int(Addon.getSetting("subs_px"))
            py=int(Addon.getSetting("subs_py"))
            self.full_list=f_list
            log.warning(video_data)
            self.video_data=video_data
            self.setGeometry(wd, hd, 9, 1,pos_x=px, pos_y=py)
            
            ############KODI-RD-IL###################
            self.total_subs_count=len(f_list)
            #########################################
            
            self.all_subs=all_subs
            self.last_sub_index=last_sub_index
            self.set_info_controls()
            self.set_active_controls()
            self.set_navigation()
            self.close_window=False
            # Connect a key action (Backspace) to close the window.
            self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
            Thread(target=self.background_task).start()
        def background_task(self):
            while (self.close_window==False):
                from resources.modules import general
                if 'מתרגם' in general.show_msg:
                    self.label_info.setLabel(general.show_msg +' - '+ str(general.progress_msg))
                xbmc.sleep(500)
        def set_info_controls(self):
        
            ############KODI-RD-IL###################
            # File Name Label
            self.video_file_name_label = f"[B][COLOR yellow]{self.video_data['Tagline']}[/COLOR][/B]"
            self.label_info = pyxbmct.Label(self.video_file_name_label)
            self.placeControl(self.label_info,  0, 0, 1, 1)

            # Total Subtitles Count Label
            self.label = pyxbmct.Label(f"[B]{str(self.total_subs_count)} כתוביות נמצאו[/B]")
            self.placeControl(self.label,  7, 0, 3, 1)
            #########################################
            
            self.list = pyxbmct.List()
            self.placeControl(self.list, 1, 0, 7, 1)
            self.connect(self.list, self.click_list)
            
            self.button = pyxbmct.Button('[B]סגור[/B]')
            self.placeControl(self.button, 8, 0)
            # Connect control to close the window.
            self.connect(self.button, self.click_c)
            
            
            
        def get_params(self,url):

            param = dict(parse_qsl(url.replace('?','')))
            return param
        def click_list(self):
            global list_index


            list_index=self.list.getSelectedPosition()
            log.warning(self.full_list[list_index])
            log.warning('list_index:'+str(list_index))
            self.label_info.setLabel('מוריד' + ' | ' + self.video_file_name_label)
            params=self.get_params(self.full_list[list_index][4])
            download_data=unque(params["download_data"])
            download_data=json.loads(download_data)
            source=(params["source"])
            language=(params["language"])
            filename=(params["filename"])
            fault_sub=False
            try:
                sub_file=download_sub(source,download_data,MySubFolder,language,filename)
                xbmc.sleep(100)
                xbmc.Player().setSubtitles(sub_file)
                log.warning('My Window Sub result:'+str(sub_file))
            
            except:
                fault_sub=True
            
            
            
            if fault_sub:
                self.label_info.setLabel('תקלה בהורדה בחר אחרת' + ' | ' + self.video_file_name_label)
            else:
                self.label_info.setLabel('מוכן' + ' | ' + self.video_file_name_label)
                save_file_name(params["filename"])
                self.last_sub_index,self.all_subs=get_db_data(self.full_list)
                self.set_active_controls()
                from resources.modules import general
                general.show_msg="END"
                
        def click_c(self):
            global list_index
            
            list_index=888
            current_list_item=''
            self.close_window=True
            self.close()
        def set_active_controls(self):
         
            self.list.reset()
            # List
            
            
            # Add items to the list
            
            n_items=[]
       
            for items in self.list_o:
                try:
                    val=self.all_subs[items[8]]
                  
                except:
                    val=None
                    pass
                
                if (self.last_sub_index==items[8]):
                    added_string='[COLOR yellow][B][I]SELECTED >> '
                elif val:
                    added_string='[COLOR deepskyblue][B][I]'
                else:
                    added_string='[COLOR gold]'
                sub_name=added_string+str(items[5])+ "% "+'[/COLOR]'+items[1]
                
                if ('[B][I]' in added_string):
                    sub_name=sub_name+'[/I][/B]'
                if self.video_data['file_original_path'].replace("."," ").lower() in items[1].replace("."," ").lower() and len(self.video_data['file_original_path'].replace("."," "))>5 or items[5]>80:
                        
                    sub_name='[COLOR gold] GOLD [B]'+sub_name+'[/B][/COLOR]'
                n_items.append(items[3]+' ' +sub_name)
              
              
            self.list.addItems(n_items)
            # Connect the list to a function to display which list item is selected.
            
            
            # Connect key and mouse events for list navigation feedback.
            
         
            
            

        def set_navigation(self):
            # Set navigation between controls
            
            self.list.controlDown(self.button)
            self.list.controlRight(self.button)
            self.list.controlLeft(self.button)
            self.button.controlUp(self.list)
            self.button.controlDown(self.list)
            # Set initial focus
            self.setFocus(self.list)

        def slider_update(self):
            # Update slider value label when the slider nib moves
            try:
                if self.getFocus() == self.slider:
                    self.slider_value.setLabel('{:.1F}'.format(self.slider.getPercent()))
            except (RuntimeError, SystemError):
                pass

        def radio_update(self):
            # Update radiobutton caption on toggle
            if self.radiobutton.isSelected():
                self.radiobutton.setLabel('On')
            else:
                self.radiobutton.setLabel('Off')

   

        def setAnimation(self, control):
            # Set fade animation for all add-on window controls
           
            
            control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=100',),
                                    ('WindowClose', 'effect=fade start=100 end=0 time=100',)])
    window = MySubs(title,list,f_list,video_data,all_subs,last_sub_index)
    window.doModal()

    del window