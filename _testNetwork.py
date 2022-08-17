# -*- coding=utf-8 -*-
import json
import time
# import datetime
# import hashlib
# import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from selenium.webdriver.common.by import By

PHONE = '18859883968'
PW = 'zkd18859883968'


def netloc_info(url):
    """
    这个是为了获取url的域名，这个代码对只获取网络请求没用，
    """
    res = urlparse(url)
    netloc_orig = res.netloc
    if str(netloc_orig)[0:3] == "www":
        netloc = str(netloc_orig).replace(str(netloc_orig)[0:4], "")
    else:
        netloc = str(netloc_orig)
    return netloc


def info(url):
    """
    调用selenium,开启selenium的日志收集功能，收集所有日志，并从中挑出network部分，分析格式化数据，传出
    :param url:
    :return:
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--headless')
    # chrome_options.add_experimental_option('w3c', False)
    caps = {
        'browserName': 'chrome',
        'goog:loggingPrefs': {
            'browser': 'ALL',
            'driver': 'ALL',
            'performance': 'ALL',
        },
        'goog:chromeOptions': {
            'perfLoggingPrefs': {
                'enableNetwork': True,
            },
            'w3c': False,
        },
    }
    driver = webdriver.Chrome(desired_capabilities=caps, options=chrome_options)
    driver.get(url)
    time.sleep(5)  # 睡眠的作用是等待网页加载完毕，因为还有异步加载的网页，有时候会少拿到请求
    ## 登录页面
    print(f'正在登录……')
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[2]/div[2]/div[1]/div/div[2]/form/p[1]/span/input').send_keys(PHONE)
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[2]/div[2]/div[1]/div/div[2]/form/p[2]/span/input').send_keys(PW)
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[2]/div[2]/div[1]/div/div[2]/form/p[5]/input').click()
    time.sleep(3)
    print(f'登录成功!')

    time.sleep(5)
    listUrl = 'https://my.jia.360.cn/web/myList'
    driver.get(listUrl)
    requests = []
    response = []
    for log in driver.get_log('performance'):
        print(log)
        x = json.loads(log['message'])['message']
        if x["method"] == "Network.responseReceived":
            try:
                ip = x["params"]["response"]["remoteIPAddress"]
            except BaseException as p:
                print(p)
                ip = ""
            try:
                port = x["params"]["response"]["remotePort"]
            except BaseException as f:
                print(f)
                port = ""
            response.append(
                [
                    x["params"]["response"]["url"],
                    ip,
                    port,
                    x["params"]["response"]["status"],
                    x["params"]["response"]["statusText"],
                    x["params"]["type"]
                ]
            )
        elif x["method"] == "Network.requestWillBeSent":
            requests.append(
                [
                    x["params"]["request"]["url"],
                    x["params"]["initiator"]["type"],
                    x["params"]["request"]["method"],
                    x["params"]["type"]
                ]
            )
        else:
            pass
    newlist = []
    for iqurl in requests:
        qwelist = [iqurl]
        for ipurl in response:
            if iqurl[0] == ipurl[0]:
                qwelist.append(ipurl)
            else:
                pass
        newlist.append(qwelist)
    for ipurl in response:
        p = 0
        for i in newlist:
            if len(i) == 1:
                pass
            else:
                if ipurl == i[1]:
                    p += 1
                else:
                    pass
        if p == 0:
            newlist.append(ipurl)
        else:
            pass
    return_list = []
    for a in newlist:
        dic = {
            "url": "",
            "method": "",
            "status": "",
            "statusText": "",
            "type": "",
            "initiator": "",
            "netloc": "",
            "remoteIPAddress": "",
            "remotePort": ""

        }
        if len(a) == 2:
            dic["url"] = a[0][0]
            dic["initiator"] = a[0][1]
            dic["method"] = a[0][2]
            dic["type"] = a[0][3]
            dic["netloc"] = netloc_info(a[0][0])
            dic["remoteIPAddress"] = a[1][1]
            dic["remotePort"] = a[1][2]
            dic["status"] = a[1][3]
            dic["statusText"] = a[1][4]
            return_list.append(dic)
        elif len(a) == 1:
            if len(a[0]) == 4:
                dic["url"] = a[0][0]
                dic["netloc"] = netloc_info(a[0][0])
                dic["initiator"] = a[0][1]
                dic["method"] = a[0][2]
                dic["type"] = a[0][3]
                return_list.append(dic)
            elif len(a[0]) == 6:
                dic["url"] = a[0][0]
                dic["netloc"] = netloc_info(a[0][0])
                dic["remoteIPAddress"] = a[0][1]
                dic["remotePort"] = a[0][2]
                dic["status"] = a[0][3]
                dic["statusText"] = a[0][4]
                dic["type"] = a[0][5]
                return_list.append(dic)
            else:
                pass
        else:
            pass
    driver.close()
    driver.quit()
    return return_list

if __name__ == '__main__':
    loginUrl = 'https://my.jia.360.cn/web/index'
    res=info(url=loginUrl)
    print(res)
