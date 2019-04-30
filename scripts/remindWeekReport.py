#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    发送telegram 信息，提醒交周报
#version: 2019/04/30  实现基本功能

import os, sys, datetime, logging, multiprocessing, requests, json, urlparse, threading, platform, commands

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
from detect.models   import department_user_t
from phxweb          import settings

from check.dependent import timeNow

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#telegram 参数
message = settings.message_TEST
message['group'] = "arno_test2"

#状态定义
error_status  = u'失败'
normal_status = [200, 404, 403]

#当前脚本路径
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))


if __name__ == '__main__':
    department = department_user_t.objects.filter(name="yunwei").first()
    department2 = department_user_t.objects.filter(name="lianfayunwei").first()
    if not department: sys.exit(1)
    
    name = [ "@"+user.user for user in department.user.all()]
    name2 = [ "@"+user.user for user in department2.user.all()]

    message['text'] = "\r\n".join([
        "周报提醒 - %s" %timeNow().format(),
        "%s: %s" %(department.department, ", ".join(name + name2)),
        "负责人: @arno", 
    ])

    message['group'] = "yunwei"
    sendTelegram(message).send()
