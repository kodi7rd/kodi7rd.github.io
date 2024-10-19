########### Imports #####################
from modules import kodi_utils
from modules.kodi_utils import hebrew_subtitles_db, media_metadata_db, database


def write_unique_subtitles_to_hebrew_subtitles_db(unique_subtitles_list, website_subtitles_dict):

    """
    Write unique subtitles from `unique_subtitles_list` to the 'current_subtitles_cache' table in 'twilight_hebrew_subtitles.db'.

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
        
        
def write_current_media_metadata_to_media_metadata_db(media_type, title, season, episode, year, tmdb_id):

    """
    Write current media metadata to the 'current_media_metadata_cache' table in the database.
    
    Args:
    media_type (TEXT)
    title (TEXT)
    season (TEXT)
    episode (TEXT)
    year (TEXT)
    tmdb_id (TEXT)

    Returns:
    None
    """
    
    # Clear the cache table in the database before writing
    clear_media_metadata_db_cache()
    
    try:
        # Connect to the database and create a cursor
        dbcon = database.connect(media_metadata_db)
        dbcur = dbcon.cursor()
        
        # dbcur.execute("INSERT INTO current_media_metadata_cache Values ('%s')"%(media_type))
        
        # Insert the media metadata into the table
        dbcur.execute(
            "INSERT INTO current_media_metadata_cache VALUES (?, ?, ?, ?, ?, ?)",
            (media_type, title, season, episode, year, tmdb_id)
        )
        
        dbcon.commit()
                    
        # Close the database connection
        dbcon.close()
            
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"EMBEDDED | Error in writing to media_metadata_db: {str(e)}")
    
 
def clear_media_metadata_db_cache():

    """
    Creates the 'current_media_metadata_cache' table in 'media_metadata_db' if it doesn't exist and clears its contents.
    This function first creates a table called 'current_media_metadata_cache' in the 'media_metadata_db' if it doesn't exist. Then it clears all the contents of the table, effectively clearing the cache.

    Args:
    None

    Returns:
    None
    """
    
    try:
        dbcon = database.connect(media_metadata_db)
        dbcur = dbcon.cursor()
        
        # Create media_metadata_db if not exist
        dbcur.execute("CREATE TABLE IF NOT EXISTS current_media_metadata_cache ("
                      "media_type TEXT, "
                      "title TEXT, "
                      "season TEXT, "
                      "episode TEXT, "
                      "year TEXT, "
                      "tmdb_id TEXT);")
        dbcon.commit()
        
        # Clear media_metadata_db
        dbcon.execute("DELETE FROM current_media_metadata_cache")
        dbcon.commit()
        
        dbcon.close()
        kodi_utils.logger("KODI-RD-IL", "EMBEDDED | Cleared media_metadata_db cache")
        
    except Exception as e:
        kodi_utils.logger("KODI-RD-IL", f"EMBEDDED | Error Clearing media_metadata_db cache: {str(e)}")

    
def get_media_type_from_media_metadata_db():

    """
    This function connects to the 'media_metadata_db' database and retrieves the media_type found in the
    'current_media_metadata_cache' table.

    Returns:
    media_type

    """
    try:
        # Connect to the database
        dbcon = database.connect(media_metadata_db)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT media_type FROM current_media_metadata_cache LIMIT 1")
        media_type = dbcur.fetchone()  # Fetch the single row as a tuple
        
        if media_type is not None:
            return media_type[0]  # Extract the value from the tuple and return
        
    except Exception as e:
        # Log any errors that occur while reading the database
        kodi_utils.logger("KODI-RD-IL", f"EMBEDDED | Error while reading media_metadata_db: {str(e)}")
    
    return None # Return None if there's an error or no value
    

def get_current_media_metadata_from_media_metadata_db():
    """
    Retrieve the current media metadata from the 'current_media_metadata_cache' table.

    Returns:
    current_media_metadata (tuple): A tuple containing media metadata (media_type, title, season, episode, year, tmdb_id),
    or None if no metadata is found.
    """
    try:
        # Connect to the database
        dbcon = database.connect(media_metadata_db)
        dbcur = dbcon.cursor()

        # Execute a query to retrieve the single row from the table
        dbcur.execute("SELECT media_type, title, season, episode, year, tmdb_id FROM current_media_metadata_cache LIMIT 1")

        current_media_metadata = dbcur.fetchone()

        if current_media_metadata is not None:
            return current_media_metadata

    except Exception as e:
        # Log any errors that occur while reading the database
        kodi_utils.logger("KODI-RD-IL", f"EMBEDDED | Error while reading media_metadata_db: {str(e)}")

    return None
