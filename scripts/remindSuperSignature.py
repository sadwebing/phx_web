#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    发送telegram 信息，提醒各家超级签所剩的名额
#version: 2019/04/30  实现基本功能

import os, sys, datetime, logging, multiprocessing, requests, json, threading, platform

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

# telegram 参数
message = settings.message_TEST
message['group'] = "arno_test2"

# 状态定义
error_status  = u'失败'
normal_status = [200, 404, 403]

# 各家 超级签接口
super_signature = {
    "ali": "https://alisuper.le079.com/apple/getAllAppleAccounts",
    "leying": "https://lysuper.le079.com/apple/getAllAppleAccounts",
    # "guangda": "https://gdsuper.le079.com/apple/getAllAppleAccounts",
    "guangda": "https://gdsmanage.le079.com/apple/getAllAppleAccounts",
    }
remind_account = 100

# 当前脚本路径
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

class SuperSign(object):
    '''
        超级签，通过程序接口，查看一些基本信息
    '''
    def __init__(self, api):
        self.__api = api
        self.__timeout = 5

    def get_data(self):
        try:
            ret = requests.get(self.__api, verify=False, timeout=self.__timeout)
            data = ret.json()['data']
        except Exception as e:
            # raise e
            print (str(e))
            return {'code': 500, 'msg': '数据获取失败: '+str(e), 'data': None}
        else:
            return {'code': 0, 'msg': '数据获取成功', 'data': data}

if __name__ == '__main__':
    # 获取需要 提醒人的纸飞机ID
    department = department_user_t.objects.filter(name="yunwei").first()
    if not department: sys.exit(1)
    name = [ "@"+user.user for user in department.user.all()]
    
    # 获取超级签 接口数据
    for product in super_signature:
        message['text'] = "超级签\r\n业主: " + product + "\r\n"
        rt = SuperSign(super_signature[product]).get_data()
        if rt['code'] != 0: # 如果通过接口获取到的数据不正常，跳出本程序
            print (rt)
            message['text'] += "错误: " + str(rt)
            # continue
            # sys.exit(1)
        else:
            data = rt['data'] # 拿到最终的数据
            
            # 循环数据，筛选得到所剩名额
            remain_all = 0
            for acc in data:
                account = acc['account']
                count = acc['count']
                message['text'] += account + ": " + str(count) + "\r\n"
                remain_all += count

            message['text'] += "\r\n".join([
                "所剩名额总数: %s" %remain_all,
                "%s: %s" %(department.department, ", ".join(name)),
            ])

        message['group'] = "arno_test2"
        # print (message['text'])
        if remain_all <= remind_account:
            message['group'] = "yunwei"
        sendTelegram(message).send()