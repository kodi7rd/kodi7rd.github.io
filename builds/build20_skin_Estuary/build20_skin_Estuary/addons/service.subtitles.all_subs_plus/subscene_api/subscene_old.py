import os
import sys
import xbmc
import urllib

import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import uuid
import unicodedata
import re
import string,time
import difflib,gzip
import logging

from myLogger import myLogger

try:
    import HTMLParser
    html_parser = HTMLParser.HTMLParser()
except:
    import html
    html_parser=html
from operator import itemgetter
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3

from xbmcaddon import Addon
try:
    from urllib.request import urlopen
    from urllib.request import Request
except ImportError:
    from urllib2 import urlopen
    from urllib2 import Request

KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
if KODI_VERSION<=18:
    xbmc_translate_path=xbmc.translatePath
else:
    import xbmcvfs
    xbmc_translate_path=xbmcvfs.translatePath
if KODI_VERSION<=18:
    que=urllib.quote_plus
    url_encode=urllib.urlencode
else:
    que=urllib.parse.quote_plus
    url_encode=urllib.parse.urlencode
if KODI_VERSION<=18:
    unque=urllib.unquote_plus
else:
    unque=urllib.parse.unquote_plus
__addon__ = xbmcaddon.Addon()
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
MyAddon = Addon()

prefix_subscene = '[SS]'

all_lang_codes={

    'Albanian': {'id': 1, '3let': 'alb', '2let': 'sq', 'name': 'Albanian'},
    'Arabic': {'id': 2, '3let': 'ara', '2let': 'ar', 'name': 'Arabic'},
    'Big 5 code': {'id': 3, '3let': 'chi', '2let': 'zh', 'name': 'Chinese'},
    'Brazillian Portuguese': {'id': 4, '3let': 'por', '2let': 'pb', 'name': 'Brazilian Portuguese'},
    'Bulgarian': {'id': 5, '3let': 'bul', '2let': 'bg', 'name': 'Bulgarian'},
    'Chinese BG code': {'id': 7, '3let': 'chi', '2let': 'zh', 'name': 'Chinese'},
    'Croatian': {'id': 8, '3let': 'hrv', '2let': 'hr', 'name': 'Croatian'},
    'Czech': {'id': 9, '3let': 'cze', '2let': 'cs', 'name': 'Czech'},
    'Danish': {'id': 10, '3let': 'dan', '2let': 'da', 'name': 'Danish'},
    'Dutch': {'id': 11, '3let': 'dut', '2let': 'nl', 'name': 'Dutch'},
    'English': {'id': 13, '3let': 'eng', '2let': 'en', 'name': 'English'},
    'Estonian': {'id': 16, '3let': 'est', '2let': 'et', 'name': 'Estonian'},
    'Farsi/Persian': {'id': 46, '3let': 'per', '2let': 'fa', 'name': 'Persian'},
    'Finnish': {'id': 17, '3let': 'fin', '2let': 'fi', 'name': 'Finnish'},
    'French': {'id': 18, '3let': 'fre', '2let': 'fr', 'name': 'French'},
    'German': {'id': 19, '3let': 'ger', '2let': 'de', 'name': 'German'},
    'Greek': {'id': 21, '3let': 'gre', '2let': 'el', 'name': 'Greek'},
    'Hebrew': {'id': 22, '3let': 'heb', '2let': 'he', 'name': 'Hebrew'},
    'Hungarian': {'id': 23, '3let': 'hun', '2let': 'hu', 'name': 'Hungarian'},
    'Icelandic': {'id': 25, '3let': 'ice', '2let': 'is', 'name': 'Icelandic'},
    'Indonesian': {'id': 44, '3let': 'ind', '2let': 'id', 'name': 'Indonesian'},
    'Italian': {'id': 26, '3let': 'ita', '2let': 'it', 'name': 'Italian'},
    'Japanese': {'id': 27, '3let': 'jpn', '2let': 'ja', 'name': 'Japanese'},
    'Korean': {'id': 28, '3let': 'kor', '2let': 'ko', 'name': 'Korean'},
    'Lithuanian': {'id': 43, '3let': 'lit', '2let': 'lt', 'name': 'Lithuanian'},
    'Malay': {'id': 50, '3let': 'may', '2let': 'ms', 'name': 'Malay'},
    'Norwegian': {'id': 30, '3let': 'nor', '2let': 'no', 'name': 'Norwegian'},
    'Polish': {'id': 31, '3let': 'pol', '2let': 'pl', 'name': 'Polish'},
    'Portuguese': {'id': 32, '3let': 'por', '2let': 'pt', 'name': 'Portuguese'},
    'Romanian': {'id': 33, '3let': 'rum', '2let': 'ro', 'name': 'Romanian'},
    'Russian': {'id': 34, '3let': 'rus', '2let': 'ru', 'name': 'Russian'},
    'Serbian': {'id': 35, '3let': 'scc', '2let': 'sr', 'name': 'Serbian'},
    'Slovak': {'id': 36, '3let': 'slo', '2let': 'sk', 'name': 'Slovak'},
    'Slovenian': {'id': 37, '3let': 'slv', '2let': 'sl', 'name': 'Slovenian'},
    'Spanish': {'id': 38, '3let': 'spa', '2let': 'es', 'name': 'Spanish'},
    'Swedish': {'id': 39, '3let': 'swe', '2let': 'sv', 'name': 'Swedish'},
    'Thai': {'id': 40, '3let': 'tha', '2let': 'th', 'name': 'Thai'},
    'Turkish': {'id': 41, '3let': 'tur', '2let': 'tr', 'name': 'Turkish'},
    'Vietnamese': {'id': 45, '3let': 'vie', '2let': 'vi', 'name': 'Vietnamese'}
}
all_nam_lang={}
for items in all_lang_codes:
    all_nam_lang[all_lang_codes[items]['3let']]={items:all_lang_codes[items]}

