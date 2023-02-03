# -*- coding: utf-8 -*-
# Licence: GPL v.3 http://www.gnu.org/licenses/gpl.html
# This is an XBMC addon for demonstrating the capabilities
# and usage of PyXBMCt framework.

import os,shutil
import xbmc,xbmcgui
import xbmcaddon
import pyxbmct,logging
from xbmcgui import Dialog, WindowXMLDialog
from threading import Timer
import xml.etree.ElementTree as ET
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
if KODI_VERSION<=18:
    xbmc_tranlate_path=xbmc.translatePath
else:
    import xbmcvfs
    xbmc_tranlate_path=xbmcvfs.translatePath
 
_addon = xbmcaddon.Addon(id='script.subskeys')
_addon_path = _addon.getAddonInfo('path')

default = xbmc_tranlate_path('special://xbmc/system/keymaps/keyboard.xml')
userdata = xbmc_tranlate_path('special://userdata/keymaps/')
gen_file = os.path.join(userdata, 'gen.xml')

userkeymap=[]
defaultkeymap=[]
list_files=[]

userkeymap_list = 'ebs_custom_keyboard.xml'
if not os.path.exists(userdata):
    os.makedirs(userdata)
else:
  list_files=os.listdir(userdata)

i=0
for file in list_files:
  change_file=0
  with open(userdata+file, 'r') as xml:
    
    if '<keyboard>' in xml.read():
      change_file=1
  if change_file>0:
    logging.warning(file)
    if file.rpartition('.')[-1]=='xml' and file!=userkeymap_list:
      logging.warning(file)
      try:
           os.remove(userdata+"keyboard"+str(i)+'.old')
      except:
       pass
      shutil.copyfile(userdata+file,  userdata+"keyboard"+str(i)+'.old')
      if os.path.exists(userdata+userkeymap_list):
        os.rename(userdata+userkeymap_list, userdata+'ebs_keyboard.old' )
      os.rename(userdata+file, userdata+userkeymap_list)

      i=i+1
        #userkeymap_list=file
    


def rpc(method, **params):
    params = json.dumps(params)
    query = '{"jsonrpc": "2.0", "method": "%s", "params": %s, "id": 1}' % (method, params)
    return json.loads(xbmc.executeJSONRPC(query))

def read_keymap(filename):
    ret = []
    logging.warning('filename:'+filename)
    with open(filename, 'r') as xml:
        tree = ET.iterparse(xml)
        for _, keymap in tree:
            for context in keymap:
                for device in context:
                    for mapping in device:
                        key = mapping.get('id') or mapping.tag
                        action = mapping.text
                        if action:
                            ret.append((context.tag.lower(), action, key.lower()))
    return ret

def write_keymap(keymap, filename):
    contexts = list(set([c for c, a, k in keymap]))

    builder = ET.TreeBuilder()
    builder.start("keymap", {})
    for context in contexts:
        builder.start(context, {})
        builder.start("keyboard", {})
        for c, a, k in keymap:
            if c == context:
                builder.start("key", {"id":k})
                builder.data(a)
                builder.end("key")
        builder.end("keyboard")
        builder.end(context)
    builder.end("keymap")
    element = builder.close()
    ET.ElementTree(element).write(filename, 'utf-8')
    xbmc.sleep(1000)
    xbmc.executebuiltin('Action(reloadkeymaps)')
    #xbmcgui.Dialog(). ok('Exist in','DONE')
    #MyAddon('PyXBMCt Demo')
# Enable or disable Estuary-based design explicitly
# pyxbmct.skin.estuary = True



       
                    

def check_if_key_in_use(key,newkey):
    choise=True
    defaultkeymap = read_keymap(default)
    userkeymap=read_keymap(userdata+userkeymap_list)
    result=findItem(defaultkeymap, key)

    answer=''
#####key number check###
    for r in result:
      answer=answer+(defaultkeymap[int(r[0])][0]+'->'+defaultkeymap[int(r[0])][1])+'\n'
      
    result2=findItem(userkeymap, key)
    for r in result2:
      answer=answer+(userkeymap[int(r[0])][1])+'\n'
