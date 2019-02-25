#!/usr/bin/env python3
#-_- coding:utf-8 -_-
#Author: Arno

import requests, sys, os, datetime, json
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from dependent  import sendTelegram, myThread

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#获取当前脚本路径
basedir = os.path.abspath(os.path.dirname(__file__))

li=[]
ret_text=""
for i in range(2):
    cmd = 'ip a'
    t = myThread(cmd)
    li.append(t)
    t.start()

for t in li:
    t.join()
    if t.get_result(): ret_text += t.get_result()

print (ret_text)
