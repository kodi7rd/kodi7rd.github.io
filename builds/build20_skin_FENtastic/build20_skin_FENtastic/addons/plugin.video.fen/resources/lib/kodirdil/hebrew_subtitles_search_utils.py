########### Imports #####################
from modules import kodi_utils
import requests
import json
from collections import OrderedDict

########### KODI-RD-IL Imports ##########
from kodirdil import string_utils
from kodirdil import db_utils
# Import hebrew subtitle search functions
from kodirdil.websites import ktuvit
from kodirdil.websites import wizdom
from kodirdil.websites import opensubtitles
from kodirdil.websites import subscene
#########################################

########### Settings ####################
minimum_sync_percent = int(kodi_utils.get_setting('minimum_hebrew_subtitles_sync_percentage_match_slider', '80'))
show_only_qualities_with_matches_found = kodi_utils.get_setting('show_only_qualities_with_matches_found', 'false') == 'true'
#########################################

########### Constants ###################
hebrew_subtitles_websites_info = {
    'ktuvit': {'website': ktuvit, 'short_name': '[KT]'},
    'wizdom': {'website': wizdom, 'short_name': '[WIZ]'},
    'opensubtitles': {'website': opensubtitles, 'short_name': '[OPS]'},
    'subscene': {'website': subscene, 'short_name': '[SS]'}
    }
    
    
release_names = ['blueray','bluray','blu-ray','bdrip','brrip','brip',
                 'hdtv','hdtvrip','pdtv','tvrip','hdrip','hd-rip',
                 'web','web-dl','web dl','web-dlrip','webrip','web-rip',
                 'dvdr','dvd-r','dvd-rip','dvdrip','cam','hdcam','cam-rip','camrip','screener','dvdscr','dvd-full',
                 'telecine','hdts','telesync']
#########################################

def search_hebrew_subtitles_for_selected_media(media_type, title, season, episode, year, tmdb_id):

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
    
    media_metadata = {
        "media_type": media_type,
        "title": title.replace("%20"," ").replace("%27","'"),
        "season": season,
        "episode": episode,
        "year": year,
        "tmdb_id": tmdb_id,
        "imdb_id": get_imdb_id(media_type, tmdb_id)
    }
    
    kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
    
    # Search for subtitles in all websites and combine them into a single list
    combined_subtitles_list = []
    website_subtitles_dict = {}
    for website_info in hebrew_subtitles_websites_info.values():
        try:
            hebrew_subtitles_list = website_info['website'].search_hebrew_subtitles(media_metadata)
            website_subtitles_dict[website_info['short_name']] = hebrew_subtitles_list
            combined_subtitles_list.extend(hebrew_subtitles_list)
            kodi_utils.logger("KODI-RD-IL", f"{website_info['short_name']}_subtitles_list: {str(hebrew_subtitles_list)}")   
            kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
            
        except Exception as e:
            kodi_utils.logger("KODI-RD-IL", f"Error in searching subtitles from {website_info['website']}: {str(e)}")
            kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
    
    # Convert the combined list to an OrderedDict to remove duplicates while preserving order
    unique_subtitles_dict = OrderedDict.fromkeys(combined_subtitles_list)
    
    # Convert the set back to a list
    unique_subtitles_list = list(unique_subtitles_dict.keys())
    
    unique_subtitles_list = strip_problematic_chars_from_subtitle_names_list(unique_subtitles_list)
    
    kodi_utils.logger("KODI-RD-IL", f"unique_subtitles_list: {str(unique_subtitles_list)}")
    kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
    
    # Write the unique subtitles list to the hebrew_subtitles_db cache table if it is not empty
    db_utils.write_unique_subtitles_to_hebrew_subtitles_db(unique_subtitles_list, website_subtitles_dict)
  
  
