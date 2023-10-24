import json
import requests
import re
from datetime import datetime
from modules.kodi_utils import local_string as ls

# URL of the JSON file
MoviesOnlineDates_JSON_URL = "https://kodi7rd.github.io/MoviesOnlineDates_JSON/MoviesOnlineDates.json"

# Define the datetime format string
timestamp_format = '%d.%m.%Y %H:%M'

def reformat_message_content(message_content):
    
    # Remove Telegram link reference for movie name twice
    for _ in range(2):
        message_content = re.sub(r'\[([^]]+)\]\(https://t\.me/MoviesOnlineDates/\d+\)', r'\1', message_content)
        
    # Unwanted strings to remove️
    unwanted_strings = [
        ('**', ''),
        ('ערוץ: @MoviesOnlineDates', ''),
        ('קבוצה: @MoviesOnlineDatesChat', ''),
        ('⭐', ''),
        ('🚨', ''),
        ('❗', '!'),
        ('הצטרפו אלינו:', ''),
        ('קבוצת הדיונים ובקשת תאריכים: @MoviesOnlineDatesChat', ''),
        ('🇮🇱', '[B][COLOR cyan]ישראל[/COLOR][/B]'),
        ('🇺🇸', 'ארה"ב'),
        ('🇯🇵', 'יפן'),
        ('✅', '[B][COLOR FF5CFF34](יצא)[/COLOR][/B]'),
        ('תקציר:\n', 'תקציר: '),
        ('️️', '')
    ]
    
    for unwanted_string, replacement_char in unwanted_strings:
        message_content = message_content.replace(unwanted_string, replacement_char)
    
    # Use regular expression to replace multiple consecutive newline characters with a single newline
    message_content = re.sub(r'\n+', '\n', message_content)
    
    # Movie label
    message_content = re.sub(f'🎬\s*(.*)\s*🎬', r'[B][COLOR yellow]\1[/COLOR][/B]', message_content)
    
    # Bold headers
    bold_headers = ["ז'אנר:", "בימוי:", "שחקנים:", "תקציר:", "תאריך יציאה לקולנוע:", "תאריך יציאה לרשת:"]
    for bold_header in bold_headers:
        # Use regular expression to capture the pattern and replace it with [B][I]pattern[/I][/B]
        message_content = re.sub(f'({bold_header})', r'[B]\1[/B]', message_content)
    
    # Make "עדכון 1 לגבי הסרט..." bold
    message_content = re.sub(r'עדכון (\d+) לגבי הסרט "(.*?)"', r'[B]עדכון \1 לגבי הסרט "\2"[/B]', message_content)
    
    # Check if both "תאריך יציאה לקולנוע:" and "תאריך יציאה לרשת:" are in the text
    if "[B]תאריך יציאה לקולנוע:[/B]" in message_content and "[B]תאריך יציאה לרשת:[/B]" in message_content:
    
        try:
            # Split the text into lines
            lines = message_content.split('\n')

            # Find the index of "[B]תאריך יציאה לקולנוע:[/B]"
            start_index = lines.index("[B]תאריך יציאה לקולנוע:[/B]")

            # Move the content from "תאריך יציאה לקולנוע:" to the end of the text to the second line
            moved_content = lines[start_index:]
            lines[start_index:] = []  # Remove the moved lines
            lines.insert(1, '\n'.join(moved_content))  # Insert the moved content at the second line

            # Reconstruct the text
            message_content = '\n'.join(lines)
        except:
            pass
            
    message_content = message_content.rstrip()
    
    return message_content

# Function to load JSON data from the URL
def load_json_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    return None
    
def search_MoviesOnlineDates_titles(title=None, original_title=None):

    # Load JSON data from the URL
    json_data = load_json_data(MoviesOnlineDates_JSON_URL)

    if not json_data:
        return "התרחשה שגיאה בטעינת הנתונים!"
    
    messages = []

    # Iterate through the JSON data and search for messages containing movie title / original_title
    for message in json_data:
    
        message_content = message["message_content"]
        
        if 'סרטים שצפויים להגיע החודש' in message_content:
            continue
            
        if (title and title in message_content) or (original_title and original_title in message_content):
            messages.append(message)

    if not messages:
        return "לא נמצא מידע!"
    
    movie_information_results = f'[B]המידע לקוח מערוץ הטלגרם "מתי יגיע לרשת?" (MoviesOnlineDates@)[/B]\n{"-"*125}\n'
    message_number = 1

    for message in messages:
        
        message_content = reformat_message_content(message['message_content'])
        
        message_timestamp_ltr_format = "\u202A" + message['message_timestamp'] + "\u202C"
        message_timestamp_str = f"[B][COLOR FF5CFF34]{message_number}) פורסם בתאריך {message_timestamp_ltr_format}[/COLOR][/B]"
        
        movie_information_results += f"{message_timestamp_str}\n{message_content}\n{'-'*125}\n"
        message_number += 1
        
    return movie_information_results


def search_MoviesOnlineDates(title=None, original_title=None):
    
    window_header = f"{ls(400017)} ({title})"

    movie_information_results = search_MoviesOnlineDates_titles(title, original_title)
        
    show_MoviesOnlineDates(window_header, movie_information_results)


def show_MoviesOnlineDates(window_header, movie_information_results):
    from windows.base_window import open_window
    return open_window(('windows.textviewer', 'TextViewer'), 'MoviesOnlineDates.xml', heading=window_header, text=movie_information_results)