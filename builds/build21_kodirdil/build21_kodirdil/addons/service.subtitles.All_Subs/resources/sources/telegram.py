# Import necessary libraries
import random
import shutil
import xbmcaddon,os,xbmc,xbmcgui
global global_var,site_id,sub_color#global
global_var=[]
from resources.modules import log
from resources.modules.general import notify
from resources.modules.general import extract_season_episode_numbers
import requests,json
import urllib
from resources.modules.extract_sub import extract
import xbmcvfs
#########################################

que=urllib.parse.quote_plus
Addon=xbmcaddon.Addon()
MyScriptID=Addon.getAddonInfo('id')
xbmc_tranlate_path=xbmcvfs.translatePath
__profile__ = xbmc_tranlate_path(Addon.getAddonInfo('profile'))
MyTmp = xbmc_tranlate_path(os.path.join(__profile__, 'temp_telegram'))

### TELETHON IMPORTS ###
import sys
# Disable C-based asyncio module https://kodi.wiki/view/Python_Problems#asyncio
sys.modules['_asyncio'] = None
import threading
import asyncio
telethon_dependencies = xbmc_tranlate_path(f'special://home/addons/{MyScriptID}/resources/modules/telethon_dependencies')
sys.path.append(telethon_dependencies)
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.types import InputMessagesFilterDocument, InputNotifyPeer, InputPeerNotifySettings
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import SessionPasswordNeededError, FloodWaitError, PhonePasswordFloodError, PasswordHashInvalidError, ChannelPrivateError
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError, PhoneCodeInvalidError
#########################################

########### Constants ###################
site_id='[Telegram]'
sub_color='deepskyblue'
# Telegram API credentials
from resources.modules.telethon_dependencies.telegram_api import api_id, api_hash, bot_token
# Telegram channel params
AllSubs_CHANNEL_ID = -1002086580511
AllSubs_CHANNEL_INVITE_LINK_SUFFIX = "t-8FePk4xRI1MDA0"
# Define the path to the session file
session_file_directory = xbmc_tranlate_path(os.path.join(__profile__, 'telegram_session'))
session_string_file_path = os.path.join(session_file_directory, 'telethon_session_string.txt')

english_hebrew_lang_mapping = {
    "Albanian": "אלבנית",
    "Arabic": "ערבית",
    "Bengali": "בנגלית",
    "Brazilian Portuguese": "פורטוגזית ברזילאית",
    "Bulgarian": "בולגרית",
    "Chinese": "סינית",
    "Croatian": "קרואטית",
    "Czech": "צ'כית",
    "Danish": "דנית",
    "Dutch": "הולנדית",
    "English": "אנגלית",
    "Farsi/Persian": "פרסית",
    "Finnish": "פינית",
    "French": "צרפתית",
    "German": "גרמנית",
    "Greek": "יוונית",
    "Hebrew": "עברית",
    "Hungarian": "הונגרית",
    "Indonesian": "אינדונזית",
    "Italian": "איטלקית",
    "Japanese": "יפנית",
    "Korean": "קוריאנית",
    "Lithuanian": "ליטאית",
    "Macedonian": "מקדונית",
    "Malay": "מלאית",
    "Norwegian": "נורווגית",
    "Polish": "פולנית",
    "Romanian": "רומנית",
    "Russian": "רוסית",
    "Serbian": "סרבית",
    "Slovenian": "סלובנית",
    "Spanish": "ספרדית",
    "Swedish": "שוודית",
    "Thai": "תאית",
    "Turkish": "טורקית",
    "Urdu": "אורדו",
    "Vietnamese": "וייטנאמית"
}
#########################################

# Custom function to handle Kodi input dialogs
def kodi_input_dialog(prompt, auto_fill="", input_type="int"):
    dialog = xbmcgui.Dialog()
    return dialog.input(prompt, type=xbmcgui.INPUT_ALPHANUM) if input_type=="string" else dialog.input(prompt, auto_fill, type=xbmcgui.INPUT_NUMERIC)

