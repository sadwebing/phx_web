#!/usr/bin/env python
#-_- coding: utf-8 -_-
#author: arno
#introduction:
#    svn api

from detect.telegram import sendTelegram
from phxweb          import settings
from tzlocal         import get_localzone
import requests, json, svn.local, svn.remote, logging
logger = logging.getLogger('django')

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#telegram 参数
message = settings.message_TEST

class SvnApi(object):
    def __init__(self, url, user, password):
        '''
            初始化接口参数，默认获取的数据格式为json
        '''
        self.__url  = url.rstrip('/')
        self.__user = user
        self.__password = password
        self.conn = svn.remote.RemoteClient(self.__url)
        self.conn._CommonClient__username = self.__user
        self.conn._CommonClient__password = self.__password

    def GetLog(self, limit=1):
        '''
            获取svn 提交日志
        '''
        logger.info("需要获取的日志是 %d 条" %limit)
        log_list = []
        try:
            info = self.conn.log_default(limit=limit, changelist=True)
            #logger.info(info)
        except Exception as e:
            message['text']  = '@arno\r\n%s: 获取svn信息失败！\r\n%s' %(self.__url, str(e))
            #logger.error(message['text'])
            sendTelegram(message).send()
        else:
            for i in range(limit):
                try:
                    t = info.next()
                except Exception as e:
                    continue
                if not t: break
                tmpdict = {
                    'revision': t.revision,
                    'author': t.author,
                    'date': t.date.astimezone(get_localzone()).strftime('%Y/%m/%d %H:%M:%S'),
                    'log': t.msg,
                    'changelist': t.changelist,
                }
                log_list.append(tmpdict)
        return log_list

        
