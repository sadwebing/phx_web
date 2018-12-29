#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    域名故障，自动切换线路，并实时预警
#version: 2018/12/26  实现基本功能

import os, sys, datetime, logging, multiprocessing, requests, json, urlparse, threading, platform, commands, re

#reload(sys)
#sys.setdefaultencoding('utf8')

#将上层目录加入环境变量，用于引用其他模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

#设置django环境
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'phxweb.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phxweb.settings")
django.setup() #启动django

from detect.telegram import sendTelegram
from monitor.models  import project_t, minion_t, minion_ip_t
from detect.models   import domains
from phxweb          import settings

from bs4        import BeautifulSoup
from time       import sleep
#from color_print import ColorP
from socket     import gethostname, gethostbyname
#from subprocess import getoutput

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#telegram 参数
message = settings.message_TEST

#状态定义
error_status  = u'失败'
normal_status = [200, 404, 403]

#当前脚本路径
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

#获取html的title
def getHtmlTitle(html):
    html = BeautifulSoup(html,'html.parser')
    try:
        return html.title.text
    except:
        return None

def getDomains():
    '''
        获取需要监控的域名列表
    '''
    domain_list  = []
    domain_l = domains.objects.filter(auto_m_dns=1).all() #获取所有有效的域名
    #domain_l = domains.objects.filter(status=1, auto_m_dns=1).all() #获取所有有效的域名
    for domain in domain_l:
        tmp_dict = {
            'name':       domain.name,
            'product':    (domain.product, domain.get_product_display()),
            'customer':   (domain.customer, domain.get_customer_display()),
            'client':     domain.group.client,
            'method':     domain.group.method,
            'ssl':        domain.group.ssl,
            'retry':      domain.group.retry,
            'cf':         domain.cf,
            'cf_content': domain.cf_content,
            'ws_content': domain.ws_content,
            'ng_content': domain.ng_content,
            'mod_date':   domain.mod_date,
        }

        domain_list.append(tmp_dict)

    return domain_list

#执行检测域名请求
class ReqDomains(object):
    def __init__(self, domain):
        self.__url      = ''
        self.__name     = ''
        self.__product  = ''
        self.__customer = ''
        self.__method   = 'head'
        self.__verify   = False
        self.__timeout  = 5
        self.__retry    = 1
        self.__reg      = '^.*[a-zA-Z0-9]+.*\.[a-zA-Z0-9]*[a-zA-Z]+[a-zA-Z0-9]*$'
        self.__headers  = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0', 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
        if isinstance(domain, dict):
            if ('client' in domain.keys()) and domain['client'] == 'wap': self.__headers = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1', 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}
            if 'method' in domain.keys(): self.__method = domain['method']
            #if ('ssl' in domain.keys()) and domain['ssl'] != 1: self.__verify = False
            if 'timeout' in domain.keys(): self.__timeout = domain['timeout']
            if 'product' in domain.keys(): self.__product = domain['product'][1]
            if 'customer' in domain.keys(): self.__customer = domain['customer'][1]
            if 'name' in domain.keys() and len(domain['name'].split('/')) >= 3: 
                self.__name = domain['name'].split('/')[2].split(':')[0].strip()
                #print (self.__name)
                self.__url  = domain['name'].strip()
        elif isinstance(domain, str) and len(domain.split('/')) >= 3: 
            self.__name = domain.split('/')[2].split(':')[0].strip()
            self.__url  = domain.strip()

        #获取域名解析地址
        try:
            self.__ip = gethostbyname(self.__name)
            #print (self.__ip)
        except:
            self.__ip = None

    def IsNameVaild(self):
        '''判断域名是否有效'''
        #return True if re.fullmatch(self.__reg, self.__name) else False
        return True if re.search(self.__reg, self.__name) else False

    def IsIpVaild(self):
        '''获取域名解析地址'''
        return True if self.__ip else False

    def ExeReq(self):
        '''执行域名检测'''
        res = []
        s   = requests.Session()
        req = requests.Request(
                method  = self.__method.strip(), 
                url     = self.__url.strip(), 
                headers = self.__headers
            ).prepare()
        try:
            ret = s.send(req, verify=self.__verify, timeout=self.__timeout)
        except requests.exceptions.ConnectTimeout:
            res.append({error_status: {self.__ip:'连接超时！'}})
        except requests.exceptions.ReadTimeout:
            res.append({error_status: {self.__ip:'加载超时！'}})
        except requests.exceptions.SSLError:
            res.append({error_status: {self.__ip:'证书认证错误！'}})
        #except requests.exceptions.NewConnectionError:
        #    res.append({error_status: {self.__ip:'找不到主机名！'}})
        except requests.exceptions.MissingSchema:
            res.append({error_status: {self.__ip:'协议头无效！'}})
        except requests.exceptions.ConnectionError:
            res.append({error_status: {self.__ip:'连接错误！'}})
        except Exception as e:
            res.append({error_status: {self.__ip:e}})
        else:
            if len(ret.history) != 0:
                for r in ret.history:
                    res.append({r.status_code: r.url})
            res.append({ret.status_code: ret.url})
            res.append({'title': getHtmlTitle(ret.content)})
        return res

