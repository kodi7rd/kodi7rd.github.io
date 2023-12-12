def login1():
    # https://opensubtitles.stoplight.io/docs/opensubtitles-api/73acf79accc0a-login
    import http.client

    conn = http.client.HTTPSConnection("api.opensubtitles.com")

    payload = "{\n  \"username\": \"burekas\",\n  \"password\": \"2786atos!\"\n}"

    headers = {
        'Content-Type': "application/json",
        'User-Agent': "",
        'Accept': "application/json",
        'Api-Key': "P83ZTw2Ec3XP6h2uXwTqOI9PWbo3cpGL"
    }

    conn.request("POST", "/api/v1/login", payload, headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))


def login2():
    # https://opensubtitles.stoplight.io/docs/opensubtitles-api/73acf79accc0a-login
    import requests

    url = "https://api.opensubtitles.com/api/v1/login"

    payload = {
        "username": "burekas",
        "password": "2786atos!"
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "",
        "Accept": "application/json",
        "Api-Key": "P83ZTw2Ec3XP6h2uXwTqOI9PWbo3cpGL"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())

# {
#   "user": {
#     "allowed_translations": 1, *********
#     "allowed_downloads": 20,  **********
#     "level": "Sub leecher",
#     "user_id": 534331,
#     "ext_installed": false,
#     "vip": false
#   },
#   "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ0Yk9HNEdObTd4alZZNG1ta0Y5cjdRTzBpQVZ0NHlHVSIsImV4cCI6MTcwMDA5ODU2MH0.9CRTVNwI-734rTyn_cGVdESspqKJEwXG3_fNYouHR7I",
#   "status": 200
# }


def search(item, imdb_id):
    #https://opensubtitles.stoplight.io/docs/opensubtitles-api/a172317bd5ccc-search-for-subtitles
    tvshow=item['tvshow']
    season=item['season']
    episode=item['episode']
    year=item['year']
    title=item['title']

    import requests

    url = "https://api.opensubtitles.com/api/v1/subtitles"

    headers = {
        "User-Agent": "",
        "Api-Key": "P83ZTw2Ec3XP6h2uXwTqOI9PWbo3cpGL"
    }

    ################
    # option1 - Movies - by imdb
    ################
    querystring = {"imdb_id":"tt0120338","languages":"he"}
    # also without 'tt': querystring = {"imdb_id":"0120338"}

    ################
    # option2 - Movies - by name and year
    ################
    querystring = {"query":"Titanic","year":"1997","languages":"he"}

    ################
    # option2 - TV Shows - by season/episode
    ################
    querystring = {"query":"Silo","season_number":"1","episode_number":"3","languages":"he"}
    # Also with imdb: querystring = {"imdb_id":"tt14688458","languages":"he","season_number":"1","episode_number":"3"}
    # Also with imdb: querystring = {"imdb_id":"14688458","languages":"he","season_number":"1","episode_number":"3"}


    response = requests.get(url, headers=headers, params=querystring)

    print(response.json())

    #data -> List of results -> attributes -> files -> file_id , file_name

# nlabel = item_data["LanguageName"]                            -> attributes['language']
# nlabel2 = colorize_text(item_data["SubFileName"],color_open) -> attributes -> files['file_name']
# nthumb = item_data["ISO639"]       ??                        -> attributes['language']
# item_data['SeriesSeason']=int(item_data['SeriesSeason'])   -> attributes -> feature_details['season_number']
# item_data['SeriesEpisode']=int(item_data['SeriesEpisode']) -> attributes -> feature_details['episode_number']

            # item_data["ZipDownloadLink"],
            # 'opensubs$$$' + item_data["IDSubtitleFile"], -> attributes -> files['file_id']
            # item_data["SubFileName"], -> attributes -> files['file_name']  **** no file extention!!!!!!!!!!!
            # item_data["SubFormat"],
            # 'opensubtitle',
            # item_data["LanguageName"],   -> attributes['language']

                #  'hearing_imp':("false", "true")[int(item_data["SubHearingImpaired"]) != 0],    -> attributes['hearing_impaired']
                #  'sync': ("false", "true")[str(item_data["MatchedBy"]) == "moviehash"]}


