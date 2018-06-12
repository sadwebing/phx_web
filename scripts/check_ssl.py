#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    监控HTTPS域名证书是否到期
#version: 2018/06/12 实现基本功能

import os, sys, datetime, logging, ssl, socket, threading, requests, json, urlparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phxweb.settings")
from phxweb import settings
from ssl import SSLError, CertificateError

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

#一个月，半年，一年到期的时间
d_one_y      = datetime.datetime.now()  + datetime.timedelta(365)
d_half_y     = datetime.datetime.now()  + datetime.timedelta(182)
d_one_m      = datetime.datetime.now()  + datetime.timedelta(31)
ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
nor_date_fmt = r'%Y/%m/%d %H:%M:%S'
timeout      = 10

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
    
    def setConn(self, bundle=None):
        '''
            初始化https连接
        '''
    
        if bundle:
            context = ssl.create_default_context(cafile="%s/bundle/%s" %(current_dir, bundle))
        else:
            context = ssl.create_default_context()
        context.verify_mode = ssl.CERT_REQUIRED
        conn    = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=self.__domain,
            #do_handshake_on_connect=False,
        )
        conn.settimeout(timeout)
        return conn
        
    def getCert(self):
        #bundles = os.listdir(u'%s/bundle/' %current_dir).insert(0, None)
        bundles = os.listdir(u'%s/bundle/' %current_dir)
        bundles.insert(0, None)
        index = 0
        ssl   = False
        while not ssl:
            #print index
            conn = self.setConn(bundle=bundles[index])
            try:
                conn.connect((self.__domain, 443))
            except (SSLError, CertificateError):
                index += 1
                if index < len(bundles):
                    continue
                else:
                    logger.error('%s 443 ssl error' %(self.__domain))
                    return SSLError
            except Exception, e:
                logger.error('%s 443 connection error: \n %s' %(self.__domain, e))
                return e
            else:
                ssl = True
                ssl_info = conn.getpeercert()
            #return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
        return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
    
class myThread(threading.Thread):
    def __init__(self,domain):
        super(myThread, self).__init__()
        self.__domain = domain

    def run(self):
        cert = sslExpiry(self.__domain).getCert()
        self.t  = None
        if cert == SSLError:
            self.t = (False, self.__domain, u"证书不合法")
        elif not cert:
            self.t = (False, self.__domain, u"连接失败")
        else:
            self.t = (True,  self.__domain, cert)

    def get_result(self):
        return self.t
    
if __name__ == "__main__":
    #print sslExpiry('alcp33.com').getTime()
    li = []

    choices_prod = ( 
            (0, 'pub'),
            (1, 'ali'), 
            (2, 'guangda'), 
            (3, 'leying'), 
            (4, 'caitou'), 
            (5, 'tiantian'), 
            (6, 'sande'), 
            (7, 'uc'), 
            (8, '9393'), 
            (9, '3535'), 
            (10, 'agcai'), 
            (11, 'wanyou'),
            (12, 'fh'),
            (13, 'le7'),
            (14, 'dx_6668'),
            (15, 'dx_70887'),
            (16, 'ys'),
            )
    
    failed    = ""
    ex_half_y = ""
    ex_one_m  = ""
    
    for domain in getDomains(product='all'):
        domain = urlparse.urlsplit(domain['name']).netloc.split('/')[0]
        if domain:
            t = myThread(domain)
            li.append(t)
            t.start()
        else:
            failed += "域名格式错误: " + domain['name'] + "\r\n"

    for t in li:
        t.join()
        result = t.get_result()
        if result[0] and isinstance(result[2], datetime.datetime):
            if d_one_m > result[2]:
                ex_one_m += result[2].strftime(nor_date_fmt) + ": " + result[1] + "\r\n"
            elif d_half_y > result[2]:
                ex_half_y += result[2].strftime(nor_date_fmt) + ": " + result[1] + "\r\n"
        else:
            failed += str(result[2]) + ": " + result[1] + "\r\n"

    message['group'] = 'arno_test' #domain_renew: 域名续费|证书续费

    if failed:
        message['text'] += u"<pre>检测失败的域名: </pre>\r\n" + failed
    if ex_one_m:
        message['text'] += u"<pre>一个月内证书到期域名: </pre>\r\n" + ex_one_m
    #if ex_half_y:
    #    message['text'] += u"<pre>半年内证书到期域名: </pre>\r\n" + ex_half_y
    if message['text']:
        sendTelegram(message)
    