from selenium import webdriver
# from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
import time
import datetime
import re
import requests
import json
import os

CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
SERVER = 'on'
PHONE = os.environ['PHONE']
PW = os.environ['PW']
SCKEY = os.environ['SCKEY']


dkStart = datetime.datetime.now()

def sendMsg(m, error=''):
    if SERVER == 'on':
        timeNow = time.strftime('%Y-%m-%d', time.localtime())
        duration = datetime.datetime.now() - dkStart
        if error == '':
            msg = '{} {}! 耗时{}秒。'.format(timeNow, m, duration.seconds)
        else:
            msg = '{} {}!'.format(timeNow, error)
        url = 'https://sctapi.ftqq.com/{}.send?title={}&desp={}'.format(SCKEY, msg, '{}\n{}'.format(msg, error))
        re.get(url)

def millisecond_to_time(millis):
    """13位时间戳转换为日期格式字符串"""
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(millis/1000))

def login(driver):
    loginUrl = 'https://my.jia.360.cn/web/index'
    driver.get(loginUrl)

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

## 重新加载一遍，以获得cookie里的值
def getcookies():
    ### /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir='/Users/yanplr/Library/Application\ Support/Google/Chrome'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    ## 部署到github action时删除debugger_address
#     options.debugger_address = '127.0.0.1:9222'
    d = DesiredCapabilities.CHROME
    d['goog:loggingPrefs'] = {'performance':'ALL'}
    s = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=s, options=options, desired_capabilities=d)
    driver.delete_all_cookies()

    loginUrl = 'https://my.jia.360.cn/web/index'
    
    login(driver)

    ## 重新get到登录页面，以获取cookies
    print('重新登录，以获取cookies')
    driver.get(loginUrl)
    time.sleep(1)

    ## 获取cookies
    print('正则匹配获取cookies和sid')
    pattern = re.compile('^.*Q=(.*?); __NS_.*T=(.*?);.*jia_web_sid=(.*?%3D).*$')
    for entry in driver.get_log('performance'):
        print(entry)
        print('------------------------')
        try:
            m = pattern.match(entry['message'])
            cookies_Q = m.group(1)
            cookies_T = m.group(2)
            cookies_sid = m.group(3)
            print(f'成功获取cookies')
            # print(f'cookies = {m.group()}')
            print(f'cookies_Q = {cookies_Q}')
            print(f'cookies_T = {cookies_T}')
            print(f'cookies_sid = {cookies_sid}')
            return cookies_Q, cookies_T, cookies_sid
        except:
            pass