# Custom function to handle phone number input
def get_valid_phone_number():
    while True:
        # Prompt user for phone number using Kodi dialog
        phone = kodi_input_dialog("הזן את מספר הטלפון שלך בפורמט:\n05XXXXXXXX", auto_fill="05", input_type="int")
        if not phone:
            return None
        
        # Check if the entered phone number is in the correct format
        if phone.startswith("05"):
            # If the phone number starts with "05" and is 9 digits long, add the country code
            return f"972{phone[1:]}"
        return phone

################### LOGIN ###############################################
# Custom function to handle Telegram login using Kodi input dialogs
async def login_to_telegram():
    try:
        client = await connect_telegram_client(exit_if_unauthorized=False)
        if client:
            if not await client.is_user_authorized():
                # Prompt user for phone number using Kodi dialog
                phone = get_valid_phone_number()
                if not phone:
                    notify("החיבור בוטל")
                    return
                try:
                    await client.send_code_request(phone, force_sms=False)
                except PhoneNumberInvalidError:
                    notify("מספר טלפון לא חוקי!")
                    return
                except FloodWaitError as e:
                    notify(f"הצפה מול טלגרם, המתן {e.seconds} שניות.")
                    return
                except PhonePasswordFloodError as e:
                    notify("ניסית להתחבר לטלגרם יותר מדי פעמים.")
                    return
                
                # Flag to indicate if sign-in is successful
                signed_in = False
                # Prompt user for verification code using Kodi dialog
                while not signed_in:
                    code = kodi_input_dialog("הזן את הקוד שקיבלת מטלגרם:", input_type="int")
                    if not code:
                        notify("החיבור בוטל")
                        return
                    try:
                        # Try signing in with the provided code
                        await client.sign_in(phone, code)
                        signed_in = True  # Set flag to True if sign-in is successful
                    except SessionPasswordNeededError:
                        while not signed_in:
                            # If 2FA is enabled, prompt user for password
                            password = kodi_input_dialog("הכנס את הסיסמה האישית שלך:", input_type="string")
                            if not password:
                                notify("החיבור בוטל")
                                return
                            try:
                                # Finish the verification process including the 2FA password
                                await client.sign_in(password=password)
                                signed_in = True  # Set flag to True if sign-in is successful
                            except PasswordHashInvalidError:
                                notify("הסיסמה שגויה. אנא נסה שנית.")
                                continue  # Continue the password loop to prompt for password again
                            except Exception as e:
                                log.warning(f"[Telegram] | login_to_telegram | Exception type: {type(e)} | Exception during sign-in with password: {str(e)}")
                                notify("התרחה שגיאה, בדוק בלוג.")
                                continue  # Continue the password loop to prompt for password again
                    except PhoneCodeInvalidError:
                        notify("קוד שגוי, נסה שנית.")
                        continue  # Continue the loop to prompt for code again
                    except FloodWaitError as e:
                        notify(f"הצפה מול טלגרם, המתן {e.seconds} שניות.")
                        return
                    except Exception as e:
                        log.warning(f"[Telegram] | login_to_telegram | Exception type: {type(e)} | Exception during sign-in with code: {str(e)}")
                        notify("התרחה שגיאה, בדוק בלוג.")
                        continue  # Continue the loop to prompt for code again
                set_session_string(client.session.save())
                # Retrieve client's first and last names
                try:
                    me = await client.get_me()
                    first_name = me.first_name or ''
                    last_name = me.last_name or ''
                    Addon=xbmcaddon.Addon()
                    Addon.setSetting("telegram_first_and_last_name", f"[B]{first_name} {last_name}[/B]")
                    xbmcgui.Dialog().ok("התחברת בהצלחה", f"שלום, {first_name} {last_name}\n[B]בסיום, לא לשכוח ללחוץ אישור בצד ימין![/B]")
                except:
                    xbmcgui.Dialog().ok("חיבור הושלם בהצלחה!", "חיבור הושלם בהצלחה!\n[B]בסיום, לא לשכוח ללחוץ אישור בצד ימין![/B]")
                log.warning("[Telegram] | login_to_telegram | Connection to Telegram - success.")
                await joinAllSubsChannel(client)
            else:
                try:
                    me = await client.get_me()
                    first_name = me.first_name or ''
                    last_name = me.last_name or ''
                    Addon=xbmcaddon.Addon()
                    Addon.setSetting("telegram_first_and_last_name", f"[B]{first_name} {last_name}[/B]")
                    xbmcgui.Dialog().ok("הינך כבר מחובר", f"הינך כבר מחובר, {first_name} {last_name}\n[B]בסיום, לא לשכוח ללחוץ אישור בצד ימין![/B]")
                except:
                    xbmcgui.Dialog().ok("כבר מחובר!", "כבר מחובר!\n[B]בסיום, לא לשכוח ללחוץ אישור בצד ימין![/B]")

    except Exception as e:
        notify(f"Telegram | login_to_telegram | Exception type: {type(e)} | Exception: {str(e)}")
        log.warning(f"[Telegram] | login_to_telegram | Exception type: {type(e)} | Exception: {str(e)}")
    finally:
        if client:
            try:
                await client.disconnect()
                log.warning(f"[Telegram] | login_to_telegram finally | Client finished function and disconnected.")
            except Exception as e:
                log.warning(f"[Telegram] | logout_from_telegram | Exception type: {type(e)} | Exception: {str(e)}")
                notify(f"Telegram | logout_from_telegram finally | Exception type: {type(e)} | Exception: {str(e)}")

