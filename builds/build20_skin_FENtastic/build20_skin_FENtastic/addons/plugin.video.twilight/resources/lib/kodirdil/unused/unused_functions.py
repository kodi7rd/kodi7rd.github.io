def filter_problematic_subtitle_names_list(unique_subtitles_list, media_type, title, season, episode, year):

    """
    Filter a list of subtitles to remove problematic ones with short names.

    Args:
        unique_subtitles_list (list): A list of unique subtitle names.
        media_type (str): The type of media (e.g., movie, tvshow).
        title (str): The title of the media.
        season (str): The season of the media (if applicable).
        episode (str): The episode of the media (if applicable).
        year (str): The year of the media (if applicable).

    Returns:
        list: A filtered list of subtitles that have a name length greater than the length of the stripped media name.

    Example: top.gun.maverick.2022.srt
    """
    
    stripped_media_name = string_utils.strip_media_name(media_type, title, season, episode, year)
    stripped_media_name_length = len(stripped_media_name)
    kodi_utils.logger("KODI-RD-IL", f"stripped_media_name_length: {stripped_media_name_length}")
    kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
    
    # Filter the unique subtitles list to only include subtitles whose name length is greater than stripped_media_name_length
    return [subtitle_name.replace("'", "") for subtitle_name in unique_subtitles_list if len(string_utils.clean_string(subtitle_name)) > stripped_media_name_length]
    
    
def generate_subtitles_match_top_panel_text_for_100_match(total_subtitles_found_count, subtitles_matched_count):
    """Generates a text string for a Twilight results top panel notification displaying the number of subtitles found and sources with 100% subtitle match.

    Args:
    total_subtitles_found_count (int): The total number of subtitles found.
    subtitles_matched_count (int): The number of sources with 100% subtitle match.

    Returns:
    str: A formatted string displaying the number of subtitles found and sources with 100% subtitle match.

    Example:
    >>> generate_subtitles_match_top_panel_text(10, 5)
    '[COLOR deepskyblue]נמצאו 10 כתוביות סך הכל[/COLOR] | [COLOR yellow]5 מקורות עם 100% התאמה לכתוביות[/COLOR] |'
    """
    if total_subtitles_found_count > 0:
        total_subtitles_found_text = f"[COLOR deepskyblue]נמצאו {total_subtitles_found_count} כתוביות סך הכל[/COLOR] | "
    else:
        total_subtitles_found_text = ""
        
    if subtitles_matched_count > 0:
        subtitles_matched_count_text = f"[COLOR yellow]{subtitles_matched_count} מקורות עם 100% התאמה לכתוביות[/COLOR] | "
    else:
        subtitles_matched_count_text = f"[COLOR yellow] לא נמצאו מקורות עם 100% התאמה לכתוביות[/COLOR] | "
        
    kodi_utils.logger("KODI-RD-IL", f"TWILIGHT sources with matched subtitles: {subtitles_matched_count}")
    kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
    
    return total_subtitles_found_text + subtitles_matched_count_text
    
    
def subtitle_name_to_twilight_source_file_name_matching(total_subtitles_found_list, original_twilight_video_tagline):

    """
    Matches the subtitle name with the TWILIGHT source file name.

    Args:
    - total_subtitles_found_list (list): A list of tuples containing subtitle names and website names.
    - original_twilight_video_tagline (str): The original name of the TWILIGHT source file.

    Returns:
    - subtitles_matched_count (int): The count of matched subtitles. 
    - subtitle_matches_text (str): A string containing the details of matched subtitle, if any.
    """
    
    subtitles_matched_count = 0
    subtitle_matches_text = ""
    
    try:
        ############KODI-RD-IL###################
        # Iterate through the list of subtitle and website names
        for subtitle_name,website_name in total_subtitles_found_list:
            
            # Clean up the subtitle name and the source file name using the clean_string function
            current_subtitle_name = string_utils.clean_string(subtitle_name)
            twilight_source_file_name = string_utils.clean_string(original_twilight_video_tagline)
            
            # Check if the cleaned up subtitle name is an exact match to the cleaned up source file name
            if current_subtitle_name == twilight_source_file_name:
                
                #kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
                kodi_utils.logger("KODI-RD-IL", f"{website_name} BEFORE STRIP - current_subtitle_name: {subtitle_name}")
                kodi_utils.logger("KODI-RD-IL", f"{website_name} BEFORE STRIP - twilight_source_file_name: {original_twilight_video_tagline}")
            
                kodi_utils.logger("KODI-RD-IL", f"{website_name} AFTER STRIP - current_subtitle_name: {current_subtitle_name}")  
                kodi_utils.logger("KODI-RD-IL", f"{website_name} AFTER STRIP - twilight_source_file_name: {twilight_source_file_name}")
                
                kodi_utils.logger("KODI-RD-IL", f"{website_name} MATCH EQUAL: {current_subtitle_name} IN {twilight_source_file_name}")
                kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
                
                # Set the subtitle matches text and count
                subtitles_matched_count = 1
                subtitle_matches_text = f"[B][COLOR deepskyblue]  SUBTITLE: [/COLOR][COLOR yellow]{website_name} התאמה של 100%[/COLOR][/B]"
                
                # Break out of the loop since we found a match
                break
            
            # Check if the cleaned up subtitle name is contained within the cleaned up source file name
            elif current_subtitle_name in twilight_source_file_name:
                
                #kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
                kodi_utils.logger("KODI-RD-IL", f"{website_name} BEFORE STRIP - current_subtitle_name: {subtitle_name}")
                kodi_utils.logger("KODI-RD-IL", f"{website_name} BEFORE STRIP - twilight_source_file_name: {original_twilight_video_tagline}")
            
                kodi_utils.logger("KODI-RD-IL", f"{website_name} AFTER STRIP - current_subtitle_name: {current_subtitle_name}")  
                kodi_utils.logger("KODI-RD-IL", f"{website_name} AFTER STRIP - twilight_source_file_name: {twilight_source_file_name}")
                
                kodi_utils.logger("KODI-RD-IL", f"{website_name} MATCH INSIDE: {current_subtitle_name} IN {twilight_source_file_name}")
                kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
                
                # Set the subtitle matches text and count
                subtitles_matched_count = 1
                subtitle_matches_text = f"[B][COLOR deepskyblue]  SUBTITLE: [/COLOR][COLOR yellow]{website_name} התאמה של 100%[/COLOR][/B]"
                
                # Break out of the loop since we found a match
                break

    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"Error in subtitle matching: {e}")
        
    return subtitles_matched_count, subtitle_matches_text
          

def clear_twilight_providers_db():

    """Clears the db cache for TWILIGHT providers by deleting the `providers.db` file used by the TWILIGHT Kodi addon.
    
    Args:
        None

    Returns:
        None
    """
    # Clear providers cache
    try:
        from caches.providers_cache import ExternalProvidersCache
        ExternalProvidersCache().delete_cache(silent=True)
        kodi_utils.logger("KODI-RD-IL", "Cleared providers.db cache")
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"Error clearing providers.db cache: {str(e)}")


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