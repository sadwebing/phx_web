#!/usr/bin/env python
#-_- coding:utf-8 -_-
#Author: Arno
#Introduction:
#    调用网宿API，刷新网宿域名静态文件缓存
#version: 1.0 20180509 实现基本功能
#         1.1 20180513 只清理http协议缓存

import requests, sys, os
import datetime, hmac, base64, json
from hashlib import sha256
#from urllib  import request,parse

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

rewrite_list = ['301', '302', '303']

#获取当前脚本路径
basedir = os.path.abspath(os.path.dirname(__file__))

#telegram 参数
tg_api  = 'bot422793714:AAE8A-sLU1Usms2bJxiKWc3tUWaWYP98bSU'  # @AuraAlertBot api
tg_url  = 'https://api.telegram.org/bot%s/sendMessage' %tg_api
message = {} # 信息主体
message['chat_id'] = '-275535278'  # '-204952096': arno_test | '-275535278': chk_ng alert
message['text']    = ""

#网宿API 参数
username = 'speedfeng'
apikey   = 'speedfeng@123'

#获取当前时间，以特定的格式，如Wed, 09 May 2018 12:51:25 GMT
def getDate():
    return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

#获取加密后的apikey
def signApikey(date, apikey):
    signed_apikey = hmac.new(apikey.encode('utf-8'), date.encode('utf-8'), sha256).digest()
    signed_apikey = base64.b64encode(signed_apikey)
    return signed_apikey

#telegram 通知
def sendTelegram(text, caption='', doc=False):
    if doc:
        with open('domain.txt', 'w') as f:
            for line in text.split('\n'):
                f.writelines(line+'\r\n')
        files = {'document': open('domain.txt', 'rb')}
        message['caption'] = caption
        try:
            ret = requests.post(tg_url.replace('sendMessage', 'sendDocument'), data=message, files=files, timeout=15)
        except:
            print ('Attention: send message failed!')

    else:
        message['text'] = text
        try:
            ret = requests.post(tg_url, data=message, timeout=15)
        except:
            print ('Attention: send message failed!')

#获取有效的网宿域名
def getWsdomains(username, apikey):
    date    = getDate()
    headers = {'Date': date, 'Accept': 'application/json'}
    url     = 'https://open.chinanetcenter.com/api/domain'
    signed_apikey = signApikey(date, apikey)
    warning = "\r\n".join([ 
                'Attention: 获取网宿域名失败，请检查:'
                '网宿URL:  + %s' %url,
                'headers:  + %s' %headers,
                '%s : %s' %(username, signed_apikey)
              ])
    try:
        ret = requests.get(url, headers=headers, auth=(username, signed_apikey))

    except Exception as e:
        text = warning + '\nException: ' + e.message
        print (text)
        sendTelegram(text)
        return False

    else:
        if ret.status_code != 200:
            text = warning + '\n' + str(ret.content)
            print (text)
            sendTelegram(text)
            return False

        else:
            #return [ line['domain-name'] for line in ret.json() if line['enabled'] == 'true']
            return [ line for line in ret.json() if line['enabled'] == 'true']

#清理网宿域名缓存
def purgeWsdomains(domains, uri='/'):
    date    = getDate()
    headers = {'Date': date, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    url     = 'http://open.chinanetcenter.com/ccm/purge/ItemIdReceiver'
    signed_apikey = signApikey(date, apikey) #获取加密的签名
    warning = "\r\n".join([ 
                'Attention: 网宿域名缓存清理失败，请检查:'
                '网宿URL:  + %s' %url,
                'headers:  + %s' %headers,
                '%s : %s' %(username, signed_apikey)
              ])

    #判断是目录刷新还是文件刷新
    if uri == '/' or uri[-1] == '/':
        type_f = 'dirs' #目录刷新
    else:
        type_f = 'urls' #文件刷新

    data    = {type_f: []} #需要刷新的域名或者文件链接

    #格式化域名或者文件链接   
    for domain in domains:
        data[type_f].append('http://%s%s' %(domain['domain-name'], uri))
        #if domain['service-type'] == 'web-https':
        #    data[type_f].append('https://%s%s' %(domain['domain-name'], uri))

    try:
        ret = requests.post(url, headers=headers, auth=(username, signed_apikey), data=json.dumps(data), timeout=30)

    except Exception as e:
        text = warning + '\nException: ' + e.message
        print (text)
        sendTelegram(text)
        return data[type_f], False

    else:
        if ret.json()['Message'] != 'handle success':
            text = warning + '\n' + str(ret.content)
            print (text)
            sendTelegram(text)
            return data[type_f], False

        else:
            return data[type_f], True
            #return data[type_f], str(ret.status_code) + ' : ' + ret.content


if __name__ == '__main__':
    #判断传入的uri
    if len(sys.argv) > 1:
        if sys.argv[1][0] != '/':
            print ('uri 错误，请重新输入！')
            sys.exit()
        uri = sys.argv[1]
    else:
        uri = '/'

    #获取网宿域名
    domains = getWsdomains(username, apikey)
    if not domains: sys.exit()

    #开始清缓存
    while len(domains) != 0 :
        domains_c = domains[:50]
        domains   = domains[50:]
        urls, result = purgeWsdomains(domains_c, uri=uri)
        text = '\n'.join(urls)
        if result:
            caption = '网宿域名缓存刷新成功！'
        else:
            caption = '网宿域名缓存刷新失败！'
        sendTelegram(text, caption, doc=True)

    #print (str(len(domains)) + ' : ' + ' '.join([domain['domain-name'] for domain in domains]))