# Function to run asyncio code in a separate thread
def run_async_login_to_telegram():
    notify("נא המתן..")
    asyncio.run(login_to_telegram())
#########################################################################

################### LOGOUT ##############################################
async def logout_from_telegram():
    confirm = xbmcgui.Dialog().yesno("האם אתה בטוח?", "האם אתה בטוח?", "[B][COLOR red]לא[/COLOR][/B]","[B][COLOR springgreen]כן[/COLOR][/B]")
    if not confirm: return
    # Create the directory if it doesn't exist
    if not os.path.exists(session_file_directory):
        os.makedirs(session_file_directory)
    try:
        telegram_session_string = get_session_string()
        client = TelegramClient(StringSession(telegram_session_string), api_id, api_hash)
        await client.connect()
        Addon=xbmcaddon.Addon()
        Addon.setSetting("telegram_first_and_last_name", "[B]לא מחובר[/B]")
        if await client.is_user_authorized():
            try:
                me = await client.get_me()
                first_name = me.first_name or ''
                last_name = me.last_name or ''
                await client.log_out()
                set_session_string('')
                xbmcgui.Dialog().ok("החשבון נותק בהצלחה", f"התנתקת בהצלחה, {first_name} {last_name}\n[B]בסיום, לא לשכוח ללחוץ אישור בצד ימין![/B]")
            except:
                xbmcgui.Dialog().ok("החשבון נותק בהצלחה", "החשבון נותק בהצלחה\n[B]בסיום, לא לשכוח ללחוץ אישור בצד ימין![/B]")
        else:
            xbmcgui.Dialog().ok("אינך מחובר לחשבון טלגרם.", "אינך מחובר לחשבון טלגרם.\n[B]בסיום, לא לשכוח ללחוץ אישור בצד ימין![/B]")
    except Exception as e:
        notify(f"Telegram | logout_from_telegram | Exception type: {type(e)} | Exception: {str(e)}")
        log.warning(f"[Telegram] | logout_from_telegram | Exception type: {type(e)} | Exception: {str(e)}")

def run_async_logout_from_telegram():
    asyncio.run(logout_from_telegram())
#########################################################################

################### CONNECT #############################################
def telegram_helper_window():
    dialog = xbmcgui.Dialog()
    dialog.ok("Telegram",'[B]לחצו "התחבר" כדי להתחבר לחשבון הטלגרם שלכם.\nלאחר מכן, תצורפו אוטומטית לערוץ הכתוביות AllSubs.\n(במידה ומתחברים מטלפון נייד - אין למזער את הקודי בזמן הזנת קוד האימות מהטלגרם)[/B]')

def get_session_string():
    try:
        with open(session_string_file_path, 'r') as file:
            return file.read()
    except Exception:
        return ''

def set_session_string(session_string):
    with open(session_string_file_path, 'w') as file:
        file.write(session_string)

