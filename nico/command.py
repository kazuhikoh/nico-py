from . import config
from . import httpclient
from . import browser

def list(channelId):
    cfg = config.load()

    opener = httpclient.createClient()
    httpclient.login(opener, cfg['username'], cfg['password'])

    pageMax = httpclient.getVideoPageMax(opener, channelId)

    if (pageMax == -1):
        return False

    for i in range(pageMax):
        items = httpclient.getVideoItems(opener, channelId, i+1)
        for it in items:
            id = it['id']
            title = it['title']
            print(f'{id} "{title}"')

    return True

def download(url, outpath):
    cfg = config.load()

    driver = browser.createWebDriver()

    browser.login(driver, cfg['username'], cfg['password'])
    browser.download(driver, url, outpath)

    browser.quit(driver)