# {
#   "total_pages": 1,
#   "total_count": 32,
#   "per_page": 60,
#   "page": 1,
#   "data": [
#     {
#       "id": "2399398",
#       "type": "subtitle",
#       "attributes": {
#         "subtitle_id": "2399398",
#         "language": "he",
#         "download_count": 1575,
#         "new_download_count": 12,
#         "hearing_impaired": false,
#         "hd": true,
#         "fps": 0,
#         "votes": 0,
#         "ratings": 0,
#         "from_trusted": false,
#         "foreign_parts_only": false,
#         "upload_date": "2015-11-15T15:20:29Z",
#         "ai_translated": false,
#         "machine_translated": false,
#         "release": "Ash.vs.Evil.Dead.S01E03.HDTV.x264-FLEET",
#         "comments": "",
#         "legacy_subtitle_id": 6382663,
#         "legacy_uploader_id": 0,
#         "uploader": {
#           "uploader_id": 3282,
#           "name": "os-auto",
#           "rank": "Application Developers"
#         },
#         "feature_details": {
#           "feature_id": 128988,
#           "feature_type": "Episode",
#           "year": 2015,
#           "title": "Books from Beyond",
#           "movie_name": "Ash vs Evil Dead - S1E3 \"Ash vs Evil Dead\" Books from Beyond",
#           "imdb_id": 4632962,
#           "tmdb_id": 1131010,
#           "season_number": 1,
#           "episode_number": 3,
#           "parent_imdb_id": 4189022,
#           "parent_title": "Ash vs Evil Dead",
#           "parent_tmdb_id": 62264,
#           "parent_feature_id": 15753
#         },
#         "url": "https://www.opensubtitles.com/he/subtitles/legacy/6382663",
#         "related_links": [
#           {
#             "label": "All subtitles for Tv Show Ash vs Evil Dead",
#             "url": "https://www.opensubtitles.com/he/features/redirect/15753",
#             "img_url": "https://s9.opensubtitles.com/features/8/8/9/128988.jpg"
#           },
#           {
#             "label": "All subtitles for Episode books from beyond",
#             "url": "https://www.opensubtitles.com/he/features/redirect/128988"
#           }
#         ],
#         "files": [
#           {
#             "file_id": 2477031,
#             "cd_number": 1,
#             "file_name": "Ash.vs.Evil.Dead.S01E03.HDTV.x264-FLEET"
#           }
#         ]
#       }
#     },
#     {
#       "id": "2499535",
#       "type": "subtitle",
#       "attributes": {
#         "subtitle_id": "2499535",
#         "language": "he",
#         "download_count": 1498,
#         "new_download_count": 1,
#         "hearing_impaired": false,
#         "hd": true,
#         "fps": 0,
#         "votes": 0,
#         "ratings": 0,
#         "from_trusted": false,
#         "foreign_parts_only": false,
#         "upload_date": "2014-04-08T16:48:59Z",
#         "ai_translated": false,
#         "machine_translated": false,
#         "release": "From.Dusk.Till.Dawn.S01E03.HDTV.x264-QCF",
#         "comments": "",
#         "legacy_subtitle_id": 5618784,
#         "legacy_uploader_id": 0,
#         "uploader": {
#           "uploader_id": 3282,
#           "name": "os-auto",
#           "rank": "Application Developers"
#         },
#         "feature_details": {
#           "feature_id": 115413,
#           "feature_type": "Episode",
#           "year": 2014,
#           "title": "Mistress",
#           "movie_name": "From Dusk till Dawn: The Series - S1E3 Mistress",
#           "imdb_id": 3453068,
#           "tmdb_id": 973903,
#           "season_number": 1,
#           "episode_number": 3,
#           "parent_imdb_id": 3337194,
#           "parent_title": "From Dusk till Dawn: The Series",
#           "parent_tmdb_id": 60626,
#           "parent_feature_id": 14337
#         },
#         "url": "https://www.opensubtitles.com/he/subtitles/legacy/5618784",
#         "related_links": [
#           {
#             "label": "All subtitles for Tv Show From Dusk till Dawn: The Series",
#             "url": "https://www.opensubtitles.com/he/features/redirect/14337",
#             "img_url": "https://s9.opensubtitles.com/features/3/1/4/115413.jpg"
#           },
#           {
#             "label": "All subtitles for Episode mistress",
#             "url": "https://www.opensubtitles.com/he/features/redirect/115413"
#           }
#         ],
#         "files": [
#           {
#             "file_id": 2575957,
#             "cd_number": 1,
#             "file_name": "From.Dusk.Till.Dawn.S01E03.HDTV.x264-QCF"
#           }
#         ]
#       }
#     },
#     {
#       "id": "3344411",
#       "type": "subtitle",
#       "attributes": {
#         "subtitle_id": "3344411",
#         "language": "he",
#         "download_count": 1425,
#         "new_download_count": 0,
#         "hearing_impaired": false,
#         "hd": false,
#         "fps": 0,
#         "votes": 0,
#         "ratings": 0,
#         "from_trusted": false,
#         "foreign_parts_only": false,
#         "upload_date": "2016-01-30T16:53:37Z",
#         "ai_translated": false,
#         "machine_translated": false,
#         "release": "Second.Chance.2016.S01E03.HDTV.x264-KILLERS[ettv]",
#         "comments": "",
#         "legacy_subtitle_id": 6483066,
#         "legacy_uploader_id": 0,
#         "uploader": {
#           "uploader_id": 3282,
#           "name": "os-auto",
#           "rank": "Application Developers"
#         },
#         "feature_details": {
#           "feature_id": 416703,
#           "feature_type": "Episode",
#           "year": 2016,
#           "title": "From Darkness the Sun",
#           "movie_name": "Second Chance - S1E3 \"Second Chance\" From Darkness, the Sun",
#           "imdb_id": 5003998,
#           "tmdb_id": 1149675,
#           "season_number": 1,
#           "episode_number": 3,
#           "parent_imdb_id": 4378456,
#           "parent_title": "Second Chance",
#           "parent_tmdb_id": 64434,
#           "parent_feature_id": 15897
#         },
#         "url": "https://www.opensubtitles.com/he/subtitles/legacy/6483066",
#         "related_links": [
#           {
#             "label": "All subtitles for Tv Show Second Chance",
#             "url": "https://www.opensubtitles.com/he/features/redirect/15897",
#             "img_url": "https://s9.opensubtitles.com/features/3/0/7/416703.jpg"
#           },
#           {
#             "label": "All subtitles for Episode from darkness the sun",
#             "url": "https://www.opensubtitles.com/he/features/redirect/416703"
#           }
#         ],
#         "files": [
#           {
#             "file_id": 3412214,
#             "cd_number": 1,
#             "file_name": "Second.Chance.2016.S01E03.HDTV.x264-KILLERS[ettv]-eng"
#           }
#         ]
#       }
#     },
#     {
#       "id": "3348369",
#       "type": "subtitle",
#       "attributes": {
#         "subtitle_id": "3348369",
#         "language": "he",
#         "download_count": 1238,
#         "new_download_count": 1,
#         "hearing_impaired": false,
#         "hd": true,
#         "fps": 0,
#         "votes": 0,
#         "ratings": 0,
#         "from_trusted": false,
#         "foreign_parts_only": false,
#         "upload_date": "2008-02-08T01:30:56Z",
#         "ai_translated": false,
#         "machine_translated": false,
#         "release": "24.503.hdtv-lol.HEB",
#         "comments": null,
#         "legacy_subtitle_id": 3243775,
#         "legacy_uploader_id": 0,
#         "uploader": {
#           "uploader_id": 3282,
#           "name": "os-auto",
#           "rank": "Application Developers"
#         },
#         "feature_details": {
#           "feature_id": 270246,
#           "feature_type": "Episode",
#           "year": 2004,
#           "title": "4.50 from Paddington",
#           "movie_name": "Agatha Christie's Marple - S01E03  \"Agatha Christie's Marple\" Marple: What Mrs. McGillicuddy Saw",
#           "imdb_id": 443579,
#           "tmdb_id": 983654,
#           "season_number": 1,
#           "episode_number": 3,
#           "parent_imdb_id": 1734537,
#           "parent_title": "Agatha Christie's Marple",
#           "parent_tmdb_id": 6127,
#           "parent_feature_id": 10829
#         },
#         "url": "https://www.opensubtitles.com/he/subtitles/legacy/3243775",
#         "related_links": [
#           {
#             "label": "All subtitles for Tv Show Agatha Christie's Marple",
#             "url": "https://www.opensubtitles.com/he/features/redirect/10829",
#             "img_url": "https://s9.opensubtitles.com/features/6/4/2/270246.jpg"
#           },
#           {
#             "label": "All subtitles for Episode 4.50 from paddington",
#             "url": "https://www.opensubtitles.com/he/features/redirect/270246"
#           }
#         ],
#         "files": [
#           {
#             "file_id": 3415738,
#             "cd_number": 1,
#             "file_name": "24.503.hdtv-lol.HEB"
#           }
#         ]
#       }
#     },
#   ]
# }

