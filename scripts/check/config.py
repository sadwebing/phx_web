#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    一些依赖函数
#version: 2018/12/30  一些依赖函数

import os, sys, datetime, logging, multiprocessing, requests, json, pytz, urlparse, threading, platform, commands, re, time
import dnsr.resolver, redis, logging

reload(sys)
sys.setdefaultencoding('utf8')

#当前脚本路径
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
predir  = os.path.dirname(basedir) #上层目录

#日志文件设定
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%d/%b/%Y:%H:%M:%S',
                filename='%s/logs/access.log' %basedir,
                filemode='a')

#将上层目录加入环境变量，用于引用其他模块
sys.path.append(os.path.abspath(os.path.join(predir, os.pardir)))

#设置django环境
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'phxweb.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phxweb.settings")
django.setup() #启动django

from detect.telegram import sendTelegram
from monitor.models  import project_t, minion_t, minion_ip_t
from detect.models   import domains
from dns.cf_api      import CfApi
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

#其他
yunwei = "@arno, @trevor"

#redis配置
redis_cfg = {
    'host': "localhost",
    'port': 6379,
    'password': "phexus1314ct",
}

#自动切换域名线路配置
failed_retry   = 2 #单次循环检测次数
failed_timeout = 5 #域名检测超时时间
failed_all     = 2 #失败达到一定次数后进行解析切换
mdns_interval  = 300 #5分钟内不重复切换域名解析
reck_interval  = 120 #2分钟后再对已切换解析的域名进行检测

if __name__ == '__main__':
    print "no more."