__cwd__ = xbmc_translate_path(__addon__.getAddonInfo('path'))
__profile__ = xbmc_translate_path(__addon__.getAddonInfo('profile'))
__resource__ = xbmc_translate_path(os.path.join(__cwd__, 'resources', 'lib'))
__temp__ = xbmc_translate_path(os.path.join(__profile__, 'temp_download', ''))
subscene_languages = {
    'Hebrew': {'id': 22, '3let': 'heb', '2let': 'he', 'name': 'Hebrew'}

}
if MyAddon.getSetting("English")== 'true':
  subscene_languages = {
    'Hebrew': {'id': 22, '3let': 'heb', '2let': 'he', 'name': 'Hebrew'},
    'English': {'id': 13, '3let': 'eng', '2let': 'en', 'name': 'English'}
}

if MyAddon.getSetting("arab")== 'true':
    subscene_languages.update(all_nam_lang['ara'])
if MyAddon.getSetting("spanish")== 'true':
    subscene_languages.update(all_nam_lang['spa'])

if len(MyAddon.getSetting("other_lang"))>0:
     all_lang=MyAddon.getSetting("other_lang").split(",")
     all_lang=['fre']
     for items in all_lang:
       if items in all_nam_lang:
        subscene_languages.update(all_nam_lang[items])
###myLogger(subscene_languages)
aliases = {
    "marvels agents of shield" : "Agents of Shield",
    "marvels agents of s.h.i.e.l.d" : "Agents of Shield",
    "marvels jessica jones": "Jessica Jones",
    "dcs legends of tomorrow": "Legends of Tomorrow"
}

# Seasons as strings for searching
seasons = ["Specials", "First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth", "Tenth"]
seasons = seasons + ["Eleventh", "Twelfth", "Thirteenth", "Fourteenth", "Fifteenth", "Sixteenth", "Seventeenth",
                     "Eighteenth", "Nineteenth", "Twentieth"]
seasons = seasons + ["Twenty-first", "Twenty-second", "Twenty-third", "Twenty-fourth", "Twenty-fifth", "Twenty-sixth",
                     "Twenty-seventh", "Twenty-eighth", "Twenty-ninth"]

search_section_pattern = "<h2 class=\"(?P<section>\w+)\">(?:[^<]+)</h2>\s+<ul>(?P<content>.*?)</ul>"
movie_season_pattern = ("<a href=\"(?P<link>/subtitles/[^\"]*)\">(?P<title>[^<]+)\((?P<year>\d{4})\)</a>\s+"
                        "</div>\s+<div class=\"subtle count\">\s+(?P<numsubtitles>\d+)")