def download(file_id, delay = 2):

    ## STEP1

    import requests

    url = "https://api.opensubtitles.com/api/v1/download"

    headers = {
        "User-Agent": "",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Api-Key": "P83ZTw2Ec3XP6h2uXwTqOI9PWbo3cpGL",
        "Authorization": "Bearer %s" %("token")
    }

    # payload = { "file_id": 2477031 }
    payload = { "file_id": file_id }

    #try catch

    response = requests.post(url, json=payload, headers=headers)
    # url = response['link']
    # filename = response['file_name']

    print(response.json())

    ## STEP2

    if response:
        ## MAKE A GLOBAL FUNCTION - WIZ, SUBSCENE, OPENSUBS
        import time
        from service import notify3
        from subscene_api.third_party.cloudscraper import cloudscraper
        global error_page_text
        # from requests import get

        myLogger("Wizdom wizdom_download_sub")
        method = 'GET'
        url = response['link']               ### not from search results as before and not a zip file as before
        filename = response['file_name']     ### not from search results as before
        dest = os.path.join(MySubFolder, filename)

        try:
            for i in range(5):
                myLogger("Wizdom wizdom_download_sub url: " + repr(url))
                s = cloudscraper.create_scraper(interpreter='native')
                r = s.request(method, url)
                # r = get(url)
                if r.status_code == 403:
                    myLogger(f"Attempt {i+1}: Response code is {r.status_code}. Retrying...")
                    time.sleep(delay)
                else:
                    myLogger(f"Attempt {i+1}: Response code is {r.status_code}. Request successful.")
                    break
            else:
                myLogger("All attempts failed.")
                notify3("%s %s" %(error_page_text, str(r.status_code)))

        except:
            s = cloudscraper.create_scraper(interpreter='native')
            r = s.request(method, url, verify=False)
            # r = get(url)
            return r.text

        if r.status_code == 200:
            with open(dest, 'wb') as f:
                f.write(r.content)
                myLogger(f'Download completed: {dest}')
        else:
            notify3(f'Download failed with status code: {r.status_code}')

