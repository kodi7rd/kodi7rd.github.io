########### Imports #####################
from modules import kodi_utils
import threading
########### KODI-RD-IL Imports ##########
from kodirdil import string_utils
from kodirdil import db_utils
# Import hebrew subtitle search functions
from kodirdil.websites import hebrew_embedded
from kodirdil.websites import ktuvit
from kodirdil.websites import wizdom
from kodirdil.websites import opensubtitles
from kodirdil.websites import subscene
#########################################

########### Settings ####################
minimum_sync_percent = int(kodi_utils.get_setting('minimum_hebrew_subtitles_sync_percentage_match_slider', '75'))
search_for_english_subtitles_when_no_hebrew_subtitles_found = kodi_utils.get_setting('search_for_english_subtitles_when_no_hebrew_subtitles_found', 'true') == 'true'
search_hebrew_subtitles_in_embedded = kodi_utils.get_setting('search_hebrew_subtitles_in_embedded', 'true') == 'true'
#########################################

########### Constants ###################
hebrew_subtitles_websites_info = {
    'ktuvit': {'website': ktuvit, 'short_name': '[HEB|KT]'},
    'wizdom': {'website': wizdom, 'short_name': '[HEB|WIZ]'},
    'opensubtitles': {'website': opensubtitles, 'short_name': '[HEB|OPS]'},
    'subscene': {'website': subscene, 'short_name': '[HEB|SS]'}
    }
    
english_subtitles_websites_info = {
    'opensubtitles': {'website': opensubtitles, 'short_name': '[ENG|OPS]'},
    'subscene': {'website': subscene, 'short_name': '[ENG|SS]'}
    }
    
release_names = ['blueray','bluray','blu-ray','bdrip','brrip','brip',
                 'hdtv','hdtvrip','pdtv','tvrip','hdrip','hd-rip',
                 'web','web-dl','web dl','web-dlrip','webrip','web-rip',
                 'dvdr','dvd-r','dvd-rip','dvdrip','cam','hdcam','cam-rip','camrip','screener','dvdscr','dvd-full',
                 'telecine','hdts','telesync']

# If "Check Before FulL Search" setting is enabled, first sources list is only CLOUD
IS_SEARCHED_FROM_EXTERNAL = False
# Initialize HEBREW_SUBTITLES_FOUND
HEBREW_SUBTITLES_FOUND = False
#########################################

def search_hebrew_subtitles_on_website(website_info, media_metadata, website_subtitles_dict, lock):
    global HEBREW_SUBTITLES_FOUND  # Declare HEBREW_SUBTITLES_FOUND as a global variable
    try:
        hebrew_subtitles_list = website_info['website'].search_for_subtitles(media_metadata)
        hebrew_subtitles_list = strip_problematic_chars_from_subtitle_names_list(hebrew_subtitles_list)

        with lock:
            website_subtitles_dict[website_info['short_name']] = hebrew_subtitles_list
            
        if hebrew_subtitles_list:  # If Hebrew subtitles are found
            HEBREW_SUBTITLES_FOUND = True  # Set HEBREW_SUBTITLES_FOUND to True

        kodi_utils.logger("KODI-RD-IL", f"{website_info['short_name']}_subtitles_list: {str(hebrew_subtitles_list)}")
        kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")

    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"Error in searching Hebrew subtitles from {website_info['website']}: {str(e)}")
        kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")


def search_english_subtitles_on_website(website_info, media_metadata, website_subtitles_dict, lock):
    try:
        english_subtitles_list = website_info['website'].search_for_subtitles(media_metadata, language='English')
        english_subtitles_list = strip_problematic_chars_from_subtitle_names_list(english_subtitles_list)

        with lock:
            website_subtitles_dict[website_info['short_name']] = english_subtitles_list

        kodi_utils.logger("KODI-RD-IL", f"{website_info['short_name']}_subtitles_list: {str(english_subtitles_list)}")
        kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")

    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"Error in searching English subtitles from {website_info['website']}: {str(e)}")
        kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")