def find_movie(content, title, year):
    found_urls = {}
    found_movies = []

    h = html_parser
    for secmatches in re.finditer(search_section_pattern, content, re.IGNORECASE | re.DOTALL):
        log(__name__, secmatches.group('section'))
        for matches in re.finditer(movie_season_pattern, secmatches.group('content'), re.IGNORECASE | re.DOTALL):
            if matches.group('link') in found_urls:
                if secmatches.group('section') == 'close':
                    found_movies[found_urls[matches.group('link')]]['is_close'] = True
                if secmatches.group('section') == 'exact':
                    found_movies[found_urls[matches.group('link')]]['is_exact'] = True
                continue
            found_urls[matches.group('link')] = len(found_movies)

            found_title = matches.group('title')
            found_title = h.unescape(found_title)
            log(__name__, "Found movie on search page: %s (%s)" % (found_title, matches.group('year')))
            found_movies.append(
                {'t': string.lower(found_title),
                 'y': int(matches.group('year')),
                 'is_exact': secmatches.group('section') == 'exact',
                 'is_close': secmatches.group('section') == 'close',
                 'l': matches.group('link'),
                 'c': int(matches.group('numsubtitles'))})

    year = int(year)
    title = string.lower(title)
    # Priority 1: matching title and year
    for movie in found_movies:
        if string.find(movie['t'], title) > -1:
            if movie['y'] == year:
                log(__name__, "Matching movie found on search page: %s (%s)" % (movie['t'], movie['y']))
                return movie['l']

    # Priority 2: matching title and one off year
    for movie in found_movies:
        if string.find(movie['t'], title) > -1:
            if movie['y'] == year + 1 or movie['y'] == year - 1:
                log(__name__, "Matching movie found on search page (one off year): %s (%s)" % (movie['t'], movie['y']))
                return movie['l']

    # Priority 3: "Exact" match according to search result page
    close_movies = []
    for movie in found_movies:
        if movie['is_exact']:
            log(__name__, "Using 'Exact' match: %s (%s)" % (movie['t'], movie['y']))
            return movie['l']
        if movie['is_close']:
            close_movies.append(movie)

    # Priority 4: "Close" match according to search result page
    if len(close_movies) > 0:
        close_movies = sorted(close_movies, key=itemgetter('c'), reverse=True)
        log(__name__, "Using 'Close' match: %s (%s)" % (close_movies[0]['t'], close_movies[0]['y']))
        return close_movies[0]['l']

    return None
def get_language_codes(languages):
    codes = {}
    for lang in subscene_languages:
        #myLogger(lang)
        #myLogger(subscene_languages[lang]['3let'] )
        if subscene_languages[lang]['3let'] in languages:
            codes[str(subscene_languages[lang]['id'])] = 1
            #myLogger('lang')
            #myLogger(str(subscene_languages[lang]['id']))
    keys = codes.keys()
    return keys

main_url = "https://subscene.com"
subscene_start = time.time()
def log(module, msg):
    global subscene_start
    myLogger(msg)
    xbmc.log((u"### [%s] %f - %s" % (module, time.time() - subscene_start, msg,)), level=xbmc.LOGDEBUG)

def prepare_search_string(s):
    s = str.strip(s)
    s = re.sub(r'\s+\(\d\d\d\d\)$', '', s)  # remove year from title
    return s

def search_subscene(item,mode_subtitle):
    filename = os.path.splitext(os.path.basename(item['file_original_path']))[0]
   # #myLogger(__name__, "Search_subscene='%s', filename='%s', addon_version=%s" % (item, filename, __version__))

    #myLogger(item['tvshow'])
    lang=[]
    lang.append('heb')
    if MyAddon.getSetting("English")== 'true':
        lang.append('eng')
    if item['tvshow']:
        num_of_subs,subtitle,subtitle_list=search_tvshow(item['tvshow'], item['season'], item['episode'], lang, filename,mode_subtitle)
    elif item['title'] and item['year']:
        #myLogger('movie Subscene')
        num_of_subs,subtitle,subtitle_list=search_movie(item['title'], item['year'], lang, filename,mode_subtitle)
    elif item['title']:
        num_of_subs,subtitle,subtitle_list=search_filename(item['title'], lang,mode_subtitle)
    else:
        num_of_subs,subtitle,subtitle_list=search_filename(filename, lang,mode_subtitle)
    return num_of_subs,subtitle,subtitle_list
