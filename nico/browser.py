import sys
import subprocess
import time
import json
import base64
import re

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as cond
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager


def createWebDriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')

    desired_capabilities = DesiredCapabilities.CHROME.copy()
    desired_capabilities["loggingPrefs"] = {
        "performance": "ALL",
    }
    desired_capabilities["goog:loggingPrefs"] = {
        "performance": "ALL",
    }

    driver = webdriver.Chrome(
        executable_path=ChromeDriverManager().install(),
        options=options,
        desired_capabilities=desired_capabilities,
    )

    return driver

def quit(driver):
    print(f'🐁 quit', file=sys.stderr)
    driver.quit()       

def login(driver, user, password):
    login_url = 'https://account.nicovideo.jp/login'
    print(f'🐁 login...', file=sys.stderr)
    print(f'🧀 url={login_url}', file=sys.stderr)
    driver.get(login_url)

    elUser = driver.find_element_by_id('input__mailtel')
    elPass = driver.find_element_by_id('input__password')
    elLogin = driver.find_element_by_id('login__submit')

    elUser.send_keys(user)
    elPass.send_keys(password)
    elLogin.submit()

    expected_url = 'www.nicovideo.jp'
    wait(driver, 5).until(cond.url_changes(expected_url)) 

    curr_url = driver.current_url
    print(f'🐁 login OK', file=sys.stderr)

def download(driver, url, outpath):
    print(f'🐁 open video page', file=sys.stderr)
    print(f'🧀 url={url}', file=sys.stderr)
    driver.get(url)
#    wait(driver, 5).until(cond.url_changes(url))

    # click play button
    print(f'🐁 play video', file=sys.stderr)
    elPlay = driver.find_element_by_css_selector('button.ActionButton.ControllerButton.PlayerPlayButton')
    elPlay.click()

    # wait  
    time.sleep(2) 

    print(f'🐁 search', file=sys.stderr)

    stream_url = find_stream_from_logs(driver)

    if stream_url == '':
        print(f'💥 No streaming packet!', file=sys.stderr)
        return False

    print(f'🐁 capture stream', file=sys.stderr)
    print(f'🧀 in={stream_url}', file=sys.stderr)
    print(f'🧀 out={outpath}', file=sys.stderr)

    res = subprocess.run([
        'ffmpeg', '-i', stream_url, '-c', 'copy', outpath
    ])

    return (res.returncode == 0)

def find_stream_from_logs(driver): 
    logs = driver.get_log("performance")
    messages = map(lambda log: json.loads(log['message'])['message'], logs)

    for msg in messages:
        if not "response" in msg["params"]:
            continue
        if not "url" in msg["params"]["response"]:
            continue

        url = msg['params']['response']['url']
        if "master.m3u8" in url:
            print(f'🧀 master={url}', file=sys.stderr)

            # Access response body
            # - https://vanilla.aslushnikov.com/?Network.getResponseBody
            requestId = msg['params']['requestId']
            #print(f'🧀 messages.params.requestId={requestId}', file=sys.stderr)

            try:
                resObj = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestId})
                resRaw = resObj['body']
                if (resObj['base64Encoded']):
                    b64 = resObj['body']
                    resRaw = base64.b64decode(b64).decode()

                print('--------------------------------', file=sys.stderr)
                print(resRaw, file=sys.stderr)
                print('--------------------------------', file=sys.stderr)

                # Select best quality playlist from master
                urlPlaylistRoot = re.sub(r'[^/]+$', '', url)
                urlPlaylistPath = find_playlist_from_master(resRaw)

                urlPlaylist = f'{urlPlaylistRoot}{urlPlaylistPath}'

                print(f'🧀 playlist={urlPlaylist}', file=sys.stderr)
                return urlPlaylist

            except WebDriverException as e:
                print(e, file=sys.stderr)

    # fallback
    return ''

def find_playlist_from_master(master):
    lines = master.splitlines()

    # contains 'BANDWIDTH=*******,'
    bandwidthMax = 0
    bandwidthMaxIndex = 0
    for index, line in enumerate(lines):
        if 'BANDWIDTH=' in line:
            bandwidth = int( re.findall('BANDWIDTH=([^,]+)', line)[0] )
            print(f'{index}: {bandwidth} max={bandwidthMax}', file=sys.stderr)
            if bandwidth > bandwidthMax:
                bandwidthMax = bandwidth
                bandwidthMaxIndex = index

    bestPlaylist = lines[bandwidthMaxIndex + 1]
    return bestPlaylist

