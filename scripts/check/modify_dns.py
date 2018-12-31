#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    修改域名dns解析
#version: 2018/12/30  实现基本功能

import os, sys, datetime, logging, multiprocessing, requests, json, pytz, urlparse, threading, platform, commands, re, time

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

from check.config    import domains, settings, CfApi, logging
from check.dependent import timeNow, isIP

class modifyDns(object):
    '''
        用于修改域名DNS解析
    '''
    def __init__(self, domain, info):
        self.__domain = domain
        self.__zone   = '.'.join(self.__domain.split('.')[1:])
        self.__info   = info
        self.cfapi    = CfApi(settings.CF_URL, info['cf'].email, info['cf'].key)

    def GetDomainRoute(self):
        ''' 获取域名的CF解析 '''
        self.__record = self.cfapi.GetDnsRecord(self.__zone, self.__domain)
        #logging.info(dir(self.cfapi))
        if self.__record and self.__record['success']:
            return self.__record
        else:
            return False

    def Modify(self):
        ''' 修改域名的CF解析 '''
        getdr = self.GetDomainRoute()
        logging.info(getdr)
        if not getdr: return False, ""

        if self.__record['result']['proxied']:
            record_type = 'A' if isIP(self.__info['ng_content']) else 'CNAME'
            result = self.cfapi.UpdateZoneRecord(self.cfapi._CfApi__zone_id, record_type, self.__domain, self.__info['ng_content'], False, self.cfapi._CfApi__record_id)
            route  = [record_type, self.__info['ng_content'], 'False']
        else:
            record_type = 'A' if isIP(self.__info['cf_content']) else 'CNAME'
            result = self.cfapi.UpdateZoneRecord(self.cfapi._CfApi__zone_id, record_type, self.__domain, self.__info['cf_content'], True, self.cfapi._CfApi__record_id)
            route  = [record_type, self.__info['cf_content'], 'True']
        if result['success']:
            return True, " - ".join(route)
        else:
            return False, ""

if __name__ == '__main__':
    print "no more."