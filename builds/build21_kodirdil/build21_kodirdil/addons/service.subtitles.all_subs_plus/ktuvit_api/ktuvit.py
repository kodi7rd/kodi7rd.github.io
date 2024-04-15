import xbmcaddon
import json, re
import cache
import requests
from myLogger import myLogger

BASE_URL_KTUVIT_DOMAIN = "www.ktuvit.me"
BASE_URL_KTUVIT = "https://" + BASE_URL_KTUVIT_DOMAIN
BASE_URL_KTUVIT_SERVICES = BASE_URL_KTUVIT + '/Services'
BASE_URL_KTUVIT_MOVIES_INFO = BASE_URL_KTUVIT + '/MovieInfo.aspx'


def GetKtuvitJson(item,imdb_id,prefix_ktuvit,color_ktuvit):
    response,f_id = get_ktuvit_data(item,imdb_id)

    subtitle_list,m_pre = parse_ktuvit_response(response,f_id,prefix_ktuvit,color_ktuvit)

    return subtitle_list,m_pre

def get_login_cook():
    __addon__ = xbmcaddon.Addon()

    headers = {
    'authority': BASE_URL_KTUVIT_DOMAIN,
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'content-type': 'application/json',
    'origin': BASE_URL_KTUVIT,
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',

    'accept-language': 'en-US,en;q=0.9',

    }

    ktEmail = __addon__.getSetting( "KT_email" )
    if (__addon__.getSetting( "KT_email" ) == ''):
        ktEmail = "hatzel6969@gmail.com"

    ktEncPass = __addon__.getSetting( "KT_enc_pass" )
    if (__addon__.getSetting( "KT_enc_pass" ) == ''):
        ktEncPass = "Jw1n9nPOZRAHw9aVdarvjMph2L85pKGx79oAAFTCsaE="

    data = '{"request":{"Email":"%s","Password":"%s"}}' %(ktEmail, ktEncPass)

    login_cook = requests.post(BASE_URL_KTUVIT_SERVICES + '/MembershipService.svc/Login', headers=headers, data=data).cookies
    login_cook_fix={}
    for cookie in login_cook:
        login_cook_fix[cookie.name]=cookie.value
    return login_cook_fix

def get_ktuvit_data(item,imdb_id):
    from service import is_local_file_tvshow

    regexHelper = re.compile('\W+', re.UNICODE)

    login_cook=cache.get(get_login_cook,1, table='subs')

    if item["tvshow"]:
        s_type='1'
        s_title=item["tvshow"]
        s_year = ''
        s_withSubsOnly = "false"
    elif is_local_file_tvshow(item):
        s_type='1'
        s_title=item["title"]
        s_year = ''
        s_withSubsOnly = "false"
    else: #movies
        s_type='0'
        s_title=item["title"]
        s_year = '' # item["year"] # optional: filtering by 'year' (not is use)
        s_withSubsOnly = "true"

    headers = {
        'authority': BASE_URL_KTUVIT_DOMAIN,
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'content-type': 'application/json',
        'origin': BASE_URL_KTUVIT,
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': BASE_URL_KTUVIT + '/Search.aspx',
        'accept-language': 'en-US,en;q=0.9',

    }

    data = '{"request":{"FilmName":"%s","Actors":[],"Studios":null,"Directors":[],"Genres":[],"Countries":[],"Languages":[],"Year":"%s","Rating":[],"Page":1,"SearchType":"%s","WithSubsOnly":%s}}'%(s_title,s_year,s_type,s_withSubsOnly)

    response = requests.post(BASE_URL_KTUVIT_SERVICES + '/ContentProvider.svc/SearchPage_search', headers=headers, data=data.encode('utf-8')).json()

    j_data = json.loads(response['d'])['Films']
    f_id = ''

    myLogger('Ktuvit data: ' + repr(data))
    myLogger('Ktuvit response: ' + repr(response))
    myLogger('Ktuvit j_data: ' + repr(j_data))

    #first filtered by imdb
    for itt in j_data:
        if len(itt['ImdbID']) > 2 and itt['ImdbID'] in imdb_id:
            f_id = itt['ID']

    #if ids still empty (wrong imdb on ktuvit page) filtered by text
    if f_id == '':
        s_title = regexHelper.sub('', s_title).lower()
        for itt in j_data:
            eng_name = regexHelper.sub('', regexHelper.sub(' ', itt['EngName'])).lower()
            heb_name = regexHelper.sub('', itt['HebName'])

            if ((s_title.startswith(eng_name) or eng_name.startswith(s_title) or
                    s_title.startswith(heb_name) or heb_name.startswith(s_title))
                    and ((not item["tvshow"] or not is_local_file_tvshow(item)) and str(itt['ReleaseDate']) == str(item['year']))):
                f_id=itt["ID"]


    if item["tvshow"] or is_local_file_tvshow(item):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': BASE_URL_KTUVIT_MOVIES_INFO + '?ID=' + f_id,
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers',
        }

        params = (
            ('moduleName', 'SubtitlesList'),
            ('SeriesID', f_id),
            ('Season', item["season"]),
            ('Episode', item["episode"]),
        )

        response = requests.get(BASE_URL_KTUVIT_SERVICES + '/GetModuleAjax.ashx', headers=headers, params=params, cookies=login_cook).content

    else:
        headers = {
            'authority': BASE_URL_KTUVIT_DOMAIN,
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': BASE_URL_KTUVIT_MOVIES_INFO + '?ID=' + f_id,
            'accept-language': 'en-US,en;q=0.9',

        }
        params = (
            ('ID', f_id),
        )

        response = requests.get(BASE_URL_KTUVIT_MOVIES_INFO, headers=headers, params=params, cookies=login_cook).content

    return response,f_id

