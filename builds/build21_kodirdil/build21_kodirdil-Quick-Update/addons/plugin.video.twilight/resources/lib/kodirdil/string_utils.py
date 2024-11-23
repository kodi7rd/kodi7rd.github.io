########### Imports #####################
from modules import kodi_utils
#########################################


def similar(w1, w2):
    from difflib import SequenceMatcher
    s = SequenceMatcher(None, w1, w2)
    return int(round(s.ratio()*100))
    

def strip_media_name(media_type, title, season, episode, year):
    """Strips the media name based on the media type and returns the result.

    Args:
    media_type (str): The type of media item, either 'movie' or 'tv'.
    title (str): The media (movie/tv) title.
    season (int): The season number for a TV show, or 0 for a movie.
    episode (int): The episode number for a TV show, or 0 for a movie.
    year (int): The year the media item was released.

    Returns:
    str: A stripped version of the media name, with special characters replaced with periods and appended with season and episode numbers for TV shows or the year for movies.

    Example:
    >>> strip_media_name('tv', 'Breaking Bad', 1, 1, 2008)
    'breaking.bad.s01.e01'
    """
    
    # Strip the media name and log the result
    if media_type == 'movie':
        kodi_utils.logger("KODI-RD-IL", f"MEDIA TITLE BEFORE STRIP - Movie Title + Year: {title} | {year}")
        stripped_media_name = f"{clean_media_title_string(title)}.{year}"
        kodi_utils.logger("KODI-RD-IL", f"MEDIA TITLE AFTER STRIP - Movie Title + Year: {stripped_media_name}")
        
    else:
        kodi_utils.logger("KODI-RD-IL", f"MEDIA TITLE BEFORE STRIP - TV Show Title + Season + Episode: {title} | {season} | {episode}")
        stripped_media_name = f"{clean_media_title_string(title)}.s{season:02d}.e{episode:02d}"
        kodi_utils.logger("KODI-RD-IL", f"MEDIA TITLE AFTER STRIP - TV Show Title + Season + Episode: {stripped_media_name}")
    
    return stripped_media_name


def clean_media_title_string(media_title):
    """Converts a media title string to a standardized format.

    Args:
    media_title (str): The media title string to be cleaned.

    Returns:
    str: A cleaned version of the media title string with all characters in lower case and special characters replaced with periods.

    Example:
    >>> clean_media_title_string("The Great Gatsby%20(2013)")
    'the.great.gatsby.2013'
    """
    return media_title.lower().strip().replace("%20",".").replace("_",".").replace(" ",".").replace("-",".").replace("...",".").replace("..",".").replace("(","").replace(")","").replace("[","").replace("]","").replace(":","").replace(",","")



def clean_string(string):
    """Cleans a string by converting to lowercase, removing leading/trailing spaces, and replacing certain characters with dots. Also removes common video and audio formats and language-specific subtitles.

    Args:
    string (str): The string to be cleaned.

    Returns:
    str: A cleaned version of the input string with all characters in lower case and special characters replaced with dots. Also removes common video and audio formats and language-specific subtitles.

    Example:
    clean_string("The Great Gatsby%20(2013)_Trailer.hebrew.srt")
    'the.great.gatsby.2013.trailer'
    """
    return string.lower().strip().replace("%20",".").replace("_",".").replace(" ",".").replace("-",".").replace("...",".").replace("..",".").replace("(","").replace(")","").replace("[","").replace("]","").replace(":","").replace(",","").replace(".avi","").replace(".mp4","").replace(".mkv","").replace(".dts","").replace(".truehd","").replace(".atmos","").replace(".aac","").replace(".x265","").replace(".x264","").replace(".7.1.1","").replace(".7.1","").replace(".5.1.1","").replace(".5.1","").replace(".hevc","").replace(".h.264","").replace(".h264","").replace(".h.265","").replace(".h265","").replace(".2160p","").replace(".1080p","").replace(".720p","").replace(".480p","").replace(".360p","").replace(".srt","").replace(".hebrew","").replace(".heb","")


def clean_subtitle_name_string(subtitle_name):
    cleaned_subtitle_name = (
        subtitle_name.strip()
        .replace(".srt", "")
        .replace("_", ".")
        .replace(" ", ".")
        .replace("+", ".")
        .replace("/", ".")
        .replace("-", ".")
    )
    return [x.strip().lower() for x in cleaned_subtitle_name.split(".") if x != '']