# 200
# {
#   "link": "https://www.opensubtitles.com/download/CA5BB5B1B8B1DED2436E97DB0BD13AA26CA147488F8B9B1E44F0A596B2B2ED565A99F1770742DAB01C8192C62F9FDBF93215A3CBDD24F03A40718CB38FA1B4873F9A4B23446CC5EBF66BDFF9A398F89D61BA3B5B2828EA3B715FD55F23156B3642F8B69476D2CF6934AA08BCF618D22879F354725581BF733BCD4568B1A1083AFDA567DFAF0ABDFA75633B34DB0AC7F026585BBBA55F677C8BF9D8C14FC4795A93BA26FC96AEFD9EACA21F43AAC78E4EEE9F2DEDB010A52919C4712585CE4D8D1FD202D3F803513FBFC76F2A8FBC1FBF68717EC7B8A380248FB423B35223A06F29881569D017B0A593763D6CBB03F4119B85D8AA5095CF26BEFF07926584AA122528D368E686D8163F01609BA1CFF05973A49AA31DAD5E7FFE065F367B882581F54CC0951BDE5A03/subfile/Ash.vs.Evil.Dead.S01E03.HDTV.x264-FLEET.srt",
#   "file_name": "Ash.vs.Evil.Dead.S01E03.HDTV.x264-FLEET.srt",
#   "requests": 2,
#   "remaining": 98,  **********
#   "message": "Your quota will be renewed in 01 hours and 55 minutes (2023-11-16 00:00:00 UTC) ts=1700085865 ",
#   "reset_time": "01 hours and 55 minutes",
#   "reset_time_utc": "2023-11-16T00:00:00.000Z",
#   "uk": "app_ud_71040",
#   "uid": 2,
#   "ts": 1700085865
# }