def find_tv_show_season(content, tvshow, season):
    url_found = None
    found_urls = []
    possible_matches = []
    all_tvshows = []

    h = html_parser
    for matches in re.finditer(movie_season_pattern, content, re.IGNORECASE | re.DOTALL):
        found_title = matches.group('title')
        found_title = h.unescape(found_title)

        if matches.group('link') in found_urls:
            continue
        log(__name__, "Found tv show season on search page: %s" % found_title)
        found_urls.append(matches.group('link'))
        s = difflib.SequenceMatcher(None, string.lower(found_title + ' ' + matches.group('year')), string.lower(tvshow))
        all_tvshows.append(matches.groups() + (s.ratio() * int(matches.group('numsubtitles')),))
        if string.find(string.lower(found_title), string.lower(tvshow) + " ") > -1:
            if string.find(string.lower(found_title), string.lower(season)) > -1:
                log(__name__, "Matching tv show season found on search page: %s" % found_title)
                possible_matches.append(matches.groups())

    if len(possible_matches) > 0:
        possible_matches = sorted(possible_matches, key=lambda x: -int(x[3]))
        url_found = possible_matches[0][0]
        log(__name__, "Selecting matching tv show with most subtitles: %s (%s)" % (
            possible_matches[0][1], possible_matches[0][3]))
    else:
        if len(all_tvshows) > 0:
            all_tvshows = sorted(all_tvshows, key=lambda x: -int(x[4]))
            url_found = all_tvshows[0][0]
            log(__name__, "Selecting tv show with highest fuzzy string score: %s (score: %s subtitles: %s)" % (
                all_tvshows[0][1], all_tvshows[0][4], all_tvshows[0][3]))

    return url_found
def search_tvshow(tvshow, season, episode, languages, filename,mode_subtitle):
    tvshow = prepare_search_string(tvshow)

    tvshow_lookup = tvshow.lower().replace("'", "").strip(".")
    if tvshow_lookup in aliases:
        log(__name__, 'found alias for "%s"' % tvshow_lookup)
        tvshow = aliases[tvshow_lookup]

    search_string = tvshow + " - " + seasons[int(season)] + " Season"

    log(__name__, "Search tvshow = %s" % search_string)
    url = main_url + "/subtitles/title?q=" + que(search_string) + '&r=true'
    content, response_url = geturl(url)

    if content is not None:
        log(__name__, "Multiple tv show seasons found, searching for the right one ...")
        myLogger('AAAAAAAAAAAA1 %s | %s | %s' %(content, tvshow, seasons[int(season)]))
        tv_show_seasonurl = find_tv_show_season(content, tvshow, seasons[int(season)])
        if tv_show_seasonurl is not None:
            log(__name__, "Tv show season found in list, getting subs ...")
            url = main_url + tv_show_seasonurl
            epstr = "%d:%d" % (int(season), int(episode))
            myLogger('search tv')
            num_of_subs,subtitle,subtitle_list=getallsubs(url, languages,mode_subtitle,filename, epstr)
    return num_of_subs,subtitle,subtitle_list
def search_manual(searchstr, languages, filename,mode_subtitle):
    search_string = prepare_search_string(searchstr)
    url = main_url + "/subtitles/release?q=" + que(search_string) + '&r=true'
    num_of_subs,subtitle,subtitle_list=getallsubs(url, languages,mode_subtitle,filename)
    return num_of_subs,subtitle,subtitle_list
def search_filename(filename, languages,mode_subtitle):
    title, year = xbmc.getCleanMovieTitle(filename)
    log(__name__, "clean title: \"%s\" (%s)" % (title, year))
    try:
        yearval = int(year)
    except ValueError:
        yearval = 0
    match = re.search(r'\WS(?P<season>\d\d)E(?P<episode>\d\d)', filename, flags=re.IGNORECASE)
    if match is not None:
        tvshow = string.strip(title[:match.start('season') - 1])
        season = string.lstrip(match.group('season'), '0')
        episode = string.lstrip(match.group('episode'), '0')
        num_of_subs,subtitle,subtitle_list=search_tvshow(tvshow, season, episode, languages, filename,mode_subtitle)
    elif title and yearval > 1900:
        num_of_subs,subtitle,subtitle_list=search_movie(title, year, languages, filename,mode_subtitle)
    else:
        num_of_subs,subtitle,subtitle_list=search_manual(filename, languages, filename,mode_subtitle)
    return num_of_subs,subtitle,subtitle_list