class myThread(threading.Thread):
    def __init__(self, domain):
        threading.Thread.__init__(self)
        self.domain = domain

    def run(self):
        rd = ReqDomains(self.domain)
        self.__product  = rd.__dict__['_ReqDomains__product']
        self.__customer = rd.__dict__['_ReqDomains__customer']
        self.t  = None
        
        for i in range(rd.__dict__['_ReqDomains__retry']):
            if not rd.IsNameVaild() or not rd.IsIpVaild():
                #print (self.domain)
                continue

        if not rd.IsNameVaild():
            self.t = ": ".join([self.__product + "_" +self.__customer, rd.__dict__['_ReqDomains__url'], '域名无效.'])
            print (self.t)
        elif not rd.IsIpVaild():
            self.t = ": ".join([self.__product + "_" +self.__customer, rd.__dict__['_ReqDomains__url'], '域名解析无效.'])
            print (self.t)
        else:
            for i in range(rd.__dict__['_ReqDomains__retry']):
                res = rd.ExeReq()
                print (self.__product + "_" +self.__customer, rd.__dict__['_ReqDomains__url'], str(res))
                #print ('.', end='')
                if error_status not in res[0].keys() and 200 in res[-2].keys():
                    break
                sleep(2)
            if error_status in res[0].keys():
                self.t = ": ".join([self.__product + "_" +self.__customer, rd.__dict__['_ReqDomains__url'], str(res[0][error_status])])
            elif 200 not in res[-2].keys():
                self.t = ": ".join([self.__product + "_" +self.__customer, rd.__dict__['_ReqDomains__url'], str(res)])

        if self.t:
            print "开始发送telegram预警：\r\n%s" % self.t
            message['text'] = "".join([
                    "管理人：@arno\r\n",
                    "产品：%s" self.__product,
                    "客户：%s" self.__customer,
                    "当前域名：%s" self.domain,
                    "当前线路：%s" self.domain,
                    self.t,
                ])
            sendTelegram(message).send()

    def get_result(self):
        if self.t:
            return self.t
        else:
            return None

def sendAlert(ip, results):
    if results:
        message['text'] = ip + results
        sendTelegram(message).send()

def getIp():
    try:
        ret = requests.get('http://myip.ipip.net')
    except Exception as e:
        print u'获取当前IP失败......'
        print str(e)
        ip = gethostname()
    else:
        if ret.status_code == 200:
            ip = ret.text
        else:
            ip = gethostname()
    return ip

if __name__ == '__main__':
    #if platform.system() == "Linux":
    #    ip = commands.getoutput('curl -s https://ip.cn')
    #else:
    #    ip = getIp()

    ip = ""

    li = []
    results = ""

    for domain in getDomains():
        t = myThread(domain)
        li.append(t)
        t.start()
    #for t in li:
    #    t.join()
    #    if t.get_result(): results += t.get_result()

    #sendAlert(ip, results)