def strip_problematic_chars_from_subtitle_names_list(unique_subtitles_list):

    """
    Removes problematic characters (e.g. apostrophes) from each string in a list of subtitle names.

    Args:
        unique_subtitles_list (list): A list of subtitle names.

    Returns:
        list: A new list where each string in unique_subtitles_list has been stripped of problematic characters.
    """

    return [subtitle_name.replace("'", "") for subtitle_name in unique_subtitles_list]
    
    
def get_imdb_id(media_type, tmdb_id):

    """Retrieves the IMDb ID for a media item from its TMDb ID.

    Args:
    media_type (str): The type of media item, either 'movie' or 'tv'.
    tmdb_id (int): The TMDb ID of the media item.

    Returns:
    str: The IMDb ID of the media item, if available. Otherwise, an empty string is returned.

    Example:
    >>> get_imdb_id('movie', 12345)
    'tt1234567'
    """

    imdb_api_url = f'https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key=34142515d9d23817496eeb4ff1d223d0&append_to_response=external_ids'
    try:
        imdb_api_reponse = requests.get(imdb_api_url).json()
        imdb_id = imdb_api_reponse['external_ids'].get('imdb_id', '')
        kodi_utils.logger("KODI-RD-IL", f"get_imdb_id function: TMDb ID: {tmdb_id} | IMDb ID: {imdb_id}")
        return imdb_id
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"Error in getting imdb_id from TMDb API: {str(e)}")
        return ''
        

def generate_subtitles_match_top_panel_text_for_sync_percent_match(total_subtitles_found_count, subtitles_matched_count, total_quality_counts):

    """
    Generate a formatted string to display a notification on a Fen results top panel.

    The function displays the number of subtitles found and the number of sources with a subtitle match percentage
    greater than or equal to the given minimum_sync_percent argument. The function also logs the number of sources 
    with matched subtitles.

    Args:
        total_subtitles_found_count (int): The total number of subtitles found.
        subtitles_matched_count (int): The number of sources with a subtitle match percentage greater than or equal to the minimum_sync_percent.
        total_quality_counts (Dict[str, int]): A dictionary containing the count of each subtitle quality.
        minimum_sync_percent (int): The minimum percentage of subtitle match to display in the formatted string.

    Returns:
        str: A formatted string displaying the total number of subtitles found and sources with a subtitle match percentage
        greater than or equal to the given minimum_sync_percent.

    Example:
        >>> generate_subtitles_match_top_panel_text_for_sync_percent_match(10, 5, {"4K": 2, "1080p": 3, "720p": 0, "SD": 0}, 90)
        '[COLOR deepskyblue]נמצאו 10 כתוביות סך הכל[/COLOR] | [COLOR yellow]5 מקורות מעל 90% התאמה לכתוביות[/COLOR] | [COLOR yellow]מחפש התאמה מעל 90%[/COLOR] | [COLOR FF0166FF]SD: 0[/COLOR] | [COLOR FF3C9900]720P: 0[/COLOR] | [COLOR FF3CFA38]1080P: 3[/COLOR] | [COLOR FFFF00FE]4K: 2[/COLOR] | סך הכל '
    """
    
    total_subtitles_found_text = (f"[COLOR deepskyblue]נמצאו {total_subtitles_found_count} כתוביות סך הכל[/COLOR] | " 
                                  if total_subtitles_found_count > 0 
                                  else "[B][COLOR deepskyblue]לא נמצאו כתוביות לתוכן זה[/COLOR] | סך הכל ")

    subtitles_matched_count_text = (f"[COLOR yellow]לא נמצאו מקורות מעל {minimum_sync_percent}% התאמה לכתוביות[/COLOR] | סך הכל "
                                   if total_subtitles_found_count > 0 and subtitles_matched_count == 0
                                   else "")
    if subtitles_matched_count > 0:
    
        # Get the counts for each quality from the total quality counts dictionary
        count_4k = total_quality_counts.get("4K", 0)
        count_1080p = total_quality_counts.get("1080p", 0)
        count_720p = total_quality_counts.get("720p", 0)
        count_sd = total_quality_counts.get("SD", 0)
        
        text_minimum_sync_percent = f"[COLOR yellow]כמות מקורות עם התאמה מעל {minimum_sync_percent}% (לפי איכות):[/COLOR] |"
        text_sd = f"[COLOR FF0166FF] SD: {count_sd}[/COLOR] |" if not show_only_qualities_with_matches_found or count_sd > 0 else ""
        text_720p = f"[COLOR FF3C9900] 720P: {count_720p}[/COLOR] |" if not show_only_qualities_with_matches_found or count_720p > 0 else ""
        text_1080p = f"[COLOR FF3CFA38] 1080P: {count_1080p}[/COLOR] |" if not show_only_qualities_with_matches_found or count_1080p > 0 else ""
        text_4k = f"[COLOR FFFF00FE] 4K: {count_4k}[/COLOR] |" if not show_only_qualities_with_matches_found or count_4k > 0 else ""
        
        subtitles_matched_count_text = (f"{text_minimum_sync_percent}{text_sd}{text_720p}{text_1080p}{text_4k} סך הכל ")
        
    kodi_utils.logger("KODI-RD-IL", f"FEN sources with matched subtitles: {subtitles_matched_count}")
    kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
    
    return total_subtitles_found_text + subtitles_matched_count_text
    
    