def search_movie(title, year, languages, filename,mode_subtitle):
    title = prepare_search_string(title)
    #myLogger(title)
    #log(__name__, "Search movie = %s" % title)
    url = main_url + "/subtitles/title?q=" + que(title) + '&r=true'
    content, response_url = geturl(url)
    #myLogger(url)
    subtitle=' '
    num_of_subs=0
    subtitle_list=''
    if content is not None:
        log(__name__, "Multiple movies found, searching for the right one ...")
        subspage_url = find_movie(content, title, year)
        if subspage_url is not None:
            log(__name__, "Movie found in list, getting subs ...")
            url = main_url + subspage_url
            #myLogger('search movie')
            num_of_subs,subtitle,subtitle_list=getallsubs(url, languages,mode_subtitle,filename)
            #myLogger(url)
        else:
            log(__name__, "Movie not found in list: %s" % title)
            if string.find(string.lower(title), "&") > -1:
                title = string.replace(title, "&", "and")
                log(__name__, "Trying searching with replacing '&' to 'and': %s" % title)
                subspage_url = find_movie(content, title, year)
                if subspage_url is not None:
                    log(__name__, "Movie found in list, getting subs ...")
                    url = main_url + subspage_url
                    #myLogger('search None')
                    num_of_subs,subtitle,subtitle_list=getallsubs(url, languages,mode_subtitle, filename)
                else:
                    log(__name__, "Movie not found in list: %s" % title)
    return num_of_subs,subtitle,subtitle_list

def geturl(url, cookies=None):
    import io
    log(__name__, "Getting url: %s" % url)
    try:
        request = Request(url)
        request.add_header('Accept-encoding', 'gzip')
        if cookies:
            request.add_header('Cookie', cookies)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:41.0) Gecko/20100101 Firefox/41.0')
        response = urlopen(request)
        log(__name__, "request done")
        if response.info().get('Content-Encoding') == 'gzip':
            buf = io.BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            content = f.read()
        else:
            content = response.read()
        log(__name__, "read done")
        # Fix non-unicode characters in movie titles
        strip_unicode = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?<>\\]+|[^\s]+)")
        content = strip_unicode.sub('', content.decode("utf-8"))
        return_url = response.geturl()
        log(__name__, "fetching done")
    except:
        log(__name__, "Failed to get url: %s" % url)
        content = None
        return_url = None
    return content, return_url

def get_episode_pattern(episode):
    parts = episode.split(':')
    if len(parts) < 2:
        return "%%%%%"
    season = int(parts[0])
    epnr = int(parts[1])
    patterns = [
        "s%#02de%#02d" % (season, epnr),
        "%#02dx%#02d" % (season, epnr),
    ]
    if season < 10:
        patterns.append("(?:\A|\D)%dx%#02d" % (season, epnr))
    return '(?:%s)' % '|'.join(patterns)

