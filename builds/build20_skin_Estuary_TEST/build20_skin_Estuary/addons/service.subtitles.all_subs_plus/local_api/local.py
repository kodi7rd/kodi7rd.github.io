import xbmc
import xbmcaddon
import os
from myLogger import myLogger

def GetLocalJson(item,prefix_local,color_local,all_setting):
    import PTN
    from service import xbmc_translate_path,colorize_text #,calc_sub_percent_sync
    from xbmcvfs import listdir

    MyScriptID = xbmcaddon.Addon().getAddonInfo('id')

    mypath=xbmc_translate_path(all_setting["storage"])
    onlyfiles=[]
    _, files =listdir(mypath)
    for f in files:
        if ('.srt' in  f or '.sub' in f):
            onlyfiles.append(f)
        #onlyfiles = [f for f in listdir(mypath) if ('.srt' in  f or '.sub' in f)]

    #count=0
    all_subs_local=[]
    #first=' '
    for file1 in onlyfiles:
        split_file=file1.split(".")
        subfix=split_file[len(split_file)-1]

        if subfix=='ass' or subfix=='srt' or subfix=='sub' or subfix=='txt':
            info=(PTN.parse(file1))
            title_compare=info['title'].strip().replace("_"," ").replace("."," ").replace(".avi","").replace(".mp4","").replace(".mkv","").lower()

            info2=(PTN.parse(item['file_original_path']))
            title_compare_file=info2['title'].strip().replace("_"," ").replace("."," ").replace(".avi","").replace(".mp4","").replace(".mkv","").lower()

            info3=(PTN.parse(xbmc.getInfoLabel("VideoPlayer.title")))
            title_compare_video=info3['title'].strip().replace("_"," ").replace("."," ").replace(".avi","").replace(".mp4","").replace(".mkv","").lower()

            if title_compare in title_compare_file or title_compare in title_compare_video:
                if "en" in info['group'].lower():
                    nthumb = 'en'
                    nlabel = 'English'
                elif "he" in info['group'].lower():
                    nthumb = 'he'
                    nlabel = 'Hebrew'
                else:
                    nthumb = ''
                    nlabel = ''

                nlabel2 = colorize_text(file1,color_local)
                #nlabel2 = colorize_text(prefix_local+ ' ' +file1,color_local)
                #nlabel2 = str(count)+'. '+colorize_text(prefix_local+file1,color_local)
                nicon = colorize_text(prefix_local,color_local)

                url = "plugin://%s/?action=download&filename=%s&id=%s&source=%s&language=%s&thumbLang=%s" % (MyScriptID,
                                                                                    xbmc_translate_path(os.path.join(mypath,file1)),
                                                                                    'LOCAL FILE',
                                                                                    'LOCAL FILE',
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
                # percent = calc_sub_percent_sync(json_data, array_original)
                # #if precent==0:

                # percent2 = calc_sub_percent_sync(json_data, array_original)

                # if (percent>30 or percent2>30):
                #     all_subs_local.append(json_data)

                # if count==0:
                #     first=file1
                # count=count+1

    return all_subs_local
    #return len(all_subs_local),first,all_subs_local