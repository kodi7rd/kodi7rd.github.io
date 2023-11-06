import xbmc
import xbmcaddon
import os
from myLogger import myLogger

def title_ready(title):
    return title.strip().replace("_"," ").replace("."," ").replace(".avi","").replace(".mp4","").replace(".mkv","").lower()

def clean_title(title):
    bad_chars = [';', ':', '!', "*"]
    for i in bad_chars:
        title = title.replace(i, '')
    return title

def isRelatedSub(item, info, all_setting):
    from service import main_languages

    _title = item['tvshow'] if len(item['tvshow']) > 0 else item['title']
    _title = clean_title(title_ready(_title))
    _year = str(item['year'])
    _season = str(item['season'])
    _episode = str(item['episode'])

    title_compare_sub = clean_title(title_ready(info['title']))
    title_compare_year = str(info['year'] if 'year' in info else -1)
    season_compare_sub = str(info['season'] if 'season' in info else -1)
    episode_compare_sub = str(info['episode'] if 'episode' in info else -1)
    rest_text_sub = info['group'] if 'group' in info else info['title']

    # myLogger("LOCAL: t1 - " + repr(title_compare_sub))
    # myLogger("LOCAL: t2 - " + repr(_title))

    for _lang in main_languages:
        # if all_setting[_lang.lower()] == 'true':
        if (_lang.lower() in all_setting and
            all_setting[_lang.lower()] != 'true' and
            xbmc.convertLanguage(_lang, xbmc.ISO_639_1)+"." in rest_text_sub.lower()):
            return False

    if ((title_compare_sub in _title or _title in title_compare_sub) or
        (item['title'].isdigit() and item['title'] in title_compare_year)):
        if len(item['tvshow']) > 0:
            return season_compare_sub == _season and episode_compare_sub == _episode
        else:
            return ((_year in title_compare_sub)
                    or (_year in title_compare_year)
                    or (_year in info['excess'] if 'excess' in info else False))
    return False


def GetLocalJson(item,prefix_local,color_local,all_setting):
    import PTN
    from service import xbmc_translate_path,colorize_text,main_languages #,calc_sub_percent_sync
    from xbmcvfs import listdir

    _item = item

    MyScriptID = xbmcaddon.Addon().getAddonInfo('id')

    mypath=xbmc_translate_path(all_setting["local_path"])
    onlyfiles=[]
    _, files =listdir(mypath)
    for f in files:
        if ('.srt' in  f or '.sub' in f):
            onlyfiles.append(f)
        #onlyfiles = [f for f in listdir(mypath) if ('.srt' in  f or '.sub' in f)]

    myLogger("LOCAL: item - " + repr(_item))

    all_subs_local=[]

    for file1 in onlyfiles:
        split_file=file1.split(".")
        subfix=split_file[len(split_file)-1]

        if subfix=='ass' or subfix=='srt' or subfix=='sub' or subfix=='txt':
            info=(PTN.parse(file1)) #sub filename
            # myLogger("LOCAL: file1 - " + repr(file1))
            # myLogger("LOCAL: info - " + repr(info))
            # myLogger("LOCAL: isRelatedSub - " + repr(isRelatedSub(_item, info, all_setting)))

            if isRelatedSub(_item, info, all_setting):
                nthumb = ''
                nlabel = ''
                rest_text_sub = info['group'] if 'group' in info else info['title']
                for _lang in main_languages:
                    if (_lang.lower() in all_setting and
                        all_setting[_lang.lower()] == 'true' and
                        xbmc.convertLanguage(_lang, xbmc.ISO_639_1)+"." in rest_text_sub.lower()):
                            nthumb = xbmc.convertLanguage(_lang, xbmc.ISO_639_1)
                            nlabel = _lang
                    else:
                        continue

                nlabel2 = colorize_text(file1,color_local)
                #nlabel2 = colorize_text(prefix_local+ ' ' +file1,color_local)
                #nlabel2 = str(count)+'. '+colorize_text(prefix_local+file1,color_local)
                nicon = colorize_text(prefix_local,color_local)

                url = "plugin://%s/?action=download&filename=%s&id=%s&source=%s&language=%s&thumbLang=%s" % (MyScriptID,
                                                                                    xbmc_translate_path(os.path.join(mypath,file1)),
                                                                                    'LOCAL FILE',
                                                                                    'local',
                                                                                    nlabel,
                                                                                    nthumb)

                json_data={'url':url,
                        'label':nlabel,
                        'label2':nlabel2,
                        'iconImage':nicon,
                        'thumbnailImage':nthumb,
                        'hearing_imp':'false',
                        'sync': 'false'}

                all_subs_local.append(json_data)

    return all_subs_local
    #return len(all_subs_local),first,all_subs_local