def getallsubs(url, allowed_languages,mode_subtitle, filename="", episode=""):
    subtitle_pattern = ("<td class=\"a1\">\s+<a href=\"(?P<link>/subtitles/[^\"]+)\">\s+"
                        "<span class=\"[^\"]+ (?P<quality>\w+-icon)\">\s+(?P<language>[^\r\n\t]+)\s+</span>\s+"
                        "<span>\s+(?P<filename>[^\r\n\t]+)\s+</span>\s+"
                        "</a>\s+</td>\s+"
                        "<td class=\"[^\"]+\">\s+(?P<numfiles>[^\r\n\t]*)\s+</td>\s+"
                        "<td class=\"(?P<hiclass>[^\"]+)\">"
                        "(?:.*?)<td class=\"a6\">\s+<div>\s+(?P<comment>[^\"]+)&nbsp;\s*</div>")
    #myLogger('codes2')
    codes = get_language_codes(allowed_languages)
    #myLogger(codes)
    #myLogger('codes')
    if len(codes) < 1:

        xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, __language__(32004))).encode('utf-8'))
        return
    log(__name__, 'LanguageFilter='+','.join(codes))
    content, response_url = geturl(url, 'LanguageFilter='+','.join(codes))
    #myLogger(url)

    if content is None:
        return

    subtitles = []
    h = html_parser
    episode_regex = None
    if episode != "":
        episode_regex = re.compile(get_episode_pattern(episode), re.IGNORECASE)
        log(__name__, "regex: %s" % get_episode_pattern(episode))
    x=1
    for matches in re.finditer(subtitle_pattern, content, re.IGNORECASE | re.DOTALL):
        numfiles = 1
        if matches.group('numfiles') != "":
            numfiles = int(matches.group('numfiles'))
        languagefound = matches.group('language')
        language_info = subscene_languages[languagefound]

        if language_info and language_info['3let'] in allowed_languages:
            link = main_url + matches.group('link')
            subtitle_name = string.strip(matches.group('filename'))
            hearing_imp = (matches.group('hiclass') == "a41")
            rating = '0'
            if matches.group('quality') == "bad-icon":
                continue
            if matches.group('quality') == "positive-icon":
                rating = '5'

            comment = re.sub("[\r\n\t]+", " ", h.unescape(string.strip(matches.group('comment'))))

            sync = False
            if filename != "" and string.lower(filename) == string.lower(subtitle_name):
                sync = True

            if episode != "":
                # log(__name__, "match: "+subtitle_name)
                if episode_regex.search(subtitle_name):
                    subtitles.append({'rating': rating, 'filename': subtitle_name, 'sync': sync, 'link': link,
                                      'lang': language_info, 'hearing_imp': hearing_imp, 'comment': comment})
                elif numfiles > 2:
                    subtitle_name = subtitle_name + ' ' + (__language__(32001) % int(matches.group('numfiles')))
                    subtitles.append({'rating': rating, 'filename': subtitle_name, 'sync': sync, 'link': link,
                                      'lang': language_info, 'hearing_imp': hearing_imp, 'comment': comment,
                                      'episode': episode})
            else:
                subtitles.append({'rating': rating, 'filename': subtitle_name, 'sync': sync, 'link': link,
                                  'lang': language_info, 'hearing_imp': hearing_imp, 'comment': comment})

    subtitles.sort(key=lambda x: [not x['sync'], not x['lang']['name'] == 'Undetermined'])
    subtitle=" "
    subtitle_list=[]
    for s in subtitles:
        subtitle,json_data=append_subtitle(s,mode_subtitle,x)
        subtitle_list.append(json_data)
        x=x+1
        if mode_subtitle==1 and subtitle!=" ":
          break
    return len(subtitles),subtitle,subtitle_list
def append_subtitle(item,mode_subtitle,x):
    title = item['filename']
    if 'comment' in item and item['comment'] != '':
        title = "%s [COLOR gray][I](%s)[/I][/COLOR]" % (title, item['comment'])
    listitem = xbmcgui.ListItem(label=item['lang']['name'],
                                label2='[COLOR burlywood]'+str(x)+ '. '+prefix_subscene+' '+title+'[/COLOR]',
                                iconImage=item['rating'],
                                thumbnailImage=item['lang']['2let'])

    listitem.setProperty("sync", 'true' if item["sync"] else 'false')
    listitem.setProperty("hearing_imp", 'true' if item["hearing_imp"] else 'false')

    # below arguments are optional, it can be used to pass any info needed in download function
    # anything after "action=download&" will be sent to addon once user clicks listed subtitle to downlaod
    url = "plugin://%s/?action=download&link=%s&filename=%s&source=%s" % (__scriptid__,
                                                                item['link'],
                                                                item['filename'],
                                                                'subscence')
    json_data={'url':url,
                             'label':item['lang']['name'],
                             'label2':'[COLOR burlywood]'+str(x)+ '. '+prefix_subscene+' '+title+'[/COLOR]',
                             'iconImage':item['rating'],
                             'thumbnailImage':item['lang']['2let'],
                             'hearing_imp':'true' if item["hearing_imp"] else 'false',
                             'sync':'true' if item["sync"] else 'false'}

    if 'episode' in item:
        url += "&episode=%s" % item['episode']
    # add it to list, this can be done as many times as needed for all subtitles found

    if mode_subtitle>1:

      #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)
      return " ",json_data
    else:
      if 'episode' in item:
        subtitle=download_subscene(item['link'],mode_subtitle,item['episode'])
      else:
        subtitle=download_subscene(item['link'],mode_subtitle)
      return subtitle,json_data


