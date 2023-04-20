        
def generate_subtitles_match_top_panel_text_for_100_match(total_subtitles_found_count, subtitles_matched_count):
    """Generates a text string for a Fen results top panel notification displaying the number of subtitles found and sources with 100% subtitle match.

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
        
    kodi_utils.logger("KODI-RD-IL", f"FEN sources with matched subtitles: {subtitles_matched_count}")
    kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
    
    return total_subtitles_found_text + subtitles_matched_count_text
    
    
def subtitle_name_to_fen_source_file_name_matching(total_subtitles_found_list, original_fen_source_file_name):

    """
    Matches the subtitle name with the FEN source file name.

    Args:
    - total_subtitles_found_list (list): A list of tuples containing subtitle names and website names.
    - original_fen_source_file_name (str): The original name of the FEN source file.

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
            fen_source_file_name = string_utils.clean_string(original_fen_source_file_name)
            
            # Check if the cleaned up subtitle name is an exact match to the cleaned up source file name
            if current_subtitle_name == fen_source_file_name:
                
                #kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
                kodi_utils.logger("KODI-RD-IL", f"{website_name} BEFORE STRIP - current_subtitle_name: {subtitle_name}")
                kodi_utils.logger("KODI-RD-IL", f"{website_name} BEFORE STRIP - fen_source_file_name: {original_fen_source_file_name}")
            
                kodi_utils.logger("KODI-RD-IL", f"{website_name} AFTER STRIP - current_subtitle_name: {current_subtitle_name}")  
                kodi_utils.logger("KODI-RD-IL", f"{website_name} AFTER STRIP - fen_source_file_name: {fen_source_file_name}")
                
                kodi_utils.logger("KODI-RD-IL", f"{website_name} MATCH EQUAL: {current_subtitle_name} IN {fen_source_file_name}")
                kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
                
                # Set the subtitle matches text and count
                subtitles_matched_count = 1
                subtitle_matches_text = f"[B][COLOR deepskyblue]  SUBTITLE: [/COLOR][COLOR yellow]{website_name} התאמה של 100%[/COLOR][/B]"
                
                # Break out of the loop since we found a match
                break
            
            # Check if the cleaned up subtitle name is contained within the cleaned up source file name
            elif current_subtitle_name in fen_source_file_name:
                
                #kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
                kodi_utils.logger("KODI-RD-IL", f"{website_name} BEFORE STRIP - current_subtitle_name: {subtitle_name}")
                kodi_utils.logger("KODI-RD-IL", f"{website_name} BEFORE STRIP - fen_source_file_name: {original_fen_source_file_name}")
            
                kodi_utils.logger("KODI-RD-IL", f"{website_name} AFTER STRIP - current_subtitle_name: {current_subtitle_name}")  
                kodi_utils.logger("KODI-RD-IL", f"{website_name} AFTER STRIP - fen_source_file_name: {fen_source_file_name}")
                
                kodi_utils.logger("KODI-RD-IL", f"{website_name} MATCH INSIDE: {current_subtitle_name} IN {fen_source_file_name}")
                kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
                
                # Set the subtitle matches text and count
                subtitles_matched_count = 1
                subtitle_matches_text = f"[B][COLOR deepskyblue]  SUBTITLE: [/COLOR][COLOR yellow]{website_name} התאמה של 100%[/COLOR][/B]"
                
                # Break out of the loop since we found a match
                break

    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"Error in subtitle matching: {e}")
        
    return subtitles_matched_count, subtitle_matches_text