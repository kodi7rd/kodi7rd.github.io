import os
import shutil
import zipfile
import asyncio
import requests

import re
import unicodedata
import json
import zlib

import xbmc
import xbmcvfs
import xbmcaddon

import time

from bs4 import BeautifulSoup

#from .myLogger import myLogger
import sys
sys.path.append(os.path.abspath('..'))
from myLogger import myLogger

import urllib3
import ssl
from requests import adapters
from .third_party.cloudscraper import cloudscraper


class TLSAdapter(adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = urllib3.poolmanager.PoolManager(num_pools=connections,
                                                           maxsize=maxsize,
                                                           block=block,
                                                           ssl_version=ssl.PROTOCOL_TLSv1_2,
                                                           ssl_context=ctx)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

error_page_text = 'Error in get Subscene page: '
class SubtitleAPI:

    URL = 'https://www.subscene.com'

    def __init__(self, *args, **kwargs) -> None:  # args are languages pass it like ('english', 'arabic', 'farsi/persian')

        self.search_page_slugs = '/subtitles/searchbytitle'  # subscene search slug

        self.langs = []
        if args:
            for lang in args:
                self.langs.append(lang.lower())

    # Method Bellow returns a BeautifulSoup object of our html response
    def parse(self, html):
        myLogger("Subscene parse data" + repr(html))
        return BeautifulSoup(html, 'html.parser')

    # this method simply call and endpoint and return it as plantext
    def get_html_by_title(self, title, delay = 2) -> str:
        from service import notify3
        global error_page_text

        myLogger("Subscene get_html_by_title")
        method = 'GET'

        url = f'{self.URL}{self.search_page_slugs}/?query='+title;

        try:
            for i in range(5):
                myLogger("Subscene search data: method " + method +"  url - " + repr(url) + " | title: " + title )
                s = cloudscraper.create_scraper(interpreter='native')
                r = s.request(method, url)
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
            return r.text

        return r.text

    # this method simply call and endpoint and return it as plantext
    def get_html_by_url(self, url, delay = 2) -> str:
        from service import notify3
        global error_page_text

        myLogger("Subscene get_html_by_url")
        method = 'GET'

        try:
            for i in range(5):
                myLogger("Subscene search data: method " + method +"  url - " + repr(url))
                s = cloudscraper.create_scraper(interpreter='native')
                r = s.request(method, url)
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
            return r.text

        return r.text

    def download_zip(self, url, filename, delay = 2):
        from service import notify3
        global error_page_text

        myLogger("Subscene download_zip")
        method = 'GET'

        try:
            for i in range(5):
                myLogger("Subscene download_zip url: " + repr(url))
                s = cloudscraper.create_scraper(interpreter='native')
                r = s.request(method, url)
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
            return r.text

        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
                myLogger(f'Download completed: {filename}')
        else:
            notify3(f'Download failed with status code: {r.status_code}')


    # this method parse html to extract only results and return as list
    def parse_search_results(self, soup):
        results = []

        try:
            for element in soup.find(class_="search-result").find_all('li'):
                element = element.find('a')
                link = element.get('href')
                name = element.get_text()
                results.append({'link': link, 'name': name})
            # a list of dicts [...,{...},{'link': '/', 'name': ''},{...},...]
        except:
            myLogger("Subscene search parse error")

        return results

    # this method can make a search query to subscene and a list of dict results contain name and link
    def search(self, title, timeout = 20) -> BeautifulSoup:
        response = self.get_html_by_title(title)
        return self.remove_duplicate_dicts(self.parse_search_results(self.parse(response)))

    def remove_duplicate_dicts(self, ListOfDicts):
        toSet = set()
        newListOFDicts = []
        for i in ListOfDicts:
            y = tuple(i.items())
            if y not in toSet:
                toSet.add(y)
                newListOFDicts.append(i)
        return newListOFDicts

    # this method excutes ascync functions
    def get_download_link(self, url, lang):
        myLogger("Subscene get_download_link")

        soup = self.parse(self.get_html_by_url(url))

        zip_link = ''
        for element in soup.find_all('div', class_='download'):
            zip_link = element.a.get('href')

        full_zip_url = f'{self.URL}{zip_link}'
        myLogger("Subscene get_download_link full_zip_url: " + repr(full_zip_url))

        if full_zip_url == f'{self.URL}':
            return 'Subscene download url not found'

        return full_zip_url

    # filter_langs(listOfDirectories) method filter initalized langs an returm a new list of subtitles

    def filter_langs(self, listDicts):
        if self.langs:
            newList = []
            for sub in listDicts:
                if sub['lang'].lower() in self.langs:
                    newList.append(sub)
            return newList
        return listDicts

    # this method return subtitle and link for download page

    def scrape_list(self, url):
        soup = self.parse(self.get_html_by_url(url))

        items = []
        for element in soup.find_all('td', class_='a1'):
            lang, name = None, None
            link = element.a.get('href')
            for index, child in enumerate(element.a.children):
                if child.name == 'span':
                    spanValue = child.text.strip()
                    spanValueLower = spanValue.lower()
                    if index == 1:
                        lang = spanValueLower
                    elif index == 3:
                        name = spanValue
            if lang and name and link:
                items.append({
                    'lang': lang,
                    'name': name,
                    'link': link
                })
        # return list like: [...,{'lang':'english', 'name':'Movie Name', 'link':'/slug'},...]
        myLogger("Subscene scrape_list result: " + repr(items))
        return self.filter_langs(items)

    # scrape_download_page(url) method scrape subtitle author, download link and release information
    async def scrape_download_page(self, url):
        soup = self.parse(self.get_html_by_title(url))
        print(soup)
        release_info_list = []
        author, download = None, None
        for element in soup.find_all('li', class_='release'):
            for child in element.children:
                if child.name == 'div':
                    release_info_list.append(child.text.strip().lower())
        for element in soup.find_all('li', class_='author'):
            for child in element.children:
                if child.name == 'a':
                    author = child.text.strip()
        download = soup.find(id='downloadButton').get('href')
        if author and download and release_info_list:
            return {
                'author': author,
                'release_info': release_info_list,
                'download': download
            }
        return {}

    # filter_release_type(ListOfDicts, typeOfRelease) method filters based on type of release passed in
    def filter_release_type(self, ListOfDicts, typeOfRelease):
        newListOfDicts = []
        for obj in ListOfDicts:
            name = obj.get('name', None)
            if typeOfRelease in name:
                newListOfDicts.append(obj)
        return newListOfDicts

    # filter based on seasons

    def find_season(self, listOfDicts, title, season_num):
        season_num = int(season_num)

        seasons = [(1, 'First Season'), (2, 'Second Season'), (3, 'Third Season'), (4, 'Fourth Season'), (5, 'Fifth Season'),
                   (6, 'Sixth Season'), (7, 'Seventh Season'), (8, 'Eighth Season'), (9, 'Ninth Season'), (10, 'Tenth Season'), (11, 'Eleventh Season'), (
                       12, 'Twelfth Season'), (13, 'Thirteenth Season'), (14, 'Fourteenth Season'), (15, 'Fifteenth Season'), (16, 'Sixteenth Season'),
                   (17, 'Seventeenth Season'), (18, 'Eighteenth Season'), (19, 'Nineteenth Season'), (20, 'Twentieth Season')]

        detect_season = None
        for index, season in seasons:
            if index == season_num:
                detect_season = season
                break;

        newListOfDicts = []
        if listOfDicts:
            for obj in listOfDicts:
                name = obj.get('name', None)
                if name and detect_season is not None:
                    if detect_season in name and title in name:
                        newListOfDicts.append(obj)
                        break;
            return newListOfDicts

        return []

    # this method make a string like S01E05 for subscene tv series search pattern

    def make_series_target_string(self, se, ep):
        se = int(se)
        ep = int(ep)

        if se < 10:
            se = f'0{se}'
        if ep < 10:
            ep = f'0{ep}'
        return f'S{se}E{ep}'.lower()

    # this method filter subtitles based on episode number

    def filter_episodes(self, ListOfDicts, string):
        newListOfDicts = []
        for obj in ListOfDicts:
            name = obj.get('name', None)
            if name:
                if string.lower() in name.lower():
                    newListOfDicts.append(obj)
        return newListOfDicts

    # this method returns subtitles as list of dicts filterd and ready to download
    def movie(self, title=None, year=None, imdb_id=None, release_type=None):
        myLogger("Subscene_movie search: imdb: %s | title: %s | year: %s" %(imdb_id,title,year))
        search_results = self.search(title)
        myLogger("Subscene_movie search_results: " + repr(search_results))
        sub_list = []

        if len(search_results) > 1:
            filtered_results = []
            for obj in search_results:
                name = obj.get('name', None)
                if year:
                    if str(year) in name:
                        filtered_results.append(obj)
                else:
                    filtered_results = search_results
            search_results = filtered_results

        myLogger("Subscene_movie search_results filtered by year: " + repr(search_results))
        if search_results:
            link = search_results[0]['link']
            url = f'{self.URL}{link}'
            myLogger("Subscene_movie page url: " + repr(url))
            sub_list = self.scrape_list(url)
            if release_type:
                sub_list = self.filter_release_type(sub_list, release_type)
            myLogger("Subscene_movie subtitles list filtered by language and release type: " + repr(sub_list))

        return sub_list

    # tvshow method returns list of subtitles target based on filter passed in
    def tvshow(self, title=None, imdb_id=None, release_type=None, season=None, episode=None):
        myLogger("Subscene_tvshow search: imdb: %s | title: %s | season: %s | episode: %s" %(imdb_id,title,season,episode))
        search_results = self.search(title)
        myLogger("Subscene_tvshow search_results: " + repr(search_results))
        sub_list = []

        if season:
            search_results = self.find_season(search_results, title, season)
        if search_results:
            link = search_results[0]['link']
            url = f'{self.URL}{link}'
            myLogger("Subscene_tvshow page url: " + repr(url))
            sub_list = self.scrape_list(url)
            if release_type:
                sub_list = self.filter_release_type(sub_list, release_type)
            myLogger("Subscene_tvshow subtitles list filtered by language and release type: " + repr(sub_list))

            if season and episode:
                se = self.make_series_target_string(season, episode)
                sub_list = self.filter_episodes(sub_list, se)

        myLogger("Subscene_tvshow subtitles list filtered by season and episode: " + repr(sub_list))
        return sub_list

    def __str__(self):
        str_ = ''
        for string in self.langs:
            str_ += f',{string} '
        return f'<subsceneScraper Class {str_}>'

    def GetSubsceneJson(self,imdb_id,item,prefix_subscene,color_subscene):
        MyScriptID = xbmcaddon.Addon().getAddonInfo('id')

        #def movie(self, title=None, year=None, imdb_id=None, release_type=None):
        #subscene.movie(title='Tenet',year=2020,release_type='bluray')
        #result = subscene.movie(title='Finch',year=2021)

        #def tvshow(self, title=None, imdb_id=None, release_type=None, season=None, episode=None):

        if item["tvshow"]:
            result = self.tvshow(imdb_id=imdb_id,title=item["tvshow"],season=item["season"], episode=item["episode"])
        elif item["title"]:
            result = self.movie(imdb_id=imdb_id,title=item["title"],year=item["year"])

        subtitle_list=[]
        #z=1

        for itt in result:
            nm = itt['name']
            lang = itt['lang']

            if lang.lower() == 'english':
                nthumb = 'en'
            elif lang.lower() == 'hebrew':
                nthumb = 'he'
            else:
                nthumb = ''

            nlabel = lang
            nlabel2 = '[COLOR '+color_subscene+']'+nm+'[/COLOR]'
            #nlabel2 = '[COLOR '+color_subscene+']'+prefix_subscene+' '+nm+'[/COLOR]'
            #nlabel2 = '[COLOR '+color_subscene+']'+str(z)+'. '+prefix_subscene+' '+nm+'[/COLOR]'
            nicon = '[COLOR '+color_subscene+']'+prefix_subscene+'[/COLOR]'

            link = 'https://subscene.com'+itt['link']
            _id = "subscene$$$" + link.split("/")[-1]

            url = "plugin://%s/?action=download&link=%s&id=%s&source=%s&language=%s&thumbLang=%s" % (MyScriptID,
                                                                                link,
                                                                                _id,
                                                                                'subscene',
                                                                                lang,
                                                                                nthumb)

            json_data={'url':url,
                            'label':nlabel,
                            'label2':nlabel2,
                            'iconImage':nicon,
                            'thumbnailImage':nthumb,
                            'hearing_imp':'false',
                            'sync': 'false'}

            subtitle_list.append(json_data)
            links_subscene=subtitle_list
            #z=z+1

        myLogger("Subscene subtitles final: " + repr(subtitle_list))
        return subtitle_list,result

    # def subscene_download_process(self, params, mode_subtitle):
    #     from service import download

    #     download_url = self.get_download_link(params["link"], params["language"])
    #     if download_url != '' :
    #         subs,temp = download(params["id"],params["language"],'','',mode_subtitle,download_url)
    #         return subs,temp

    #     return [],' '