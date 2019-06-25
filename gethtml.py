# -*- coding: utf-8 -*-
import requests
import time
import random

import logging
from getconfig import getConfig
if getConfig('output', 'log') == 'True':
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.ERROR)

req = requests.session()
def getHeads():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    return random.choice(user_agent_list)


#headers = {'User-Agent': getConfig("headers", "User-Agent")}
headers = {'User-Agent': getHeads()}




def GetNewIpProxy():
    global proxy
    ipStrArray = str(requests.get("http://127.0.0.1:5010/get/").content).split('\'')
    proxy = {"http": "http://{}".format(ipStrArray[1])}
    logging.info(proxy)

def randsleep():
    time.sleep(random.randint(1, 2))
    return 1

def Req_get(url):
    retry = 5
    logging.info(url)
    while retry != 0:
        try:
            html = req.get(url, headers=headers, proxies=proxy, timeout=30).text
            randsleep()
            if '</html>' not in html.lower():
                retry -= 1
                continue
            return html
        except:
            logging.warning('请求url: {0} 时 出现异常, 正在重试.'.format(url))
            retry -= 1
    #sys.exit(999)
    logging.warning('请求url失败!')
    return None


def Req_post(url, data):
    retry = 5
    logging.info(url)
    while retry != 0:
        try:
            html = req.post(url, data=data, headers=headers, proxies=proxy, timeout=30).text
            randsleep()
            if '</html>' not in html.lower():
                retry -= 1
                continue
            return html
        except:
            logging.warning('提交url: {0} 时 出现异常, 正在重试.'.format(url))
            retry -= 1
    #sys.exit(999)
    logging.warning('提交url失败!')
    return None

def Req_get_v2(url):
    retry = 5
    logging.info(url)
    while retry != 0:
        try:
            html = req.get(url, headers=headers, proxies=proxy, timeout=30)
            randsleep()
            # if '</html>' not in html.lower():
            #     retry -= 1
            #     continue
            logging.info('status_code = ' + str(html.status_code))
            if html.status_code != 200:
                retry -= 1
                continue
            return html
        except requests.exceptions.ConnectionError:
            logging.warning('请求url: {0} 时 ConnectionError出现异常, 正在重试.'.format(url))
            retry -= 1
        except requests.exceptions.ChunkedEncodingError:
            logging.warning('请求url: {0} 时 ChunkedEncodingError 出现异常, 正在重试.'.format(url))
            retry -= 1
    #sys.exit(999)
    logging.warning('请求url失败!')
    return None