async def connect_telegram_client(exit_if_unauthorized=True):
    # Create the directory if it doesn't exist
    if not os.path.exists(session_file_directory):
        os.makedirs(session_file_directory)
    try:
        telegram_session_string = get_session_string()
        if telegram_session_string:
            client = TelegramClient(StringSession(telegram_session_string), api_id, api_hash)
        else:
            client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized() and exit_if_unauthorized:
            return None
        return client
    except Exception as e:
        notify(f"Telegram | connect_telegram_client | Exception type: {type(e)} | Exception: {str(e)}")
        log.warning(f"[Telegram] | connect_telegram_client | Exception type: {type(e)} | Exception: {str(e)}")
        return None
#########################################################################


async def joinAllSubsChannel(client):
    try:
        # Check if the user is already in the channel
        try:
            await client.get_entity(AllSubs_CHANNEL_ID)
            log.warning("[Telegram] | joinAllSubsChannel | get_entity | User already in channel!")
            return  # If user is already in the channel, return without attempting to join
        except Exception as e:
            log.warning(f"[Telegram] | joinAllSubsChannel | get_entity | exception: {e}")
            pass

        # Attempt to parse the invite link and join the channel
        AllSubsChannel = await client(ImportChatInviteRequest(AllSubs_CHANNEL_INVITE_LINK_SUFFIX))
        log.warning("[Telegram] | joinAllSubsChannel | ImportChatInviteRequest | Joined channel successfully.")

        # Mute notifications of the channel forever
        await client(UpdateNotifySettingsRequest(
            peer=InputNotifyPeer(AllSubsChannel.chats[0]),  # Target the joined channel chat
            settings=InputPeerNotifySettings(mute_until=2**31 - 1)  # Mute forever
        ))
        log.warning("[Telegram] | joinAllSubsChannel | Notifications muted forever.")
        
        # Archive the joined channel
        # await client.edit_folder([AllSubsChannel.chats[0]], folder=1)
        # log.warning("[Telegram] | joinAllSubsChannel | Channel archived.")
        
        notify("צורפת לערוץ הכתוביות AllSubs בהצלחה!")
        
    except Exception as e:
        log.warning(f"[Telegram] | joinAllSubsChannel | ImportChatInviteRequest| Failed to join channel: {str(e)}")

################### SEARCH ##############################################
async def async_search_subtitles(search_query_list, exit_if_unauthorized):
    client = await connect_telegram_client(exit_if_unauthorized)
    if client:
        async with client:
            try:
                telegram_search_results = await search_subtitles(client, search_query_list)
                return telegram_search_results
            except (ChannelPrivateError, ValueError) as e:
                xbmc.sleep(300)
                log.warning(f"[Telegram] | async_search_subtitles | Exception type: {type(e)} | Exception: {str(e)}")
                log.warning("[Telegram] | async_search_subtitles | User not in channel. Attempting to join...")
                await joinAllSubsChannel(client)
                xbmc.sleep(300)
                # Retry search after joining the channel
                telegram_search_results = await search_subtitles(client, search_query_list)
                return telegram_search_results
            except Exception as e:
                notify(f"Telegram | async_search_subtitles | Exception type: {type(e)} | Exception: {str(e)}")
                log.warning(f"[Telegram] | async_search_subtitles | Exception type: {type(e)} | Exception: {str(e)}")
                return []
            finally:
                await client.disconnect()
                log.warning(f"[Telegram] | async_search_subtitles | Client finished function and disconnected.")
    else:
        log.warning("[Telegram] | async_search_subtitles | Failed to connect to Telegram client.")
    return []

# Wrapper function for Telethon client connection
async def search_subtitles(client, search_query_list):
    telegram_search_results=[]
    for search_query in search_query_list:
        log.warning(f"[Telegram] | search_subtitles | Searching for: {search_query}")
        async for message in client.iter_messages(AllSubs_CHANNEL_ID, limit=900, reverse=True, search=search_query, filter=InputMessagesFilterDocument):
            telegram_search_results.append(message)
    return telegram_search_results
#########################################################################
    

