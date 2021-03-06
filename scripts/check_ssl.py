#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    监控HTTPS域名证书是否到期
#version: 2018/06/12 实现基本功能
#         2018/07/26 域名区分产品和客户, 信息长度大于4096，以文件形式发送信息
#         2018/07/29 域名区分产品和客户, 发送到相应的客户群组
#         2019/04/01 做一些异常处理

import os, sys, datetime, logging,  threading, requests, json, urlparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phxweb.settings")
from phxweb import settings
from ssl import SSLError, CertificateError
import time
import subprocess ## 2019 11 23 新增功能 使每家报警日期不同
reload(sys)
sys.setdefaultencoding('utf8')

#获取当前目录
current_dir = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO, filename="%s/check_ssl.log" %current_dir, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#telegram 参数
message = {} # 信息主体
message['doc']        = False
message['bot']        = "sa_monitor_bot" #AuraAlertBot: 大魔王
message['text']       = ""
message['group']      = 'domain_renew' #domain_renew: 域名续费|证书续费
message['parse_mode'] = "HTML"
message['doc_name']   = 'message.txt'

#django接口
dj_url = 'sa.l510881.com'
#dj_url = '127.0.0.1:5000'

#一个月，半年，一年到期的时间
d_one_y      = datetime.datetime.now() + datetime.timedelta(365)
d_half_y     = datetime.datetime.now() + datetime.timedelta(182)
d_one_m      = datetime.datetime.now() + datetime.timedelta(31)
ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
nor_date_fmt = r'%Y/%m/%d %H:%M:%S'

#telegram 通知
def sendTelegram(message):
    #telegram 通知
    try:
        ret = requests.post('http://%s/detect/send_telegram' %dj_url, data=json.dumps(message))
    except Exception as e:
        print (str(e))

#获取域名
def getDomains(product='all'):
    try:
        ret = requests.post('http://%s/detect/get_domains' %dj_url, headers={'Content-Type': 'application/json'}, data=json.dumps({'product': product}))
    except Exception as e:
        print (str(e))
        return []
    else:
        return ret.json()

class sslExpiry(object):
    def __init__(self, domain):
        '''
            获取https域名证书到期的时间，以及是否是有效证书
        '''
        self.__domain = domain
    
    
class myThread(threading.Thread):
    ##  初始化接口中获取的域名信息 与 域名提取
    def __init__(self,domain_l):
        super(myThread, self).__init__()
        self.__domain_l = domain_l
        self.__domain   = urlparse.urlsplit(domain_l['name']).netloc.split(':')[0].strip()  
    ##  在多线程中 直接 用python3 提取信息 原来的检测模块有问题,信息不准确.
    def get_result(self):
        for n in range(16):
            ##  改动最大的地方 由于未知的原因此主机在运行python脚本进会报线程错误
            ##  所以,加大了python3脚本的outtime 120秒
            ##  反复链接15次  如果15次后仍然不能获取数据,那么默认为链接失败
            ##  threading 模块 + cmd命令行调用,导致脚本运行非常的慢
            if n == 15:
                self.t = (False,self.__domain_l,'证书获取失败')
                break
            else:
                res = subprocess.Popen('/usr/bin/python3 /pythonenv/monitor/phx_web/scripts/check_ssl_p3.py %s'\
                    %self.__domain,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                b = res.stdout.read().split('+')
                a = res.stderr.read()
                if a:
                    time.sleep(0.05)
                    continue
                else:
                    valve = b[0].strip()
                    if valve == 'True':
                        cert = datetime.datetime.strptime(b[1].strip(),'%Y %m %d %H %M %S')
                        self.t = (True,  self.__domain_l, cert)
                    else:
                        cert = b[1].strip()
                        self.t = (False,  self.__domain_l, cert)    
                    break

        return self.t
    
if __name__ == "__main__":
    li = []
    failed    = ""
    ex_half_y = ""
    ex_one_m  = ""
    
    getDomainsDict = getDomains(product='all')

    for domain_l in getDomainsDict['domain']:
        if domain_l['customer'][0] in [14, 15]:  #['大象6668[dx_6668]', '大象70887[dx_70887]']
            continue
        scheme = urlparse.urlsplit(domain_l['name']).scheme

        if scheme == "https":
            t = myThread(domain_l)
            li.append(t)
            t.start()

    ##  特殊时间业主列表,元素来源于settings.py 中的 choices_customer 变量
    ##  ali, guangda ,zyp ,hengxin
    seven_day_list = [1,2,121001,41]                  ## 2019 08 18 新增功能 使每家报警日期不同

    for t in li:
        d_one_m = datetime.datetime.now() + datetime.timedelta(31)
        t.join()
        result = t.get_result()
        valve = result[1]['customer'][0]

        ##  查看业主名,是正在特殊时间列表中
        if valve in seven_day_list:                                      ## 2019 08 18 新增功能 使每家报警日期不同
            ##  如果在列表中,改变默认变量阀值
            d_one_m = datetime.datetime.now() + datetime.timedelta(8)    ## 2019 08 18 新增功能 使每家报警日期不同
        alert = None
        #将结果存入报警列表
        for tmp in getDomainsDict['alert']['others']:
            if result[1]['product'][0] == tmp['product'][0] and result[1]['customer'][0] == tmp['customer'][0]:
                alert = tmp
                break
            else:
                continue
        if not alert:
            alert = getDomainsDict['alert']['default']

        customer = "_"+result[1]['customer'][1] if result[1]['customer'][0] != 29 else ""
        info     = "["+result[1]['product'][1]+customer+"]"+urlparse.urlsplit(result[1]['name']).netloc.split(':')[0].strip()
        if result[0]:
            if d_one_m > result[2]:
                alert['ex_one_m'] += result[2].strftime(nor_date_fmt) + ": " + info + "\r\n"
            elif d_half_y > result[2]:
                alert['ex_half_y'] += result[2].strftime(nor_date_fmt) + ": " + info + "\r\n"
        else:
            alert['failed'] += str(result[2]) + ": " + info + "\r\n"
    getDomainsDict['alert']['others'].append(getDomainsDict['alert']['default'])

    for alert in getDomainsDict['alert']['others']:

        message['text']    = ""
        message['doc']     = False
        message['caption'] = ""

        if alert['failed']:
            message['text'] += u"<pre>证书检测失败的域名: </pre>\r\n" + alert['failed']
        if alert['ex_one_m']:                                             ## 2019 08 18 新增功能 使每家报警日期不同
            message['text'] += u"<pre>一个月内证书到期域名: </pre>\r\n" + alert['ex_one_m'] 

        atUser = u"%s " %" ".join([ "@"+user for user in alert['user'] ]) if len(alert['user']) !=0 else ""
        atUser += u"请注意更换证书！"

        if "证书" in message['text']:

            if len(message['text']) >= 4096:
                message['text']    = message['text'].replace('\r\n', '\n')
                message['doc']     = True
                message['caption'] = u"\r\n" + atUser
            else:
                message['text'] += atUser
        else:
            continue
        for group in alert['chat_group']:
            ##  这是阿若的测试 group ID
##            message['group'] = "arno_test"
            message['group'] = group
            sendTelegram(message)
