import time
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import chromedriver_binary
import os
import requests
import schedule

def setupDriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options = options)
    return driver

def readConfig():
    config = ConfigParser()
    config.read('./config.ini')

    keio_id = config.get('keio', 'ID')
    keio_pwd = config.get('keio', 'PW')

    slack_token = config.get('slack', 'token')
    slack_channel = config.get('slack', 'channel')

    return keio_id, keio_pwd, slack_token, slack_channel

def login(driver, keio_id, keio_pwd):
    driver.get('https://portal.keio.jp/')
    WDW(driver, 15).until(EC.presence_of_all_elements_located)

    driver.find_element_by_id('username').send_keys(keio_id)
    driver.find_element_by_id('password').send_keys(keio_pwd)
    driver.find_element_by_name('_eventId_proceed').send_keys(Keys.ENTER)

    return driver

def getNewsPic(driver):
    WDW(driver, 15).until(EC.presence_of_all_elements_located)
    driver.find_element_by_css_selector('.btn.btn-link').send_keys(Keys.ENTER)
    time.sleep(3)

    page_width = driver.execute_script('return document.body.scrollWidth')
    page_height = driver.execute_script('return document.body.scrollHeight')
    driver.set_window_size(page_width, page_height)
    now = time.time()
    pngFile = './' + str(now) + '.png'
    driver.save_screenshot(pngFile)
    return pngFile, driver

def sendSlackMsg(pngFile, token, channel):
    url = 'https://slack.com/api/files.upload'
    data = {
        'token': token,
        'channels': channel,
        'title': pngFile,
        'initial_comment': 'https://portal.keio.jp'
    }
    files = {
        'file': open(pngFile, 'rb')
    }
    requests.post(url, data = data, files = files)

def sendSlackErr(token, channel, msg):
    url = 'https://slack.com/api/chat.postMessage'
    data = {
        'token': token,
        'channels': channel,
        'text': 'an error occurd in ' + msg
    }
    requests.post(url, data = data)


def main():
    keio_id, keio_pwd, slack_token, slack_channel = readConfig()
    driver = setupDriver()
    try:
        driver = login(driver, keio_id, keio_pwd)
    except:
        sendSlackErr(slack_token, slack_channel, 'login')
    try:
        pngFile, driver = getNewsPic(driver)
    except:
        sendSlackErr(slack_token, slack_channel, 'acquire news')
    driver.quit()
    sendSlackMsg(pngFile, slack_token, slack_channel)
    os.remove(pngFile)

schedule.every().hour.at(':10').do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