def search_hebrew_subtitles_for_selected_media(media_type, title, season, episode, year, tmdb_id, imdb_id):

    """
    Search for Hebrew subtitles for a selected media and write the filtered subtitles to a cache table.
    
    Args:    
    media_type: The type of media ('movie' or 'tv').
    title: The title of the media.
    season: The season number for TV shows.
    episode: The episode number for TV shows.
    year: The release year of the media.
    tmdb_id: The ID of the media in the TMDB database.

    Returns:
    None
    """
    global IS_SEARCHED_FROM_EXTERNAL
    IS_SEARCHED_FROM_EXTERNAL = True
    
    # Check if the current metadata in the cache is the same as the new metadata
    current_media_metadata_in_cache = db_utils.get_current_media_metadata_from_media_metadata_db()
    # Convert season and episode to strings to match the data types
    input_params = (str(media_type), str(title), str(season), str(episode), str(year), str(tmdb_id))
    if current_media_metadata_in_cache and current_media_metadata_in_cache == input_params:
        # Metadata is the same, no need to write to the cache
        kodi_utils.logger("KODI-RD-IL", f"current_media_metadata_in_cache is the same. Skipping subtitles search...")
        return
        
    # Write the current media_type to the media_metadata_dbcache table
    db_utils.write_current_media_metadata_to_media_metadata_db(media_type, title, season, episode, year, tmdb_id)
    
    media_metadata = {
        "media_type": media_type,
        "title": title.replace("%20"," ").replace("%27","'"),
        "season": season,
        "episode": episode,
        "year": year,
        "tmdb_id": tmdb_id,
        "imdb_id": imdb_id
    }
    
    kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
    
    # Search for subtitles in all websites and combine them into a single list
    lock = threading.Lock()  # Create a lock for thread safety
    hebrew_subtitles_search_threads = []
    website_subtitles_dict = {}
    global HEBREW_SUBTITLES_FOUND

    # Hebrew subtitle search threads
    for website_info in hebrew_subtitles_websites_info.values():
        thread = threading.Thread(target=search_hebrew_subtitles_on_website, args=(website_info, media_metadata, website_subtitles_dict, lock))
        hebrew_subtitles_search_threads.append(thread)
        thread.start()

    for thread in hebrew_subtitles_search_threads:
        thread.join()
    
    kodi_utils.logger("KODI-RD-IL", f"HEBREW_SUBTITLES_FOUND={HEBREW_SUBTITLES_FOUND} | SETTING search_for_english_subtitles_when_no_hebrew_subtitles_found={search_for_english_subtitles_when_no_hebrew_subtitles_found}")

    # English subtitle search threads
    if not HEBREW_SUBTITLES_FOUND and search_for_english_subtitles_when_no_hebrew_subtitles_found:
        # Reset website_subtitles_dict
        website_subtitles_dict = {}
        english_subtitles_search_threads = []
        
        for website_info in english_subtitles_websites_info.values():
            thread = threading.Thread(target=search_english_subtitles_on_website, args=(website_info, media_metadata, website_subtitles_dict, lock))
            english_subtitles_search_threads.append(thread)
            thread.start()

        for thread in english_subtitles_search_threads:
            thread.join()
    else:
        kodi_utils.logger("KODI-RD-IL", f"Skipping Searching for English subtitles...")
    
    # Extract subtitles in the desired order
    subtitles_websites_info = hebrew_subtitles_websites_info if HEBREW_SUBTITLES_FOUND else english_subtitles_websites_info
    unique_subtitles_list = []
    
    for website_info in subtitles_websites_info.values():
        subtitles = website_subtitles_dict.get(website_info['short_name'], [])
        unique_subtitles_list.extend(subtitle for subtitle in subtitles if subtitle not in unique_subtitles_list)
    
    kodi_utils.logger("KODI-RD-IL", f"unique_subtitles_list: {str(unique_subtitles_list)}")
    kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")

    # Write the unique subtitles list to the hebrew_subtitles_db cache table if it is not empty
    db_utils.write_unique_subtitles_to_hebrew_subtitles_db(unique_subtitles_list, website_subtitles_dict)
  
  
