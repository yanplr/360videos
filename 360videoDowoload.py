from selenium import webdriver
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
from PIL import Image
# from paddleocr import PaddleOCR


CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
SERVER = 'on'
PHONE = os.environ['PHONE']
PW = os.environ['PW']
SCKEY = os.environ['SCKEY']


dkStart = datetime.datetime.now()

def captcha(driver, ocr):
    screenshot = './screenshot.png'
    driver.save_screenshot(screenshot)
    img = Image.open(screenshot)
    img = img.convert("RGB")
    # cropped = img.crop((1190, 1010, 1400, 1080)) ## mac的参数
    cropped = img.crop((899, 503, 1004, 543))

    cropped.save('./captcha.png')
    time.sleep(1)

    ## 进行ocr
    # res = 'null'
    # result = ocr.ocr('./captcha.png', cls=True)
    # for line in result:
    #     res = line[1][0].lower()
    #     print(f'验证码可能是 {res}')
    
    ## 输入captcha
    # driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[2]/div[2]/div[1]/div/div[2]/form/p[3]/span/input').send_keys(res)
    # time.sleep(1)
    # driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[2]/div[2]/div[1]/div/div[2]/form/p[5]/input').click()
    # time.sleep(3)

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

## 重新加载一遍，以获得cookie里的值
def getcookies():
    ### /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir='/Users/yanplr/Library/Application\ Support/Google/Chrome'
#     os.system('/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
#     options.add_experimental_option("detach", True)
    options.set_capability("detach", True)
    ## 部署到github action时删除debugger_address
#     options.debugger_address = '127.0.0.1:9222'
    d = DesiredCapabilities.CHROME
    d['goog:loggingPrefs'] = {'performance':'ALL'}
    s = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=s, options=options, desired_capabilities=d)
    driver.delete_all_cookies()

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

    flag = True
    tryTime = 0
    # ocr = PaddleOCR(use_angle_cls=True, lang="en") 
    ocr = ''
    while(flag and tryTime < 3):
        try:
            user_name = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/a[1]')
            print(f'用户名：{user_name.text}')
            print(f'登录成功')
            flag = False
        except:
            tryTime += 1
            print(f'尝试输入验证码：第{str(tryTime)}次')
            captcha(driver, ocr)

    # ## 重新get
    # driver.get(loginUrl)
    # indexCookieList = driver.get_cookies()
    # print(type(indexCookieList[0]))
    # print(indexCookieList)

    # for cookie in indexCookieList:
    #     # print(cookie)
    #     # for key, value in cookie.items():
    #     if cookie['name'] == 'jia_web_sid':
    #         cookies_sid = cookie['value']
    #     if cookie['name'] == 'Q':
    #         cookies_Q = cookie['value']
    #     if cookie['name'] == 'T':
    #         cookies_T= cookie['value']
    
    # print(f'cookies_Q = {cookies_Q}')
    # print(f'cookies_T = {cookies_T}')
    # print(f'cookies_sid = {cookies_sid}')
    # return cookies_Q, cookies_T, cookies_sid
   

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
    # cookies_Q, cookies_T, cookies_sid = getcookies()
    getcookies()
    
    ## 下载视频
    # getVideoDict(cookies_Q, cookies_T, cookies_sid)
