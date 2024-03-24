import xbmc
from resources.modules import iso639

def get_lang_id(language, lang_format):
    try:
        return get_lang_ids([language], lang_format)[0]
    except:
        return ''

def get_lang_ids(languages, lang_format=xbmc.ISO_639_2):
    try:
        lang_ids = []
        for language in languages:
            lang = language.lower()
            if lang in ['pb', 'pob', 'pt-br'] or 'brazil' in lang:
                if lang_format == xbmc.ISO_639_1:
                    lang_ids.append('pt-br')
                elif lang_format == xbmc.ISO_639_2:
                    lang_ids.append('pob')
                elif lang_format == xbmc.ENGLISH_NAME:
                    lang_ids.append('Portuguese (Brazil)')
                continue

            lang = iso639.Lang(language)

            lang_id = None
            if lang_format == xbmc.ISO_639_1:
                lang_id = lang.pt1
            elif lang_format == xbmc.ISO_639_2:
                lang_id = lang.pt3
            elif lang_format == xbmc.ENGLISH_NAME:
                lang_id = lang.name

            if lang_id is not None:
                lang_ids.append(lang_id)

        lang_ids.sort()
        return lang_ids
    except:
        return []