def strip_problematic_chars_from_subtitle_names_list(subtitles_list):

    """
    Removes problematic characters (e.g. apostrophes) from each string in a list of subtitle names.

    Args:
        subtitles_list (list): A list of subtitle names.

    Returns:
        list: A new list where each string in subtitles_list has been stripped of problematic characters.
    """

    return [subtitle_name.replace("'", "") for subtitle_name in subtitles_list]
        

def generate_subtitles_match_top_panel_text_for_sync_percent_match(total_external_subtitles_found_count, total_hebrew_embedded_subtitles_matches_count, total_subtitles_matches_count, total_quality_counts):

    """
    Generate a formatted string to display a notification on a Twilight results top panel.

    The function displays the number of subtitles found and the number of sources with a subtitle match percentage
    greater than or equal to the given minimum_sync_percent argument. The function also logs the number of sources 
    with matched subtitles.

    Args:
        total_external_subtitles_found_count (int): The total number of subtitles found.
        total_subtitles_found_count (int): The number of sources with a subtitle match percentage greater than or equal to the minimum_sync_percent.
        total_quality_counts (Dict[str, int]): A dictionary containing the count of each subtitle quality.
        minimum_sync_percent (int): The minimum percentage of subtitle match to display in the formatted string.

    Returns:
        str: A formatted string displaying the total number of subtitles found and sources with a subtitle match percentage
        greater than or equal to the given minimum_sync_percent.

    Example:
        >>> generate_subtitles_match_top_panel_text_for_sync_percent_match(10, 5, {"4K": 2, "1080p": 3, "720p": 0, "SD": 0}, 90)
        '[COLOR deepskyblue]נמצאו 10 כתוביות סך הכל[/COLOR] | [COLOR yellow]5 מקורות מעל 90% התאמה לכתוביות[/COLOR] | [COLOR yellow]מחפש התאמה מעל 90%[/COLOR] | [COLOR FF0166FF]SD: 0[/COLOR] | [COLOR FF3C9900]720P: 0[/COLOR] | [COLOR FF3CFA38]1080P: 3[/COLOR] | [COLOR FFFF00FE]4K: 2[/COLOR] | סך הכל '
    """
    
    global IS_SEARCHED_FROM_EXTERNAL
    if not IS_SEARCHED_FROM_EXTERNAL:
        return "[COLOR yellow]מקורות שהפעלת בעבר[/COLOR]", "[COLOR yellow]לרשימת מקורות מלאה עם התאמת כתוביות:[/COLOR]", "[COLOR cyan]לחץ על חיפוש מקורות מלא (בסוף הרשימה)[/COLOR]"
        
    HEBREW_SUBTITLES_FOUND = db_utils.hebrew_subtitles_db_has_hebrew_subtitles()
    
    total_subtitles_found_count = total_external_subtitles_found_count + total_hebrew_embedded_subtitles_matches_count
    
    hebrew_embedded_text_string = ""
    if total_hebrew_embedded_subtitles_matches_count > 0:
        hebrew_embedded_text_string = f" [COLOR cyan]({total_hebrew_embedded_subtitles_matches_count} מתרגום מובנה)[/COLOR]"
    
    results_language_text = "[COLOR deepskyblue]שפת חיפוש כתוביות:[/COLOR] "

    if not HEBREW_SUBTITLES_FOUND and not search_for_english_subtitles_when_no_hebrew_subtitles_found:
        results_language_text += "[COLOR deepskyblue]עברית[/COLOR]"
    else:
        results_language_text += (
            "[COLOR deepskyblue]עברית[/COLOR]"
            if HEBREW_SUBTITLES_FOUND
            else "[COLOR deepskyblue]אנגלית + תרגום מכונה[/COLOR] [COLOR red](אין חיצוניות בעברית)[/COLOR]"
        )

    total_subtitles_found_text = (
    f"[COLOR FFFE9900]נמצאה כתובית אחת{hebrew_embedded_text_string}[/COLOR]"
    if total_subtitles_found_count == 1
    else (
        f"[COLOR FFFE9900]נמצאו {total_subtitles_found_count} כתוביות סך הכל{hebrew_embedded_text_string}[/COLOR]"
        if total_subtitles_found_count > 0
        else "[COLOR red]לא נמצאו כתוביות לתוכן זה[/COLOR]"
    )
)
    
    subtitles_matched_count_text = (f"[COLOR yellow]לא נמצאו מקורות מעל {minimum_sync_percent}% סיכוי התאמה לכתוביות[/COLOR]"
                                   if total_subtitles_found_count > 0 and total_subtitles_matches_count == 0
                                   else "")
                                   
    if total_subtitles_matches_count > 0:
    
        # Get the counts for each quality from the total quality counts dictionary
        count_4k = total_quality_counts.get("4K", 0)
        count_1080p = total_quality_counts.get("1080p", 0)
        count_720p = total_quality_counts.get("720p", 0)
        count_sd = total_quality_counts.get("SD", 0)
        
        text_minimum_sync_percent = f"[COLOR yellow]כמות מקורות עם סיכוי התאמה מעל {minimum_sync_percent}% (לפי איכות):[/COLOR]"

        # Create a list to store the text messages for each quality
        quality_texts = []

        # Add the text for each quality to the list if the count is greater than 0
        if count_sd > 0:
            quality_texts.append(f"[COLOR FF0166FF]SD: {count_sd}[/COLOR]")
        if count_720p > 0:
            quality_texts.append(f"[COLOR FF3C9900]720P: {count_720p}[/COLOR]")
        if count_1080p > 0:
            quality_texts.append(f"[COLOR FF3CFA38]1080P: {count_1080p}[/COLOR]")
        if count_4k > 0:
            quality_texts.append(f"[COLOR FFFF00FE]4K: {count_4k}[/COLOR]")
            
        # Join the quality texts using " |" seperator
        subtitles_matched_count_text = " | ".join(quality_texts)
        
        subtitles_matched_count_text = f"{text_minimum_sync_percent} {subtitles_matched_count_text}"
        
    kodi_utils.logger("KODI-RD-IL", f"TWILIGHT sources with matched subtitles: {total_subtitles_matches_count}")
    kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
    
    return results_language_text, total_subtitles_found_text, subtitles_matched_count_text
    
    
