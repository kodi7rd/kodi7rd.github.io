########### Imports #####################
from modules import kodi_utils
import time
from modules import settings
#########################################

########### KODI-RD-IL Imports ##########
from kodirdil import hebrew_subtitles_search_utils
#########################################

def create_search_hebrew_subtitles_thread(media_type, title, season, episode, year, tmdb_id, imdb_id):

    """Creates a thread to search for Hebrew subtitles for a media item.

    Args:
    media_type (str): The type of media item, either 'movie' or 'tv'.
    title (str): The title of the media item.
    season (int): The season number for a TV show, or 0 for a movie.
    episode (int): The episode number for a TV show, or 0 for a movie.
    year (int): The year the media item was released.
    tmdb_id (str): The TMDb ID of the media item.
    imdb_id (str): The TMDb ID of the media item.

    Returns:
    threading.Thread: The created thread for searching Hebrew subtitles.

    Example:
    >>> create_search_hebrew_subtitles_thread('tv', 'Breaking Bad', 1, 1, 2008, 12345)
    """
    
    if media_type == 'movie':
        hebrew_subtitles_search_arguments = ('movie', title, '0', '0', year, tmdb_id, imdb_id)
        kodi_utils.logger("KODI-RD-IL", f"START search_hebrew_subtitles_thread - Calling search_hebrew_subtitles_for_selected_media() for Movie: {title} | Year: {year} | TMDb ID: {tmdb_id} | IMDb ID: {imdb_id}")
    else:
        hebrew_subtitles_search_arguments = ('tv', title, season, episode, year, tmdb_id, imdb_id)
        kodi_utils.logger("KODI-RD-IL", f"START search_hebrew_subtitles_thread - Calling search_hebrew_subtitles_for_selected_media() for TV Show: {title} Season {season} Episode {episode} | Year: {year} | TMDb ID: {tmdb_id} | IMDb ID: {imdb_id}")
    
    try:
        search_hebrew_subtitles_thread = kodi_utils.Thread(target=hebrew_subtitles_search_utils.search_hebrew_subtitles_for_selected_media, args=hebrew_subtitles_search_arguments)
        
        # return the thread object and start time
        return search_hebrew_subtitles_thread
        
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"ERROR while creating search_hebrew_subtitles_thread and calling search_hebrew_subtitles_for_selected_media(): {str(e)}")
        return None


def manage_search_hebrew_subtitles_thread(search_hebrew_subtitles_thread, search_hebrew_subtitles_thread_start_time):

    """Manage the search_hebrew_subtitles_thread to prevent it from running indefinitely. 

    This function checks if the thread is still running and if so, waits for 200ms before checking again. 
    This process is repeated until the thread has finished running or if it runs longer than 10 seconds, 
    at which point the function forcibly stops the thread. The function logs messages to the Kodi log 
    to indicate the status of the thread.

    Args:
        search_hebrew_subtitles_thread (threading.Thread): The thread to be managed.
        search_hebrew_subtitles_thread_start_time (float): The start time of the thread in seconds since the Epoch.

    Returns:
        None

    Example:
        To manage the search_hebrew_subtitles_thread, call this function and pass in the thread object:

        >>> manage_search_hebrew_subtitles_thread(search_hebrew_subtitles_thread, search_hebrew_subtitles_thread_start_time)
    """
    
    try:
        count = 0
        while search_hebrew_subtitles_thread is not None and search_hebrew_subtitles_thread.is_alive():
            #kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
            kodi_utils.logger("KODI-RD-IL", "SLEEP search_hebrew_subtitles_thread - Still alive. sleeping 100ms...")
            kodi_utils.sleep(100)
            count += 1
            if count > 150:
                kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
                kodi_utils.logger("KODI-RD-IL", "FORCE STOP search_hebrew_subtitles_thread -  runs longer than 15 seconds. stopping the thread...")
                break
                
        # calculate the total run time
        search_hebrew_subtitles_thread_elapsed_time = time.time() - search_hebrew_subtitles_thread_start_time
        kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
        kodi_utils.logger("KODI-RD-IL", f"END search_hebrew_subtitles_thread - Finished. Total run time: {search_hebrew_subtitles_thread_elapsed_time:.2f} seconds.")
        
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"###########################################################################################")
        kodi_utils.logger("KODI-RD-IL", f"ERROR search_hebrew_subtitles_thread - Error managing search_hebrew_subtitles_thread loop: {str(e)}")
        
        