################### DOWNLOAD ############################################
async def async_download_subtitle(telegram_message_file_id):
    client = await connect_telegram_client()
    if client:
        async with client:
            try:
                # Fetch the message using its ID
                telegram_subtitle_message = await client.get_messages(AllSubs_CHANNEL_ID, ids=telegram_message_file_id)
                await telegram_subtitle_message.download_media(MyTmp)
                log.warning(f"[Telegram] | async_download_subtitle | File downloaded successfully | {MyTmp}")
            except Exception as e:
                log.warning(f"[Telegram] | async_download_subtitle | Exception: {str(e)}")
            finally:
                await client.disconnect()
                log.warning(f"[Telegram] | async_download_subtitle | Client finished function and disconnected.")
    else:
        log.warning("[Telegram] | async_download_subtitle | Failed to connect to Telegram client.")

def run_async_download_subtitle(telegram_message_file_id):
    asyncio.run(async_download_subtitle(telegram_message_file_id))
#########################################################################


################### UPLOAD ##############################################
async def async_upload_subtitle(sub_file_to_upload, filename_to_upload, upload_message_caption):

    client = await connect_telegram_client(exit_if_unauthorized=False)
    if client:
        async with client:
            try:
                await client.send_file(AllSubs_CHANNEL_ID, sub_file_to_upload, caption=upload_message_caption)
                log.warning(f"[Telegram] | async_upload_subtitle | Subtitle uploaded successfully | filename_to_upload={filename_to_upload}")
            except Exception as e:
                log.warning(f"[Telegram] | async_upload_subtitle | Exception: {str(e)}")
            finally:
                await client.disconnect()
                log.warning(f"[Telegram] | async_upload_subtitle | Client finished function and disconnected.")
    else:
        log.warning("[Telegram] | async_upload_subtitle | Failed to connect to Telegram client.")
#########################################################################
       
def get_subs(item):
    
    global global_var
    media_type = item["media_type"]
    season = item.get('season', '')
    episode = item.get('episode', '')
    imdb_id = item.get('imdb', '')
    
    if not imdb_id.startswith('tt'): return []
    
    search_query_list = [imdb_id] # Example: ["tt16253418"]
    log.warning(f"[Telegram] | item={str(item)}")
    log.warning(f"[Telegram] | query={str(search_query_list)}")
    

    telegram_search_results = asyncio.run((async_search_subtitles(search_query_list, exit_if_unauthorized=True)))
    if not telegram_search_results: return
        
    telegram_found_subtitles_files=[]
    subtitle_list=[]
    
    for telegram_message in telegram_search_results:
    
        telegram_message_file_name = telegram_message.media.document.attributes[0].file_name
        # Skip over already added subtitles
        # Skip over ZIP files from @ScrewZiraBot (always contains more than 1 subtitles)
        if (telegram_message_file_name in telegram_found_subtitles_files) or (telegram_message_file_name.startswith('@ScrewZiraBot') and telegram_message_file_name.endswith('.zip')):
            continue
        telegram_found_subtitles_files.append(telegram_message_file_name)

        #####################################################################################################################
        # TV Shows Season/Episode Number Matching
        if media_type == 'tv':
            # Check if the extracted numbers match the expected values
            if extract_season_episode_numbers(telegram_message_file_name) != (season.zfill(2), episode.zfill(2)):
                # Skip this subtitle if there's no match
                continue
        #####################################################################################################################
        
        telegram_message_caption = telegram_message.message.replace('\n',' ')
        
        telegram_message_file_id = telegram_message.id
        
        telegram_subtitle_display_name = telegram_message_file_name
        strings_to_replace = [
            'TranslationsMoviesHEB.t.me HEB',
            'TranslationsMoviesHEB HEB',
            'TranslationsMoviesHEB.t.me',
            'TranslationsMoviesHEB',
            '@ScrewZiraBot_',
            '@ScrewZiraBot-',
            '@ScrewZiraBot',
            '.srt',
            '.ass',
            '.sub',
            '.idx',
            '.sup',
        ]
        for string in strings_to_replace:
            telegram_subtitle_display_name = telegram_subtitle_display_name.replace(string, '') # Replace to none
        
        language = "Hebrew"
        if 'Imdb:' in telegram_message_caption and 'תרגום מכונה' in telegram_message_caption:
            # Use regex to find the language name, ensuring "תרגום מכונה - " is present
            import re
            match = re.search(r'\(([^-]+) - תרגום מכונה\)', telegram_message_caption)
            if match:
                english_lang_name = match.group(1).strip()
                hebrew_lang_name = english_hebrew_lang_mapping.get(english_lang_name, None)
                machine_translated_text = f"(תרגום מכונה מ{hebrew_lang_name})" if hebrew_lang_name else f"({english_lang_name}-תרגום מכונה מ)"
            else:
                machine_translated_text = f"(תרגום מכונה)"
            telegram_subtitle_display_name = f'[COLOR khaki]{machine_translated_text}[/COLOR] {telegram_subtitle_display_name}'
            language = "HebrewMachineTranslated"
            
        download_data = {}
        download_data['filename'] = telegram_message_file_name
        download_data['id'] = telegram_message_file_id
        download_data['format'] = "srt"
        url = "plugin://%s/?action=download&filename=%s&id=%s&download_data=%s&source=telegram&language=%s" % (
                MyScriptID, que(telegram_message_file_name), telegram_message_file_id, que(json.dumps(download_data)), language)

        json_data={'url':url,
                         'label':language,
                         'label2':site_id+' '+telegram_subtitle_display_name,
                         'iconImage':"",
                         'thumbnailImage':"he",
                         'hearing_imp':'false',
                         'site_id':site_id,
                         'sub_color':sub_color,
                         'filename':telegram_message_file_name,
                         'sync': 'false'}

      
        subtitle_list.append(json_data)
                
    global_var=subtitle_list
    
    
