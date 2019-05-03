#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    一些依赖函数
#version: 2018/12/30  一些依赖函数

import os, sys, datetime, logging, multiprocessing, requests, json, pytz, urlparse, threading, platform, commands, re, time
import dnsr.resolver, redis

reload(sys)
sys.setdefaultencoding('utf8')

#当前脚本路径
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
predir  = os.path.dirname(basedir) #上层目录

#将上层目录加入环境变量，用于引用其他模块
sys.path.append(os.path.abspath(os.path.join(predir, os.pardir)))

from check.config import message, sendTelegram, logging

from bs4        import BeautifulSoup
from time       import sleep
#from color_print import ColorP
from socket     import gethostname, gethostbyname
#from subprocess import getoutput

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#状态定义
error_status  = u'失败'
normal_status = [200, 404, 403]

#获取当前时间
class timeNow(object):
    def __init__(self):
        self.current_time = datetime.datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai'))

    def now(self):
        return datetime.datetime.now()

    def stamp(self):
        return self.current_time
    
    def format(self, form='%Y/%m/%d %H:%M:%S'):
        return self.current_time.strftime(form)

#获取域名解析
def getDomainDns(domain):
    results = {'cname': '', 'a':[]}

    try:
        ret = dnsr.resolver.query(domain, 'CNAME').response.answer[0].items[0].__str__()
    except dnsr.resolver.NoAnswer:
        try:
            ret = dnsr.resolver.query(domain, 'A').response.answer
        except dnsr.resolver.NoAnswer:
            print 'Get a for %s failed!' %domain
            return 'Get a for %s failed!' %domain
        else:
            for answer in ret:
                for record in answer:
                    results['a'].append(record.__str__())
            return str(results['a'])
    except Exception as e:
        print 'Get dns for %s failed!' %domain
        return 'Get dns for %s failed: %s' %(domain, str(e))
    else:
        results['cname'] = ret
        print 'Get cname for %s: %s' %(domain, results['cname'])
        return results['cname']

#获取html的title
def getHtmlTitle(html):
    html = BeautifulSoup(html,'html.parser')
    try:
        return html.title.text
    except:
        return None

def sendAlert(ip, results):
    if results:
        message['text'] = ip + results
        sendTelegram(message).send()

def isIP(str):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(str):
        return True
    else:
        return False

class getIp(object):
    def __init__(self):
        if platform.system() == "Linux":
            self.__str = commands.getoutput('curl -s https://ip.cn')
        try:
            ret = requests.get('http://myip.ipip.net')
        except Exception as e:
            print u'获取当前IP失败......'
            print str(e)
            self.__str = gethostname()
        else:
            if ret.status_code == 200:
                self.__str = ret.text
            else:
                self.__str = gethostname()

    def str(self):
        return self.__str

    def ip(self):
        self.__ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', self.__str)
        if self.__ip:
            return self.__ip[0]
        else:
            return '127.0.0.1'

if __name__ == '__main__':
    print "no more."