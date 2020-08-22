import time
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import chromedriver_binary
import os
import requests
import copy
import re
import json
import difflib as diff


def setupDriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver


def readConfig():
    config = ConfigParser()
    config.read('./config.ini')

    keio_id = config.get('keio', 'ID')
    keio_pwd = config.get('keio', 'PW')

    slack_token = config.get('slack', 'token')
    slack_channel = config.get('slack', 'channel')

    text_mode = config.getboolean('global', 'textmode')

    return keio_id, keio_pwd, slack_token, slack_channel, text_mode


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


def getNewsContent(driver):
    WDW(driver, 15).until(EC.presence_of_all_elements_located)
    driver.find_element_by_css_selector('.btn.btn-link').send_keys(Keys.ENTER)
    WDW(driver, 15).until(EC.presence_of_all_elements_located)
    time.sleep(3)
    news_content = driver.find_element_by_xpath(
        "/html/body/div/div[3]/section/div[2]/div[1]/div[4]").text
    return news_content, driver


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
    requests.post(url, data=data, files=files)


def sendSlackMsgDiff(token, channel, add, delete):
    att = []
    if add:
        att.append(
            {
                'color': 'good',
                'text': '\n'.join(add),
            }
        )
    if delete:
        att.append(
            {
                'color': 'danger',
                'text': '\n'.join(delete),
            }
        )
    url = 'https://slack.com/api/chat.postMessage'
    data = {
        'channel': channel,
        'attachments': att,
        'text': 'https://portal.keio.jp'
    }
    headers = {"content-type": "application/json",
               "Authorization": "Bearer "+token}
    requests.post(url, data=json.dumps(data), headers=headers).json()


def sendSlackErr(token, channel, msg):
    url = 'https://slack.com/api/chat.postMessage'
    data = {
        'token': token,
        'channel': channel,
        'text': 'an error occurd in ' + msg
    }
    requests.post(url, data=data,)


def stringDiff(strNew, strOld):
    strNew_lines_raw = strNew.splitlines()
    strNew_lines = []
    d = ''
    for s in strNew_lines_raw:
        if re.match(r'\d{4}\/\d{2}\/\d{2}', s):
            d = copy.copy(s)
        else:
            s = d+' '+s
            d = ''
            strNew_lines.append(s)
    strOld_lines_raw = strOld.splitlines()
    strOld_lines = []
    d = ''
    for s in strOld_lines_raw:
        if re.match(r'\d{4}\/\d{2}\/\d{2}', s):
            d = copy.copy(s)
        else:
            s = d+' '+s
            d = ''
            strOld_lines.append(s)
    addedLines = []
    deletedLines = []
    for d in diff.context_diff(strOld_lines, strNew_lines):
        if re.match(r'\-', d) and not re.match(r'\-\-\-', d):
            deletedLines.append(d)
        elif re.match(r'\+', d) and not re.match(r'\+\+\+', d):
            addedLines.append(d)
    return addedLines, deletedLines


def main():
    keio_id, keio_pwd, slack_token, slack_channel, text_mode = readConfig()
    try:
        f = open('.lastContent', 'r', encoding='utf-8')
        newsContent = f.read()
        f.close()
    except:
        newsContent = ''
    driver = setupDriver()
    try:
        driver = login(driver, keio_id, keio_pwd)
    except:
        sendSlackErr(slack_token, slack_channel, 'login')
        exit
    pngFile = ''
    newNewsContent = ''
    try:
        if text_mode:
            newNewsContent, driver = getNewsContent(driver)
        else:
            pngFile, driver = getNewsPic(driver)
    except:
        sendSlackErr(slack_token, slack_channel, 'acquire news')
        exit
    driver.quit()
    if newsContent != newNewsContent and text_mode:
        add, delete = stringDiff(newNewsContent, newsContent)
        sendSlackMsgDiff(slack_token, slack_channel,
                         add, delete)
        newsContent = newNewsContent
        f = open('.lastContent', 'w', encoding='utf-8')
        f.write(newsContent)
        f.close()
    elif not text_mode:
        sendSlackMsg(pngFile, slack_token, slack_channel)
        os.remove(pngFile)


main()