def getVideoDict(cookies_Q, cookies_T, cookies_sid):
    imageHeaders = {
        'Host':'q3.jia.360.cn',
        'Accept':'*/*',
        'Content-Type':'application/json',
        'Cache-Control':'no-cache',
        'User-Agent':'360%E6%91%84%E5%83%8F%E6%9C%BA/202205251509 CFNetwork/1335.0.3 Darwin/21.6.0',
        'Connection':'keep-alive',
        
        'Accept-Language':'zh-CN,zh-Hans;q=0.9',
        'Authorization':'Basic: someValue',
        'Content-Length':'206',
        'Accept-Encoding':'gzip, deflate, br',
    }

    imageHeaders['Cookie'] = 'q=' + cookies_Q + ';' + 't=' + cookies_T + ';qid=229226876;sid=' + cookies_sid

    # 构造data， taskid去掉， date去掉
    # 获取前几天的，就是page的值改为1，2，3……
    imageData = {
        "parad":"{\"needTotal\":1,\"taskid\":\"\",\"imgType\":3,\"withCry\":0,\"date\":\"\",\"sn\":\"3601Q0700002176\",\"page\":0}","ver":"7.7.6","from":"mpc_ipcam_ios"
    }
    imageData = json.dumps(imageData)

    # print(imageHeaders)

    ## 进行requests
    imageUrl = 'https://q3.jia.360.cn/image/getImagesBySn?lang=zh-Hans'
    imageJson = requests.post(url=imageUrl, headers=imageHeaders, data=imageData, verify=False).json()
    imageNum = imageJson['images']['total']
    print(f'视频回放数量为imagenum = {imageNum}')

    ## 修改 imageData['parad']里的page
    pagesNum = imageNum // 20

    ## 保存位置
    date = str(datetime.date.today()).replace('-', '')
    saveDir = './' + date
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    print(f'总共{pagesNum}个page')
    videoDict = dict()
    for page in range(0, pagesNum + 1):
    # for page in range(0, 1):  
        payload = imageData[:122] + str(page) + imageData[123:]

        imageJson = requests.post(url=imageUrl, headers=imageHeaders, data=payload, verify=False).json()
        js = imageJson['images']['data']
        jsLen = len(js)

        for i in range(0, jsLen):
        # for i in range(0, 1):
            videoUrl = js[i]['videoUrl']
            # print(f'第{page*20 + i + 1}个/共{imageNum}个，videoUrl = {videoUrl}')

            # eventTime 为时间戳
            eventTime = js[i]['eventTime']
            # videoTime 为时间戳转化过来的标准时间，准备作为mp4的文件名
            videoTime = millisecond_to_time(eventTime).replace('-', '').replace(' ', '_').replace(':', '_')
            
            print(f'第{page*20 + i + 1}个/共{imageNum}个, {videoTime}')
            
            videoDict[videoTime] = videoUrl

    downloadVideos(videoDict, saveDir, cookies_Q, cookies_T, cookies_sid)
    msg = '成功同步' + str(imageNum) + '条360视频'
    sendMsg(msg)

def downloadVideos(videoDict, saveDir, cookies_Q, cookies_T, cookies_sid):
    videoHeaders = {
        'Host':	'q3.jia.360.cn',
        'Accept':'image/*;q=0.8',
        
        'User-Agent':'360HomeGuard_NoPods/7.7.6 (iPad; iOS 15.6; Scale/2.00)',
        'Accept-Language':'zh-CN,zh-Hans;q=0.9',
        'Accept-Encoding':'gzip, deflate, br',
        'Connection':'keep-alive',
    }
    videoHeaders['Cookie'] = 'q=' + cookies_Q + ';' + 't=' + cookies_T + ';qid=229226876;sid=' + cookies_sid

    for key, value in videoDict.items():
        try:
            videoTime = key
            videoUrl = value
            # requests到video的二进制数据
            videoContent = requests.get(url=videoUrl, headers=videoHeaders, verify=False).content

            ## 保存为
            mp4Name = saveDir + '/' + videoTime + '.mp4'
            with open(mp4Name, 'wb') as f:
                f.write(videoContent)
                f.close()
        except:
            pass

if __name__ == '__main__':
    ## 获取cookies
    cookies_Q, cookies_T, cookies_sid = getcookies()

    ## 临时设置cookies
#     cookies_Q = 'u%3Dyvat888funa%26n%3D%26le%3D%26m%3DZGHjWGWOWGWOWGWOWGWOWGWOAwZl%26qid%3D229226876%26im%3D1_t0105d6cf9b508f72c8%26src%3Dpcw_ipcam_live%26t%3D1'
#     cookies_T = 's%3Dcc6f74495cb4897c555b98a4200a486c%26t%3D1660659928%26lm%3D%26lf%3D2%26sk%3D6f3854937956fe8d4691d41c4716ab03%26mt%3D1660659928%26rc%3D%26v%3D2.0%26a%3D0'
#     cookies_sid = '7de55fb60d0c690b380e4b3c5b719467E40W8Iz%2BCs10aPFbt1HvUieTynC%2B996GDypGrOhK9JU%3D'
    
    ## 下载视频
    getVideoDict(cookies_Q, cookies_T, cookies_sid)
