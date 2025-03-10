import xbmcaddon
from os import path

from myLogger import myLogger

def getDomainWizdom():
    from requests import get
    try:
        url = 'https://pastebin.com/raw/0rv7wtrm'
        # url = 'https://pastebin.com/raw/1vbRPSGh'
        myDomain = str(get(url).text)
        return myDomain
    except Exception as err:
        myLogger('Caught Exception: error in finding getDomainWizdom: %s' % format(err))
        return "wizdom.xyz" # "lolfw.com"

def get_wizdom_url():
    return getDomainWizdom() + "/api"

def GetWizJson(imdb,prefix_wizdom,color_wizdom,season=0,episode=0,version=0):

    from service import caching_json, colorize_text

    MyScriptID = xbmcaddon.Addon().getAddonInfo('id')

    filename = 'subs.search.wizdom.%s.%s.%s.json'%(imdb,season,episode)
    #old url was: http://json.wizdom.xyz/search.php
    #new url is: http://wizdom.xyz/search
    url = "http://%s/search?action=by_id&imdb=%s&season=%s&episode=%s&version=%s" % (get_wizdom_url(),
                                                                                                imdb,
                                                                                                season,
                                                                                                episode,
                                                                                                version)

    myLogger("GetWizJson url: " + repr(url))

    json_object = caching_json(filename,url)

    subs_rate = []
    #x=1
    id_all_collection=[]
    subtitle_list=[]
    if json_object!=0:
        for item_data in json_object:
            nlabel = "Hebrew"
            nlabel2 = colorize_text(item_data["versioname"],color_wizdom)
            #nlabel2 = colorize_text(prefix_wizdom+' '+item_data["versioname"],color_wizdom)
            #nlabel2 = colorize_text(str(x)+'. '+prefix_wizdom+' '+item_data["versioname"],color_wizdom)
            nicon = colorize_text(prefix_wizdom,color_wizdom)
            #nicon = path.join('resources', 'images', "logoWizdom.png")
            #nicon = path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'images', "logoWizdom.png")
            #nicon = "%s"%("{:.0f}".format(item_data["score"]/2))
            nthumb = "he"

            _id = 'wizdom$$$' + str(item_data["id"])

            url = "plugin://%s/?action=download&versioname=%s&id=%s&source=%s&language=%s&thumbLang=%s" % (
                                                                        MyScriptID,
                                                                        item_data["versioname"],
                                                                        _id,
                                                                        'wizdom',
                                                                        nlabel,
                                                                        nthumb)

            json_data={'url':url,
                       'label':nlabel,
                       'label2':nlabel2,
                       'iconImage':nicon,
                       'thumbnailImage':nthumb,
                       'hearing_imp':'false',
                       'sync': 'true' if int(item_data["score"])>8 else 'false'}
            if item_data["id"] not in id_all_collection:
                id_all_collection.append(item_data["id"])

                subtitle_list.append(json_data)
                links_wizdom=subtitle_list
                #x=x+1

    if (json_object)==0:
        return 0,' ',subtitle_list
    else:
        return subtitle_list,json_object

def wizdom_download_sub(id,archive_file,delay = 2):
    import time
    from service import notify3
    from subscene_api.third_party.cloudscraper import cloudscraper
    global error_page_text
    # from requests import get

    myLogger("Wizdom wizdom_download_sub")
    method = 'GET'
    url = "http://%s/"%format(get_wizdom_url())+"files/sub/"+id

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
        with open(archive_file, 'wb') as f:
            f.write(r.content)
            myLogger(f'Download completed: {archive_file}')
    else:
        notify3(f'Download failed with status code: {r.status_code}')

    # try:
    #     from urllib import urlretrieve
    # except:
    #     from urllib.request import urlretrieve

    # if not path.exists(archive_file):
    #     urlretrieve("http://%s/"%format(get_wizdom_url())+"/files/sub/"+id, archive_file)