def download_subscene(link,mode_subtitle, episode=""):
    subtitle_list = []
    exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass"]
    downloadlink_pattern = "...<a href=\"(.+?)\" rel=\"nofollow\" onclick=\"DownloadSubtitle"

    uid = uuid.uuid4()
    tempdir = os.path.join(__temp__, str(uid))
    xbmcvfs.mkdirs(tempdir)

    content, response_url = geturl(link)
    match = re.compile(downloadlink_pattern).findall(content)
    if match:
        downloadlink = main_url + match[0]
        viewstate = 0
        previouspage = 0
        subtitleid = 0
        typeid = "zip"
        filmid = 0

        postparams = url_encode(
            {'__EVENTTARGET': 's$lc$bcr$downloadLink', '__EVENTARGUMENT': '', '__VIEWSTATE': viewstate,
             '__PREVIOUSPAGE': previouspage, 'subtitleId': subtitleid, 'typeId': typeid, 'filmId': filmid}).encode('utf-8')

        useragent = ("User-Agent=Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) "
                       "Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)")
        headers = {'User-Agent': useragent, 'Referer': link}
        log(__name__, "Fetching subtitles using url '%s' with referer header '%s' and post parameters '%s'" % (
            downloadlink, link, postparams))
        request = Request(downloadlink, postparams, headers)
        # xbmc.log('bla bla'+str(request), 5)
        response = urlopen(request)
        # request = urllib2.Request(downloadlink, postparams, headers)
        # response = urllib2.urlopen(request)
        if response.getcode() != 200:
            log(__name__, "Failed to download subtitle file")
            return subtitle_list

        local_tmp_file = os.path.join(tempdir, "subscene.xxx")
        packed = False

        try:
            log(__name__, "Saving subtitles to '%s'" % local_tmp_file)
            local_file_handle = xbmcvfs.File(local_tmp_file, "wb")
            local_file_handle.write(response.read())
            local_file_handle.close()

            # Check archive type (rar/zip/else) through the file header (rar=Rar!, zip=PK)
            myfile = xbmcvfs.File(local_tmp_file, "rb")
            myfile.seek(0,0)
            if myfile.read(1) == 'R':
                typeid = "rar"
                packed = True
                log(__name__, "Discovered RAR Archive")
            else:
                myfile.seek(0,0)
                if myfile.read(1) == 'P':
                    typeid = "zip"
                    packed = True
                    log(__name__, "Discovered ZIP Archive")
                else:
                    typeid = "srt"
                    packed = False
                    log(__name__, "Discovered a non-archive file")
            myfile.close()
            local_tmp_file = os.path.join(tempdir, "subscene." + typeid)
            xbmcvfs.rename(os.path.join(tempdir, "subscene.xxx"), local_tmp_file)
            log(__name__, "Saving to %s" % local_tmp_file)
        except:
            log(__name__, "Failed to save subtitle to %s" % local_tmp_file)

        if packed:
            xbmc.sleep(500)
            xbmc.executebuiltin(('Extract("%s","%s")' % (local_tmp_file, tempdir,)), True)

        episode_pattern = None
        if episode != '':
            episode_pattern = re.compile(get_episode_pattern(episode), re.IGNORECASE)

        for dir in xbmcvfs.listdir(tempdir)[0]:
            for file in xbmcvfs.listdir(os.path.join(tempdir, dir))[1]:
                if os.path.splitext(file)[1] in exts:
                    log(__name__, 'match '+episode+' '+file)
                    if episode_pattern and not episode_pattern.search(file):
                        continue
                    log(__name__, "=== returning subtitle file %s" % file)
                    subtitle_list.append(os.path.join(tempdir, dir, file))

        for file in xbmcvfs.listdir(tempdir)[1]:
            if os.path.splitext(file)[1] in exts:
                log(__name__, 'match '+episode+' '+file)
                if episode_pattern and not episode_pattern.search(file):
                    continue
                log(__name__, "=== returning subtitle file %s" % file)
                subtitle_list.append(os.path.join(tempdir, file))

        if len(subtitle_list) == 0:
            if episode:
                xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, __language__(32002))))
            else:
                xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, __language__(32003))))
    if mode_subtitle==1:
      #xbmc.Player().setSubtitles(subtitle_list[0])
      return subtitle_list[0]
    else:
      return subtitle_list