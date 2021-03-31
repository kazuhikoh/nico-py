from . import config
from . import browser

def download(url, outpath):
    cfg = config.load()

    driver = browser.createWebDriver()

    browser.login(driver, cfg['username'], cfg['password'])
    browser.download(driver, url, outpath)

    browser.quit(driver)

