import os, time, datetime, json, requests

DD_TOKEN = os.environ['DD_TOKEN']

SERVER = 'on'
dkStart = datetime.datetime.now()


def sendMsg(m, error=''):
    if SERVER == 'on':
        timeNow = time.strftime('%Y-%m-%d', time.localtime())
        duration = datetime.datetime.now() - dkStart
        dingDingUrl = 'https://oapi.dingtalk.com/robot/send?access_token=' + DD_TOKEN
        print(dingDingUrl)
        if error == '':
            msg = 'yanplr:{} {}! 耗时{}秒。'.format(timeNow, m, duration.seconds)
            data_info = {
                "msgtype": "text",
                "text": {
                "content": msg
                },
                "isAtAll": False
            }
        else:
            msg = 'yanplr:{} {}!'.format(timeNow, error)
            data_info = {
                "msgtype": "text",
                "text": {
                "content": msg
                },
                "isAtAll": False
            }
        # url = 'https://sctapi.ftqq.com/{}.send?title={}&desp={}'.format(SCKEY, msg, '{}\n{}'.format(msg, error))
        # requests.get(url)

        ## 钉钉发送的信息
        HEADERS = {"Content-Type": "application/json;charset=utf-8"}
        value = json.dumps(data_info)
        response = requests.post(dingDingUrl,data=value,headers=HEADERS)
        if response.json()['errmsg']!='ok':
            print(response.text)

if __name__ == '__main__':
    msg = '成功同步100条360视频'
    sendMsg(msg)