def calculate_highest_sync_percent_and_set_match_text(total_subtitles_found_list, original_twilight_video_tagline, quality, hebrew_embedded_taglines):

    """
    Calculates the highest subtitle synchronization percentage between the subtitles found and the given TWILIGHT source, and returns
    the corresponding subtitle website name and sync percentage as a string. If the sync percentage is greater than or equal to 
    the minimum_sync_percent, sets the total_subtitles_found_count to 1 and returns the formatted subtitle_matches_text.

    Args:
        total_subtitles_found_list (List[str]): A list of all the subtitle sources found.
        original_twilight_video_tagline (str): The name of the original TWILIGHT source file.
        quality (str): The quality of the video file.

    Returns:
        Dict: A dictionary containing total_subtitles_found_count (an integer indicating the number of sources with a subtitle match percentage greater than or equal to minimum_sync_percent), subtitle_matches_text (a formatted string indicating the name of the subtitle website and the sync percentage), and the count for each quality.
        
    Example:
        >>> calculate_highest_sync_percent_and_set_match_text(["sub1", "sub2"], "TWILIGHT source", "1080p", 90)
        {
            "total_subtitles_found_count": 1,
            "subtitle_matches_text": '[B][COLOR deepskyblue]  SUBTITLE: [/COLOR][COLOR yellow]{matched_subtitle_website_name} {highest_sync_percent}% התאמה של[/COLOR][/B]',
            "4k_count": 5,
            "1080p_count": 1,
            "720p_count": 3,
            "sd_count": 0
        }
    """
    
    quality_counts_for_source = {
        "4K": 0,
        "1080p": 0,
        "720p": 0,
        "SD": 0
    }
    
    external_subtitles_matched_count = 0
    hebrew_embedded_subtitles_matched_count = 0
    subtitle_matches_text = ""
    
    global IS_SEARCHED_FROM_EXTERNAL
    if not IS_SEARCHED_FROM_EXTERNAL:
        return external_subtitles_matched_count, hebrew_embedded_subtitles_matched_count, subtitle_matches_text, quality_counts_for_source
    
    ############################################# HEBREW EMBEDDED TAGLINES #############################################
    
    # Checking first if video tagline matches embedded Hebrew taglines list. (which have 101% LOC embedded)
    if search_hebrew_subtitles_in_embedded and hebrew_embedded_taglines:
        
        is_hebrew_embedded_tagline_match_found = hebrew_embedded.check_match(original_twilight_video_tagline,hebrew_embedded_taglines)
        
        if is_hebrew_embedded_tagline_match_found:
            matched_subtitle_website_name = "[HEB|LOC]"
    
            hebrew_embedded_subtitles_matched_count = 1
            subtitle_matches_text = f"[B][COLOR deepskyblue]  SUBTITLE: [/COLOR][COLOR cyan]{matched_subtitle_website_name} תרגום מובנה[/COLOR][/B]"
            
            # Increment the quality count if a match is found
            if quality in quality_counts_for_source:
                quality_counts_for_source[quality] = 1
        
            kodi_utils.logger("KODI-RD-IL", f"EMBEDDED | Match found! SYNC PERCENT: 101% | For TWILIGHT Original Video Tagline: {original_twilight_video_tagline} (In Hebrew Embedded taglines repo).")
            kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
            
            return external_subtitles_matched_count, hebrew_embedded_subtitles_matched_count, subtitle_matches_text, quality_counts_for_source
            
    ############################################# EXTERNAL SUBTITLES #############################################
    
    if total_subtitles_found_list:
    
        highest_sync_percent, matched_subtitle_name, matched_subtitle_website_name  = calculate_highest_sync_percent_between_subtitles_and_twilight_source(total_subtitles_found_list, original_twilight_video_tagline, quality)
        
        if highest_sync_percent >= minimum_sync_percent:
        
            external_subtitles_matched_count = 1
            subtitle_matches_text = f"[B][COLOR deepskyblue]  SUBTITLE: [/COLOR][COLOR yellow]{matched_subtitle_website_name} {highest_sync_percent}% סיכוי התאמה של[/COLOR][/B]"
            
            # Increment the quality count if a match is found
            if quality in quality_counts_for_source:
                quality_counts_for_source[quality] = 1
            
            kodi_utils.logger("KODI-RD-IL", f"Match found! SYNC PERCENT: {highest_sync_percent}% | Between TWILIGHT Original Video Tagline: {original_twilight_video_tagline} To Subtitle Name: {matched_subtitle_name}")
            kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
            
    return external_subtitles_matched_count, hebrew_embedded_subtitles_matched_count, subtitle_matches_text, quality_counts_for_source