####key lower check####
    result=findItem(defaultkeymap, key.lower())
    logging.warning(result)

    for r in result:
      answer=answer+(defaultkeymap[int(r[0])][0]+'->'+defaultkeymap[int(r[0])][1])+'\n'
      
    result2=findItem(userkeymap, key.lower())
    for r in result2:
      answer=answer+(userkeymap[int(r[0])][1])+'\n'
      
      
#####new key check###
    result3=findItem(defaultkeymap, newkey)
    for r in result3:
      answer=answer+(defaultkeymap[int(r[0])][0]+'->'+defaultkeymap[int(r[0])][1])+'\n'
      
    result4=findItem(userkeymap, newkey)
    for r in result4:
      answer=answer+(userkeymap[int(r[0])][0]+'->'+userkeymap[int(r[0])][1])+'\n'
    if len(answer)>0:
      answer=answer+'[COLOR lightblue]Overwrite?[/COLOR]'
      choise=xbmcgui.Dialog(). yesno('Exist in',answer)
    return choise


class KeyListener(WindowXMLDialog):
    TIMEOUT = 5

    def __new__(cls):
        gui_api = tuple(map(int, xbmcaddon.Addon('xbmc.gui').getAddonInfo('version').split('.')))
        file_name = "DialogNotification.xml" if gui_api >= (5, 11, 0) else "DialogKaiToast.xml"
        return super(KeyListener, cls).__new__(cls, file_name, "")

    def __init__(self):
        self.key = None

    def onInit(self):
        try:
            self.getControl(401).addLabel(_addon.getLocalizedString(32001))#('Press the key you want to assign now')
            self.getControl(402).addLabel(_addon.getLocalizedString(32002))#('Timeout in %.0f seconds...' % self.TIMEOUT)
        except AttributeError:
            self.getControl(401).setLabel(_addon.getLocalizedString(32001))#'Press the key you want to assign now')
            self.getControl(402).setLabel(_addon.getLocalizedString(32002))#('Timeout in %.0f seconds...' % self.TIMEOUT)

    def onAction(self, action):
        code = action.getButtonCode()
        self.key = None if code == 0 else str(code)
        self.close()

    @staticmethod
    def record_key():
        dialog = KeyListener()
        timeout = Timer(KeyListener.TIMEOUT, dialog.close)
        timeout.start()
        dialog.doModal()
        timeout.cancel()
        key = dialog.key
        del dialog
        return key
class POPUPTEXT(pyxbmct.AddonDialogWindow):
    def __init__(self, title='',text=''):
        super(POPUPTEXT, self).__init__(title)
        self.setGeometry(1200, 700, 9, 4)
        self.text=text
        self.x=0
        self.set_active_controls()
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        #self.changelog.controlUp(lambda:self.scroll_up)
       
    def scroll_up(self):
       self.changelog.scroll(self.x)
       self.lines_count=sum(1 for line in self.text)

       if self.x<self.lines_count:
         self.x=self.x+1
    def scroll_down(self):
       self.changelog.scroll(self.x)
       if self.x>0:
         self.x=self.x-1
    def set_active_controls(self):
        self.changelog = pyxbmct.TextBox(font='Small')
        self.placeControl(self.changelog, 0, 0, 8, 8)
        self.changelog.setText(self.text)
        #self.changelog.autoScroll(delay=500, time=500, repeat=1000)
        self.connectEventList([pyxbmct.ACTION_MOVE_DOWN],
                              self.scroll_up)
        self.connectEventList([pyxbmct.ACTION_MOVE_UP],
                              self.scroll_down)
        # Button
        self.button5 = pyxbmct.Button('Close')
        self.placeControl(self.button5, 8, 2)
        # Connect control to close the window.
        self.connect(self.button5, self.close)
        
      
      
      
      
      
      
      
      