# {
#   "link": "https://www.opensubtitles.com/download/6FDC5B3CF93BB11FFBD7DEBE076B8EE8A0D05DF6A2517A37BD94CAAC141D80073FEA8E51FAC19974FBB7B28ED3B26CCA2D96A53A79E45E0ED1B9FA627E4AA1A76F5CD1845700CB300E6C8D2155F94F52E7DBB352B2B85C49253B2A8FEB2615FAB3E28CCCB3568F8D610F5E801774536BDF4729760DB1330590AB715115EEA53DBBCDA5C707171EE12C3A1FE2728A885470E44928ACAA8A07CCCF161B5A36E43B476F6D2AA51AAAA5BF9FD803FCE49E82A8D42DC6BFF3F9A82966A34207B5669254C5B261F78EAB0B90348BB0B5C4A5F59C59BB99520F3B7B979CDE08829664C40019BD3F56D90AF0057FC1FDA214520085594E35DDF9B63E98CF2CFC5F00819565FFB122C6B2A72007B4429A0DEDDEE625404E14F9A42F1808E41F59081E05D4ED2EE11F69E4B0C0/subfile/castle.rock.s01e04.webrip.x264-tbs-eng.srt",
#   "file_name": "castle.rock.s01e04.webrip.x264-tbs-eng.srt",
#   "requests": 100,
#   "remaining": 0,
#   "message": "Your quota will be renewed in 09 hours and 41 minutes (2023-11-25 23:59:59 UTC) ts=1700921907 ",
#   "reset_time": "09 hours and 41 minutes",
#   "reset_time_utc": "2023-11-25T23:59:59.000Z",
#   "uk": "app_ud_71040",
#   "uid": 2,
#   "ts": 1700921907
# }

# 406
# {
#   "requests": 101,
#   "remaining": -1,
#   "message": "You have downloaded your allowed 100 subtitles for 24h.Your quota will be renewed in 09 hours and 40 minutes (2023-11-26 00:00:00 UTC) ts=1700921947 ",
#   "reset_time": "09 hours and 40 minutes",
#   "reset_time_utc": "2023-11-26T00:00:00.000Z",
#   "uk": "app_ud_71040",
#   "uid": 2,
#   "ts": 1700921947
# }