def calculate_highest_sync_percent_between_subtitles_and_twilight_source(total_subtitles_found_list, original_twilight_video_tagline, quality):

    """Calculates the highest synchronization percentage between the given subtitles and the given TWILIGHT source file.

    Args:
        total_subtitles_found_list (List[Tuple[str, str]]): A list of tuples, where each tuple contains the name of a subtitle and the name of the subtitle website.
        original_twilight_video_tagline (str): The name of the original TWILIGHT source file.
        quality (str): The quality of the video file.

    Returns:
        Tuple[float, str]: A tuple containing the highest synchronization percentage, the name of the subtitle and the name of the subtitle website with the highest percentage.

    Example:
        >>> calculate_highest_sync_percent_between_subtitles_and_twilight_source([("sub1", "website1"), ("sub2", "website2")], "TWILIGHT source", "1080p")
        (95.0, "website1")
    """
    
    # Reformat quality from Twilight to correct format.
    quality_mapping = {
        "4K": "2160p",
        "1080p": "1080p",
        "720p": "720p",
        "SD": "480p"
    }
    
    quality = quality_mapping.get(quality, quality)
    
    array_twilight_source_file_name = original_twilight_video_tagline.strip().replace("_",".").replace(" ",".").replace("+",".").replace("/",".").replace("-",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")

    highest_sync_percent = 0
    matched_subtitle_name = ""
    matched_subtitle_website_name = ""
    
    # Loop over all subtitles to find the one with the highest synchronization percentage.
    for subtitle_element in total_subtitles_found_list:
    
        subtitle_name, subtitle_website_name = subtitle_element
        
        # kodi_utils.logger("KODI-RD-IL", f"Calculating sync percentage match for subtitle name: {subtitle_name}")
        # Calculate sync percentage between subtitle and TWILIGHT source file.
        sync_percent = calculate_sync_percent_between_subtitles_and_twilight_source(subtitle_name, array_twilight_source_file_name, quality)
        
        # Get highest sync percent from results
        if sync_percent > highest_sync_percent:
            highest_sync_percent = sync_percent
            matched_subtitle_name = subtitle_name
            matched_subtitle_website_name = subtitle_website_name
        
    # kodi_utils.logger("KODI-RD-IL", f"HIGHEST SYNC PERCENT IS: {highest_sync_percent}% (BETWEEN TWILIGHT FILE NAME - {original_twilight_video_tagline} AND SUBTITLE NAME - {matched_subtitle_name})")
    
    return highest_sync_percent, matched_subtitle_name, matched_subtitle_website_name


def calculate_sync_percent_between_subtitles_and_twilight_source(subtitle_name, array_twilight_source_file_name, quality):

    """Calculates the synchronization percentage between the given subtitle and the given TWILIGHT source file, and returns the percentage.

    Args:
        subtitle_name (str): The name of the subtitle file.
        array_twilight_source_file_name (List[str]): The parts of the name of the TWILIGHT source file.
        quality (str): The quality of the video file.

    Returns:
        float: The synchronization percentage between the subtitle and the TWILIGHT source file.

    Example:
        >>> calculate_sync_percent_between_subtitles_and_twilight_source("sub1.srt", ["twilight", "source", "file", "1080p"], "1080p")
        85.0
    """
    
    # Reset array_twilight_source_file_name (remove quality / releases names)
    array_twilight_source_file_name = [element.strip().lower() for element in array_twilight_source_file_name if element != '']
    
    array_subtitle_name = subtitle_name.strip().replace(".srt",'').replace("_",".").replace(" ",".").replace("+",".").replace("/",".").replace("-",".").split(".")
    array_subtitle_name=[element.strip().lower() for element in array_subtitle_name if element != '']

    if quality not in array_twilight_source_file_name and quality in array_subtitle_name:
        array_twilight_source_file_name.append(quality)
        
    # Gives more weight to the ratio score to "release name" when comparing.
    for release_name in release_names:
    
        if release_name in array_twilight_source_file_name and release_name in array_subtitle_name:
            
            array_twilight_source_file_name.append(release_name)
            array_twilight_source_file_name.append(release_name)
            array_twilight_source_file_name.append(release_name)
            array_subtitle_name.append(release_name)
            array_subtitle_name.append(release_name)
            array_subtitle_name.append(release_name)


    sync_percent = string_utils.similar(array_twilight_source_file_name, array_subtitle_name)
    
    return sync_percent