class MyAddon(pyxbmct.AddonDialogWindow):

    def __init__(self, title=''):
        super(MyAddon, self).__init__(title)
        self.setGeometry(700, 450, 9, 4)
        #self.set_info_controls()
        self.set_active_controls()
        self.set_navigation()
        self.nextbutton=0

        
        # Connect a key action (Backspace) to close the window.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
  
    def set_info_controls(self):
        # Demo for PyXBMCt UI controls.
        no_int_label = pyxbmct.Label('Information output', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(no_int_label, 0, 0, 1, 2)
        #
        label_label = pyxbmct.Label('Label')
        self.placeControl(label_label, 1, 0)
        # Label
        self.label = pyxbmct.Label('Simple label')
        self.placeControl(self.label, 1, 1)
        #
        fadelabel_label = pyxbmct.Label('FadeLabel')
        self.placeControl(fadelabel_label, 2, 0)
        # FadeLabel
        self.fade_label = pyxbmct.FadeLabel()
        self.placeControl(self.fade_label, 2, 1)
        self.fade_label.addLabel('Very long string can be here.')
        #
        textbox_label = pyxbmct.Label('TextBox')
        self.placeControl(textbox_label, 3, 0)
        # TextBox
        self.textbox = pyxbmct.TextBox()
        self.placeControl(self.textbox, 3, 1, 2, 1)
        self.textbox.setText('It can display long text.\n'
                             'Lorem ipsum dolor sit amet, consectetur adipiscing elit.')
        # Set auto-scrolling for long TexBox contents
        self.textbox.autoScroll(1000, 1000, 1000)
        #
        image_label = pyxbmct.Label('Image')
        self.placeControl(image_label, 5, 0)
        # Image
        self.image = pyxbmct.Image(os.path.join(_addon_path, 'bbb-splash.jpg'))
        self.placeControl(self.image, 5, 1, 2, 1)
    def convert_num_char(self,key):
       try:

        new_key=int(key)

        new_key=(chr(int(new_key)-61440))

        return new_key
       except:
        return key
    def setbutton(self,value,type):
      userkeymap=read_keymap(userdata+userkeymap_list)

      newkey = KeyListener.record_key()
      key=self.convert_num_char(newkey)
 
      choise=check_if_key_in_use(key,newkey)

      if choise==True:
        location=findItem(userkeymap,key)

        for loc in location:
            userkeymap.pop(loc[0])

            
        if type=='next':
          location=findItem(userkeymap,'RunScript(special://home/addons/script.subskeys/default.py,next)')
      
       
          for loc in location:
            userkeymap.pop(loc[0])
            
          userkeymap.append(('global', 'RunScript(special://home/addons/script.subskeys/default.py,next)', newkey))
          self.button2.setLabel(' [COLOR lightblue]'+key.lower()+'[/COLOR]'+_addon.getLocalizedString(32003))#('Set next Subtitle Button - [COLOR lightblue]'+key.lower()+'[/COLOR]')
          
        elif  type=='previous':
          location=findItem(userkeymap,'RunScript(special://home/addons/script.subskeys/default.py,previous)')
      
       
          for loc in location:
            userkeymap.pop(loc[0])
          userkeymap.append(('global', 'RunScript(special://home/addons/script.subskeys/default.py,previous)', newkey))
          self.button3.setLabel(' [COLOR lightblue]'+key.lower()+'[/COLOR]'+_addon.getLocalizedString(32004))#('Set previous Subtitle Button - [COLOR lightblue]'+key.lower()+'[/COLOR]')
        elif type=='open':
          location=findItem(userkeymap,'ActivateWindow(subtitlesearch)')

          for loc in location:
            userkeymap.pop(loc[0])
          userkeymap.append(('global', 'ActivateWindow(subtitlesearch)', newkey))
          self.button1.setLabel(' [COLOR lightblue]'+key.lower()+'[/COLOR]'+_addon.getLocalizedString(32005))#('Set OpenSubtitle Button - [COLOR lightblue]'+key.lower()+'[/COLOR]')
        
        elif type=='delay_p':
          location=findItem(userkeymap,'subtitledelayplus')

          for loc in location:
            userkeymap.pop(loc[0])
          userkeymap.append(('global', 'subtitledelayplus', newkey))
          self.button9.setLabel(' [COLOR lightblue]'+key.lower()+'[/COLOR]'+_addon.getLocalizedString(32006))#('Set Subtitle Delay Plus - [COLOR lightblue]'+key.lower()+'[/COLOR]')
        elif type=='delay_m':
          location=findItem(userkeymap,'subtitledelayminus')

          for loc in location:
            userkeymap.pop(loc[0])
          userkeymap.append(('global', 'subtitledelayminus', newkey))
          self.button10.setLabel(' [COLOR lightblue]'+key.lower()+'[/COLOR]'+_addon.getLocalizedString(32007))#('Set Subtitle Delay Minus - [COLOR lightblue]'+key.lower()+'[/COLOR]')
        elif type=='background':
          location=findItem(userkeymap,'RunScript(special://home/addons/script.subskeys/default.py,background)')
      
       
          for loc in location:
            userkeymap.pop(loc[0])
            
          userkeymap.append(('global', 'RunScript(special://home/addons/script.subskeys/default.py,background)', newkey))
          self.button14.setLabel(' [COLOR lightblue]'+key.lower()+'[/COLOR]'+_addon.getLocalizedString(32014))#('Set next Subtitle Button - [COLOR lightblue]'+key.lower()+'[/COLOR]')
        write_keymap(userkeymap,userdata+userkeymap_list)
    def showText(self,heading, text):
      id = 10147
      xbmc.executebuiltin('ActivateWindow(%d)' % id)
      xbmc.sleep(100)
      win = xbmcgui.Window(id)
      retry = 50
      while (retry > 0):
        try:
            xbmc.sleep(10)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            return
        except:
            pass
    def showcurrentkeymap(self):
         defaultkeymap = read_keymap(default)
         userkeymap=read_keymap(userdata+userkeymap_list)
         textfile=''
         for value in userkeymap:

           textfile=textfile+'[COLOR bisque]'+value[0].upper()+'[/COLOR]->[COLOR lightblue]'+value[1].upper()+'[/COLOR]->[COLOR khaki]'+self.convert_num_char(value[2])+'[/COLOR]\n'
         for value in defaultkeymap:
           textfile=textfile+'[COLOR bisque]'+value[0].upper()+'[/COLOR]->[COLOR lightblue]'+value[1].upper()+'[/COLOR]->[COLOR khaki]'+self.convert_num_char(value[2])+'[/COLOR]\n'
         #self.showText('Keymap',textfile)
         window = POPUPTEXT('Current Keymap',textfile)
         window.doModal()

         del window

    def clearbutton(self,type):
       userkeymap=read_keymap(userdata+userkeymap_list)
       if type=='open':
        location=findItem(userkeymap,'ActivateWindow(subtitlesearch)')
        self.button1.setLabel(_addon.getLocalizedString(32005))#'Set Open Subtitle Button - ')
       elif type=='next':
        location=findItem(userkeymap,'runscript(special://home/addons/script.subskeys/default.py,next)')
        self.button2.setLabel(_addon.getLocalizedString(32003))#('Set next Subtitle Button - ')
       elif type=='previous':
        location=findItem(userkeymap,'runscript(special://home/addons/script.subskeys/default.py,previous)')
        self.button3.setLabel(_addon.getLocalizedString(32004))#('Set Previous Subtitle Button - ')
       elif type=='delay_p':
        location=findItem(userkeymap,'subtitledelayplus')
        self.button9.setLabel(_addon.getLocalizedString(32006))#('Set Subtitle Delay Plus - ')
       elif type=='delay_m':
        location=findItem(userkeymap,'subtitledelayminus')
        self.button10.setLabel(_addon.getLocalizedString(32007))#('Set Subtitle Delay Minus - ')
       elif type=='background':
        location=findItem(userkeymap,'RunScript(special://home/addons/script.subskeys/default.py,background)')
        self.button14.setLabel(_addon.getLocalizedString(32014))#('Set Subtitle Delay Minus - ')
        
       for loc in location:
         userkeymap.pop(loc[0])
       write_keymap(userkeymap, userdata+userkeymap_list)
       
    def restore(self):
      choise=xbmcgui.Dialog(). yesno((_addon.getLocalizedString(32008)),(_addon.getLocalizedString(32009)))#'Restore','Are you sure you want to restore the default keymap?')
      if choise==True:
       if  os.path.exists(userdata+userkeymap_list):
          os.remove(userdata+userkeymap_list)

       if  os.path.exists(userdata+"keyboard0.old"):
           
           os.rename(userdata+"keyboard0.old", userdata+'keyboard.xml')
       self.close()
    def set_active_controls(self):
        '''
        int_label = pyxbmct.Label('Interactive Controls', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(int_label, 0, 2, 1, 2)
        #
        radiobutton_label = pyxbmct.Label('RadioButton')
        self.placeControl(radiobutton_label, 1, 2)
        # RadioButton
        self.radiobutton = pyxbmct.RadioButton('Off')
        self.placeControl(self.radiobutton, 1, 3)
        self.connect(self.radiobutton, self.radio_update)
        #
        edit_label = pyxbmct.Label('Edit')
        self.placeControl(edit_label, 2, 2)
        # Edit
        self.edit = pyxbmct.Edit('Edit')
        self.placeControl(self.edit, 2, 3)
        # Additional properties must be changed after (!) displaying a control.
        self.edit.setText('Enter text here')
        #
        list_label = pyxbmct.Label('List')
        self.placeControl(list_label, 3, 2)
        #
        self.list_item_label = pyxbmct.Label('', textColor='0xFF808080')
        self.placeControl(self.list_item_label, 4, 2)
        # List
        self.list = pyxbmct.List()
        self.placeControl(self.list, 3, 3, 3, 1)
        # Add items to the list
        items = ['Item {0}'.format(i) for i in range(1, 8)]
        self.list.addItems(items)
        # Connect the list to a function to display which list item is selected.
        self.connect(self.list, lambda: xbmc.executebuiltin('Notification(Note!,{0} selected.)'.format(
            self.list.getListItem(self.list.getSelectedPosition()).getLabel())))
        # Connect key and mouse events for list navigation feedback.
        self.connectEventList(
            [pyxbmct.ACTION_MOVE_DOWN,
             pyxbmct.ACTION_MOVE_UP,
             pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
             pyxbmct.ACTION_MOUSE_WHEEL_UP,
             pyxbmct.ACTION_MOUSE_MOVE],
            self.list_update)
        # Slider value label
        SLIDER_INIT_VALUE = 25.0
        self.slider_value = pyxbmct.Label(str(SLIDER_INIT_VALUE), alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.slider_value, 6, 3)
        #
        slider_caption = pyxbmct.Label('Slider')
        self.placeControl(slider_caption, 7, 2)
        # Slider
        self.slider = pyxbmct.Slider()
        self.placeControl(self.slider, 7, 3, pad_y=10)
        self.slider.setPercent(SLIDER_INIT_VALUE)
        # Connect key and mouse events for slider update feedback.
        self.connectEventList([pyxbmct.ACTION_MOVE_LEFT,
                               pyxbmct.ACTION_MOVE_RIGHT,
                               pyxbmct.ACTION_MOUSE_DRAG,
                               pyxbmct.ACTION_MOUSE_LEFT_CLICK],
                              self.slider_update)
        '''
     
        userkeymap=read_keymap(userdata+userkeymap_list)



        
        location_next=findItem(userkeymap,'RunScript(special://home/addons/script.subskeys/default.py,next)')
        location_previous=findItem(userkeymap,'RunScript(special://home/addons/script.subskeys/default.py,previous)')
        location_open=findItem(userkeymap,'ActivateWindow(subtitlesearch)')
        
        location_delay_p=findItem(userkeymap,'subtitledelayplus')
        location_delay_m=findItem(userkeymap,'subtitledelayminus')
         
        location_back=findItem(userkeymap,'RunScript(special://home/addons/script.subskeys/default.py,background)')
        # Button
        if len(location_open)>0:
          self.button1 = pyxbmct.Button(' [COLOR lightblue]'+self.convert_num_char(userkeymap[int(location_open[0][0])][2])+'[/COLOR]'+(_addon.getLocalizedString(32005)))
          
        else:
          self.button1 = pyxbmct.Button((_addon.getLocalizedString(32005)))
        self.placeControl(self.button1, 0,0, 1,3)
        #self.button.setLabel('New')
        # Connect control to close the window.
        self.connect(self.button1, lambda:self.setbutton(1,'open'))
        
        if len(location_next)>0:
          self.button2 = pyxbmct.Button(' [COLOR lightblue]'+self.convert_num_char(userkeymap[int(location_next[0][0])][2])+'[/COLOR]'+(_addon.getLocalizedString(32003)))
        else:
          self.button2 = pyxbmct.Button((_addon.getLocalizedString(32003)))
        self.placeControl(self.button2, 1,0, 1,3)
        # Connect control to close the window.
        self.connect(self.button2, lambda:self.setbutton(1,'next'))
        
        if len(location_previous)>0:
          self.button3 = pyxbmct.Button(' [COLOR lightblue]'+self.convert_num_char(userkeymap[int(location_previous[0][0])][2])+'[/COLOR]'+(_addon.getLocalizedString(32004)))
        else:
          self.button3 = pyxbmct.Button((_addon.getLocalizedString(32004)))
        self.placeControl(self.button3, 2,0, 1,3)
        # Connect control to close the window.
        self.connect(self.button3, lambda:self.setbutton(1,'previous'))
        
        if len(location_delay_p)>0:
          self.button9 = pyxbmct.Button(' [COLOR lightblue]'+self.convert_num_char(userkeymap[int(location_delay_p[0][0])][2])+'[/COLOR]'+(_addon.getLocalizedString(32006)))
        else:
          self.button9 = pyxbmct.Button((_addon.getLocalizedString(32006)))
        self.placeControl(self.button9, 3,0, 1,3)
        # Connect control to close the window.
        self.connect(self.button9, lambda:self.setbutton(1,'delay_p'))
        
        if len(location_delay_m)>0:
          self.button10 = pyxbmct.Button(' [COLOR lightblue]'+self.convert_num_char(userkeymap[int(location_delay_m[0][0])][2])+'[/COLOR]'+(_addon.getLocalizedString(32007)))
        else:
          self.button10 = pyxbmct.Button((_addon.getLocalizedString(32007)))
        self.placeControl(self.button10, 4,0, 1,3)
        # Connect control to close the window.
        self.connect(self.button10, lambda:self.setbutton(1,'delay_m'))
        
        if len(location_back)>0:
          self.button14 = pyxbmct.Button(' [COLOR lightblue]'+self.convert_num_char(userkeymap[int(location_back[0][0])][2])+'[/COLOR]'+_addon.getLocalizedString(32014))
        else:
          self.button14 = pyxbmct.Button((_addon.getLocalizedString(32014)))
        self.placeControl(self.button14, 5,0, 1,3)
        # Connect control to close the window.
        self.connect(self.button14, lambda:self.setbutton(1,'background'))
        
        
        
        self.button4 = pyxbmct.Button(_addon.getLocalizedString(32011))#('Show current keymap ')
        self.placeControl(self.button4, 6,0,2,2)
        # Connect control to close the window.
        self.connect(self.button4, lambda:self.showcurrentkeymap())
        
        
        self.button5 = pyxbmct.Button((_addon.getLocalizedString(32010)))
        self.placeControl(self.button5, 0,3, 1,1)
        #self.button.setLabel('New')
        # Connect control to close the window.
        self.connect(self.button5, lambda:self.clearbutton('open'))
        
        self.button6 = pyxbmct.Button(_addon.getLocalizedString(32010))
        self.placeControl(self.button6, 1,3, 1,1)
        #self.button.setLabel('New')
        # Connect control to close the window.
        self.connect(self.button6, lambda:self.clearbutton('next'))
        
        self.button7 = pyxbmct.Button(_addon.getLocalizedString(32010))
        self.placeControl(self.button7, 2,3, 1,1)
        #self.button.setLabel('New')
        # Connect control to close the window.
        self.connect(self.button7, lambda:self.clearbutton('previous'))
        
        self.button11 = pyxbmct.Button(_addon.getLocalizedString(32010))
        self.placeControl(self.button11, 3,3, 1,1)
        #self.button.setLabel('New')
        # Connect control to close the window.
        self.connect(self.button11, lambda:self.clearbutton('delay_p'))
        
        self.button12 = pyxbmct.Button(_addon.getLocalizedString(32010))
        self.placeControl(self.button12, 4,3, 1,1)
        #self.button.setLabel('New')
        # Connect control to close the window.
        self.connect(self.button12, lambda:self.clearbutton('delay_m'))
        
        self.button15 = pyxbmct.Button(_addon.getLocalizedString(32010))
        self.placeControl(self.button15, 5,3, 1,1)
        #self.button.setLabel('New')
        # Connect control to close the window.
        self.connect(self.button15, lambda:self.clearbutton('background'))
        
        self.button8 = pyxbmct.Button(_addon.getLocalizedString(32012))#('Resote default ')
        self.placeControl(self.button8, 6,2, 2,2)
        # Connect control to close the window.
        self.connect(self.button8, lambda:self.restore())
        
        # Button
        self.button13 = pyxbmct.Button((_addon.getLocalizedString(32013)))
        self.placeControl(self.button13, 8, 2)
        # Connect control to close the window.
        self.connect(self.button13, self.close)
        

     
    def set_navigation(self):
        # Set navigation between controls

        self.button13.controlUp(self.button8)
        self.button8.controlUp(self.button4)
        self.button4.controlUp(self.button12)
        self.button12.controlUp(self.button11)
        self.button11.controlUp(self.button7)
 
        self.button7.controlUp(self.button6)
        self.button6.controlUp(self.button5)
        self.button5.controlUp(self.button10)
        self.button10.controlUp(self.button9)
        self.button9.controlUp(self.button3)
        self.button3.controlUp(self.button2)
        self.button2.controlUp(self.button1)
        self.button1.controlUp(self.button13)
                
        self.button1.controlDown(self.button2)
        self.button2.controlDown(self.button3)
        self.button3.controlDown(self.button9)
        self.button9.controlDown(self.button10)
        self.button10.controlDown(self.button5)
        self.button5.controlDown(self.button6)
        self.button6.controlDown(self.button7)
        self.button7.controlDown(self.button11)
        self.button11.controlDown(self.button12)
        
        self.button12.controlDown(self.button4)
       
        self.button4.controlDown(self.button8)
        self.button8.controlDown(self.button13)
        self.button13.controlDown(self.button1)

        

        # Set initial focus
        self.setFocus(self.button1)

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

    def list_update(self):
        # Update list_item label when navigating through the list.
        try:
            if self.getFocus() == self.list:
                self.list_item_label.setLabel(self.list.getListItem(self.list.getSelectedPosition()).getLabel())
            else:
                self.list_item_label.setLabel('')
        except (RuntimeError, SystemError):
            pass

    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=500',),
                                ('WindowClose', 'effect=fade start=100 end=0 time=500',)])

def findItem(theList, item):
   return [(ind, theList[ind].index(item)) for ind in range(len(theList)) if item in theList[ind]]

if not os.path.exists(userdata+userkeymap_list):
    write_keymap(userkeymap, userdata+userkeymap_list)
logging.warning('Running Script')
if len(sys.argv)>1:
  params=sys.argv[1]
  logging.warning('params:')
  logging.warning(params)
  addon = xbmcaddon.Addon('service.subtitles.All_Subs')
  addon.setSetting('nextsub', params)
elif __name__ == '__main__':
    

    if os.path.exists(gen_file):
        try:
            userkeymap = read_keymap(gen_file)
        except Exception:
       
            rpc('GUI.ShowNotification', title="Keymap Editor",message="Failed to load keymap file", image='error')
            
   
    window = MyAddon('All Subs key mapper')
    window.doModal()
    # Destroy the instance explicitly because
    # underlying xbmcgui classes are not garbage-collected on exit.
    del window
