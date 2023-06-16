########### Imports #####################
from modules import kodi_utils
from modules.kodi_utils import hebrew_subtitles_db, database


def write_unique_subtitles_to_hebrew_subtitles_db(unique_subtitles_list, website_subtitles_dict):

    """
    Write unique subtitles from `unique_subtitles_list` to the 'current_subtitles_cache' table in 'hebrew_subtitles.db'.

    Args:
    unique_subtitles_list (list): A list of unique subtitles to be written to the database.
    website_subtitles_dict (dict): A dictionary containing website short names as keys and corresponding subtitle lists as values.

    Returns:
    None
    """
    
    # Clear the cache table in the database before writing new subtitles
    clear_hebrew_subtitles_db_cache()
    
    try:
        # Connect to the database and create a cursor
        dbcon = database.connect(hebrew_subtitles_db)
        dbcur = dbcon.cursor()
        
        if unique_subtitles_list:
            # Iterate through each subtitle in `unique_subtitles_list`
            for subtitle_name in unique_subtitles_list:
                website_name = None
                for website_short_name, website_subtitles_list in website_subtitles_dict.items():
                    if subtitle_name in website_subtitles_list:
                        website_name = website_short_name
                        break
                if website_name:
                    # Insert the subtitle and website name into the cache table
                    dbcur.execute("INSERT INTO current_subtitles_cache Values ('%s','%s')"%(subtitle_name, website_name))
                    dbcon.commit()
                    
            # Close the database connection
            dbcon.close()
            
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"Error in writing subtitles to hebrew_subtitles_db: {str(e)}")
    
 
def clear_hebrew_subtitles_db_cache():

    """
    Creates the 'current_subtitles_cache' table in 'hebrew_subtitles_db' if it doesn't exist and clears its contents.
    This function first creates a table called 'current_subtitles_cache' in the 'hebrew_subtitles_db' if it doesn't exist. Then it clears all the contents of the table, effectively clearing the cache.

    Args:
    None

    Returns:
    None
    """
    
    try:
        dbcon = database.connect(hebrew_subtitles_db)
        dbcur = dbcon.cursor()
        
        # Create hebrew_subtitles_db if not exist
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s ( ""subtitle_name TEXT ,""website_name TEXT);" % ('current_subtitles_cache'))
        dbcon.commit()
        
        # Clear hebrew_subtitles_db
        dbcon.execute("DELETE FROM current_subtitles_cache")
        dbcon.commit()
        
        dbcon.close()
        kodi_utils.logger("KODI-RD-IL", "Cleared hebrew_subtitles_db cache")
        
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"Error Clearing hebrew_subtitles_db cache: {str(e)}")

    
def get_total_subtitles_found_list_from_hebrew_subtitles_db():

    """
    This function connects to the 'hebrew_subtitles_db' database and retrieves a list of all the subtitles found in the
    'current_subtitles_cache' table. If there are no subtitles found, an empty list is returned. If there is an error while
    reading the database, an error message is logged and an empty list is returned.

    Returns:
    total_subtitles_found_list: A list of all the subtitles found in the 'current_subtitles_cache' table.

    """
    try:
        # Connect to the database and get the current subtitles cache
        dbcon = database.connect(hebrew_subtitles_db)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM current_subtitles_cache")
        total_subtitles_found_list = dbcur.fetchall()

        # If there are subtitles found in the cache, get the count
        if not total_subtitles_found_list:
            return []
            
        return total_subtitles_found_list
        
    except Exception as e:
        # Log any errors that occur while reading the database
        kodi_utils.logger("KODI-RD-IL", f"Error while reading hebrew_subtitles_db and setting total_subtitles_found_count parameter: {str(e)}")
        return []
          

def clear_fen_providers_db():

    """Clears the db cache for FEN providers by deleting the `providers.db` file used by the FEN Kodi addon.
    
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
    
