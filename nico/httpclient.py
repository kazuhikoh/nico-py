import sys
import re

from urllib.request import build_opener, HTTPCookieProcessor
from urllib.parse import urlencode
from urllib.error import HTTPError
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup 

def createClient():
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    return opener

def login(opener, user, password):
    #data = f'mail={user}&password={password}'
    data = {
            'mail': user,
            'password': password
    }

    opener.open(
            'https://secure.nicovideo.jp/secure/login',
            urlencode(data).encode('utf-8') 
    )
    
def getVideoPageMax(opener, channelId):
    url = f'https://ch.nicovideo.jp/{channelId}/video'

    try:
        print(f'🐁 Open channel page', file=sys.stderr)
        print(f'🧀 url={url}', file=sys.stderr)
        html = opener.open(url)
        document = BeautifulSoup(html, "html.parser")
        
        # channel is not found
        if document.select_one('section.contents_list') is None:
            print(f'💥 Channel page is not found! ({url})', file=sys.stderr)
            return -1

        footer = document.select_one('footer')

        # no pager
        if footer.menu is None:
            print(f'🧀 pager=none', file=sys.stderr)
            return 1

        options = footer.menu.ul.select_one('li.pages').select_one('select').select('option')

        pageNums = map(lambda e: int(e.text), options)
        pageNumMax = max(pageNums)
        print(f'🧀 pager=[1..{pageNumMax}]', file=sys.stderr)

        return pageNumMax

    except HTTPError as e:
        print(f'💥 Channel page is not found! ({url})', file=sys.stderr)
        return -1 
    
def getVideoItems(opener, channelId, page):
    html = opener.open(f'https://ch.nicovideo.jp/{channelId}/video?sort=f&order=d&page={page}')
    bsDocument = BeautifulSoup(html, "html.parser")

    bsSection = bsDocument.select_one('section.contents_list')
    bsItems = bsSection.select_one('ul.items').select('li.item')
    bsAnchors = map(lambda e: e.select_one('div.item_right').select_one('h6.title').select_one('a'), bsItems)

    items = map(lambda a: {
        'id': re.findall(r'[^/]+$', a['href'])[0],
        'url': a['href'],
        'title': a['title']
    }, bsAnchors)

    return items