def parse_ktuvit_response(response,f_id,prefix_ktuvit,color_ktuvit):
    from service import colorize_text
    MyScriptID = xbmcaddon.Addon().getAddonInfo('id')

    regex = '<tr>(.+?)</tr>'
    m_pre = re.compile(regex,re.DOTALL).findall(response.decode('utf-8'))
    #z=1
    subtitle = ' '
    subtitle_list = []

    for itt in m_pre:
        regex = '<div style="float.+?>(.+?)<br />.+?data-subtitle-id="(.+?)"'
        m = re.compile(regex,re.DOTALL).findall(itt)
        if len(m) == 0:
            continue

        if ('i class' in m[0][0]):    #burekas fix for KT titles
            regex = 'כתובית מתוקנת\'></i>(.+?)$'
            n = re.compile(regex,re.DOTALL).findall(m[0][0])
            nm = n[0]
        else:
            nm = m[0][0]

        nm = nm.strip().replace('\n','').replace('\r','').replace('\t','').replace(' ','.')

        data = '{"request":{"FilmID":"%s","SubtitleID":"%s","FontSize":0,"FontColor":"","PredefinedLayout":-1}}'%(f_id,m[0][1])

        nlabel = "Hebrew"
        nlabel2 = colorize_text(nm,color_ktuvit)
        # nlabel2 = colorize_text(prefix_ktuvit,color_ktuvit)
        # nlabel2 = colorize_text(str(z)+'. '+prefix_ktuvit+' '+nm,color_ktuvit)
        nicon = colorize_text(prefix_ktuvit,color_ktuvit)
        nthumb = "he"
        url = "plugin://%s/?action=download&versioname=%s&id=%s&source=%s&language=%s&thumbLang=%s" % (
                                                                                MyScriptID,
                                                                                nm,
                                                                                "ktuvit$$$"+data+'$$$'+f_id,
                                                                                'ktuvit',
                                                                                nlabel,
                                                                                nthumb)

        json_data={'url':url,
                            'label':nlabel,
                            'label2':nlabel2,
                            'iconImage':nicon,
                            'thumbnailImage':nthumb,
                            'hearing_imp':'false',
                            'sync': 'false'}

        subtitle_list.append(json_data)
        #z=z+1

    return subtitle_list,m_pre

def ktuvit_download_sub(id,mode_subtitle):
    from os import path
    from service import MySubFolder2

    #font_c="0"
    #size=0

    o_id=id
    id=id.split("$$$")[1].split("$$$")[0]
    login_cook=cache.get(get_login_cook,1, table='subs')

    f_id=o_id.split("$$$")[2]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': BASE_URL_KTUVIT,
        'Connection': 'keep-alive',
        'Referer': BASE_URL_KTUVIT_MOVIES_INFO + '?ID=' + f_id,
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'Trailers',
    }

    data = id
    response = requests.post(BASE_URL_KTUVIT_SERVICES + '/ContentProvider.svc/RequestSubtitleDownload', headers=headers, cookies=login_cook, data=data).json()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': BASE_URL_KTUVIT_MOVIES_INFO + '?ID=' + f_id,
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'Trailers',
    }

    params = (
        ('DownloadIdentifier', json.loads(response['d'])['DownloadIdentifier']),
    )

    response = requests.get(BASE_URL_KTUVIT_SERVICES + '/DownloadFile.ashx', headers=headers, params=params, cookies=login_cook)
    headers=(response.headers)

    file_name=headers['Content-Disposition'].split("filename=")[1]
    archive_file = path.join(MySubFolder2, file_name)

    # Throw an error for bad status codes
    response.raise_for_status()

    subtitle_list=[]
    with open(archive_file, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)

    subtitle_list.append(archive_file)

    if mode_subtitle>1:
        return subtitle_list," "
    else:
        return subtitle_list,True