def download(download_data,MySubFolder):
    try:
        shutil.rmtree(MyTmp)
    except: pass
    xbmcvfs.mkdirs(MyTmp)
    telegram_message_file_id = download_data['id']
    filename = download_data['filename']
    
    sub_file = os.path.join(MyTmp, str(filename))
    log.warning(f'Telegram | Desired sub filename: {filename} | telegram_message_file_id: {telegram_message_file_id} | sub_file: {sub_file}')
    
    # Create a thread for downloading the subtitle asynchronously
    download_thread = threading.Thread(target=run_async_download_subtitle, args=(telegram_message_file_id,))
    download_thread.start()
    download_thread.join()
    
    return sub_file
    


def upload_subtitle_to_telegram(sub_file_to_upload,filename_to_upload,caption,source):
    
    from resources.modules.general import get_video_data
    imdb_id = get_video_data().get('imdb', '')

    upload_message_caption = f"Imdb: {imdb_id}{caption}\nSource: {source}"
    
    telegram_search_results = asyncio.run((async_search_subtitles([filename_to_upload], exit_if_unauthorized=False)))
    
    for telegram_message in telegram_search_results:
    
        telegram_message_file_name = telegram_message.media.document.attributes[0].file_name
        
        extensions_to_remove = ['.srt', '.sub', '.sup', '.idx', '.ass']
        for extension in extensions_to_remove:
            if filename_to_upload.lower().replace(extension, '') == telegram_message_file_name.lower().replace(extension, ''):
                # Exit function if subtitle already in Telegram channel.
                log.warning(f"[Telegram] | upload_subtitle_to_telegram | Subtitle already exists in telegram | filename_to_upload={filename_to_upload}")
                return
                
    xbmc.sleep(200)
    # asyncio.run(async_upload_subtitle(sub_file_to_upload, filename_to_upload, upload_message_caption))
    # Upload From Bot
    try:
        telegram_api_url = "https://api.telegram.org"
        document = f"{telegram_api_url}/bot{bot_token}/sendDocument"
        upload_message_caption += "\n(Upload From Bot)"
        
        file_to_upload = open(sub_file_to_upload, 'rb')
        files = {
        'chat_id': (None, AllSubs_CHANNEL_ID),
        'document': file_to_upload,
        'caption':(None,upload_message_caption)
        }
            
        response = requests.post(document, files=files)
        file_to_upload.close()
        log.warning(f"[Telegram] | upload_subtitle_to_telegram | Subtitle uploaded successfully | filename_to_upload={filename_to_upload}")
        
    except Exception as e:
        log.warning(f"[Telegram] | upload_subtitle_to_telegram | Exception: {str(e)}")