def calculate_highest_sync_percent_and_set_match_text(total_subtitles_found_list, original_fen_source_file_name, quality):

    """
    Calculates the highest subtitle synchronization percentage between the subtitles found and the given FEN source, and returns
    the corresponding subtitle website name and sync percentage as a string. If the sync percentage is greater than or equal to 
    the minimum_sync_percent, sets the subtitles_matched_count to 1 and returns the formatted subtitle_matches_text.

    Args:
        total_subtitles_found_list (List[str]): A list of all the subtitle sources found.
        original_fen_source_file_name (str): The name of the original FEN source file.
        quality (str): The quality of the video file.

    Returns:
        Dict: A dictionary containing subtitles_matched_count (an integer indicating the number of sources with a subtitle match percentage greater than or equal to minimum_sync_percent), subtitle_matches_text (a formatted string indicating the name of the subtitle website and the sync percentage), and the count for each quality.
        
    Example:
        >>> calculate_highest_sync_percent_and_set_match_text(["sub1", "sub2"], "FEN source", "1080p", 90)
        {
            "subtitles_matched_count": 1,
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
    
    subtitles_matched_count = 0
    subtitle_matches_text = ""

    highest_sync_percent, matched_subtitle_name, matched_subtitle_website_name  = calculate_highest_sync_percent_between_subtitles_and_fen_source(total_subtitles_found_list, original_fen_source_file_name, quality)
    
    if highest_sync_percent >= minimum_sync_percent:
    
        subtitles_matched_count = 1
        subtitle_matches_text = f"[B][COLOR deepskyblue]  SUBTITLE: [/COLOR][COLOR yellow]{matched_subtitle_website_name} {highest_sync_percent}% התאמה של[/COLOR][/B]"
        
        # Increment the quality count if a match is found
        if quality in quality_counts_for_source:
            quality_counts_for_source[quality] = 1
        
        kodi_utils.logger("KODI-RD-IL", f"Match found! SYNC PERCENT: {highest_sync_percent} | Between FEN Original Source File Name: {original_fen_source_file_name} To Subtitle Name: {matched_subtitle_name}")
        kodi_utils.logger("KODI-RD-IL", f"To Subtitle Name: {matched_subtitle_name}")
        kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
        
    return subtitles_matched_count, subtitle_matches_text, quality_counts_for_source


def calculate_highest_sync_percent_between_subtitles_and_fen_source(total_subtitles_found_list, original_fen_source_file_name, quality):

    """Calculates the highest synchronization percentage between the given subtitles and the given FEN source file.

    Args:
        total_subtitles_found_list (List[Tuple[str, str]]): A list of tuples, where each tuple contains the name of a subtitle and the name of the subtitle website.
        original_fen_source_file_name (str): The name of the original FEN source file.
        quality (str): The quality of the video file.

    Returns:
        Tuple[float, str]: A tuple containing the highest synchronization percentage, the name of the subtitle and the name of the subtitle website with the highest percentage.

    Example:
        >>> calculate_highest_sync_percent_between_subtitles_and_fen_source([("sub1", "website1"), ("sub2", "website2")], "FEN source", "1080p")
        (95.0, "website1")
    """
    
    # Reformat quality from Fen to correct format.
    quality_mapping = {
        "4K": "2160p",
        "1080p": "1080p",
        "720p": "720p",
        "SD": "480p"
    }
    
    quality = quality_mapping.get(quality, quality)
    
    array_fen_source_file_name = original_fen_source_file_name.strip().replace("_",".").replace(" ",".").replace("+",".").replace("/",".").replace(".avi","").replace(".mp4","").replace(".mkv","").split(".")

    highest_sync_percent = 0
    matched_subtitle_name = ""
    matched_subtitle_website_name = ""
    
    # Loop over all subtitles to find the one with the highest synchronization percentage.
    for subtitle_element in total_subtitles_found_list:
    
        subtitle_name, subtitle_website_name = subtitle_element
        
        # kodi_utils.logger("KODI-RD-IL", f"Calculating sync percentage match for subtitle name: {subtitle_name}")
        # Calculate sync percentage between subtitle and FEN source file.
        sync_percent = calculate_sync_percent_between_subtitles_and_fen_source(subtitle_name, array_fen_source_file_name, quality)
        
        # Get highest sync percent from results
        if sync_percent > highest_sync_percent:
            highest_sync_percent = sync_percent
            matched_subtitle_name = subtitle_name
            matched_subtitle_website_name = subtitle_website_name
        
    # kodi_utils.logger("KODI-RD-IL", f"HIGHEST SYNC PERCENT IS: {highest_sync_percent}% (BETWEEN FEN FILE NAME - {original_fen_source_file_name} AND SUBTITLE NAME - {matched_subtitle_name})")
    
    return highest_sync_percent, matched_subtitle_name, matched_subtitle_website_name


def calculate_sync_percent_between_subtitles_and_fen_source(subtitle_name, array_fen_source_file_name, quality):

    """Calculates the synchronization percentage between the given subtitle and the given FEN source file, and returns the percentage.

    Args:
        subtitle_name (str): The name of the subtitle file.
        array_fen_source_file_name (List[str]): The parts of the name of the FEN source file.
        quality (str): The quality of the video file.

    Returns:
        float: The synchronization percentage between the subtitle and the FEN source file.

    Example:
        >>> calculate_sync_percent_between_subtitles_and_fen_source("sub1.srt", ["fen", "source", "file", "1080p"], "1080p")
        85.0
    """
    
    # Reset array_fen_source_file_name (remove quality / releases names)
    array_fen_source_file_name = [element.strip().lower() for element in array_fen_source_file_name if element != '']
    
    array_subtitle_name = subtitle_name.strip().replace(".srt",'').replace("_",".").replace(" ",".").replace("+",".").replace("/",".").split(".")
    array_subtitle_name=[element.strip().lower() for element in array_subtitle_name if element != '']

    if quality not in array_fen_source_file_name and quality in array_subtitle_name:
        array_fen_source_file_name.append(quality)
        
    # Gives more weight to the ratio score to "release name" when comparing.
    for release_name in release_names:
    
        if release_name in array_fen_source_file_name and release_name in array_subtitle_name:
            
            array_fen_source_file_name.append(release_name)
            array_fen_source_file_name.append(release_name)
            array_fen_source_file_name.append(release_name)
            array_subtitle_name.append(release_name)
            array_subtitle_name.append(release_name)
            array_subtitle_name.append(release_name)


    sync_percent = string_utils.similar(array_fen_source_file_name, array_subtitle_name)
    
    return sync_percent