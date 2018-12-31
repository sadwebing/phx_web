#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    redis
#version: 2018/12/30  redis

import os, sys, requests
import dnsr.resolver, redis

reload(sys)
sys.setdefaultencoding('utf8')

#当前脚本路径
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
predir  = os.path.dirname(basedir) #上层目录

#将上层目录加入环境变量，用于引用其他模块
sys.path.append(os.path.abspath(os.path.join(predir, os.pardir)))

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from check.config    import message, sendTelegram, yunwei, logging
from check.dependent import getIp

#redis连接池
class connRedis(object):
    def __init__(self, host='localhost', port=6379, password=None):
        if password:
            self.pool = redis.ConnectionPool(host=host, port=port, password=password, decode_responses=True)
        else:
            self.pool = redis.ConnectionPool(host=host, port=port, decode_responses=True)
        
    def rdp(self):
        return redis.Redis(connection_pool=self.pool)

    def test(self):
        try:
            self.rdp().get('test')
        except Exception as e:
            message['text'] = "".join([
                    "%s\r\n" %getIp().str(),
                    "管理: %s\r\n" %yunwei,
                    "连接本地redis失败: %s\r\n" %str(e),
                    "请及时修复，域名自动切换脚本已暂停！",
                ])
            sendTelegram(message).send()
            sys.exit()

if __name__ == '__main__':
    print "no more."