#!/usr/bin/env python
#-_- coding:utf-8 -_-
#Author: Arno
#Introduction:
#    调用aws API
#version: 1.0 20190603 实现基本功能

import requests, sys, commands, os, logging
import datetime, hmac, base64, json
import boto3
from hashlib import sha256
from phxweb  import settings
from detect.telegram import sendTelegram
#from urllib  import request,parse

logger = logging.getLogger('django')

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

rewrite_list = ['301', '302', '303']

#telegram 参数
message = settings.message_TEST

#获取当前脚本路径
basedir = os.path.abspath(os.path.dirname(__file__))

#获取当前时间，以特定的格式，如Wed, 09 May 2018 12:51:25 GMT
def getDate():
    return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

class awsApi(object):
    def __init__(self, username, apikey):
        self.__username = username
        self.__apikey   = apikey
        self.__resource = 'cloudfront'
        self.__product  = ['fenghuang']

    def createCli(self, resource=''):
        '''
            建立aws 客户端，默认请求 aws cdn云资源，即 cloudfront
        '''
        resource = self.__resource
        client = boto3.client(
                resource,
                aws_access_key_id     = self.__username,
                aws_secret_access_key = self.__apikey
            )
        return client

    def sendTelegramAlert(self, content=""):
        message['text'] = content
        logger.error(message['text'])
        sendTelegram(message).send()

    def getdomains(self, product=[]):
        '''
            通过aws 特有的标签，识别所需要的配置
        '''
        product = self.__product

        # 建立aws 客户端
        client = self.createCli() 

        # 警告信息
        self.__warning = "\r\n".join([ 
                    'Attention: aws域名获取失败，请检查:',
                    'aws账号:  + %s' %self.__username,
                ])
        
        # 获取分发内容的列表
        try:
            ret = client.list_distributions()

        except Exception as e:
            content = self.__warning + '\r\n' + str(e).replace('<', '&lt;').replace('>', '&gt;')[:2047]
            sendTelegramAlert(content)
            return [], False
        
        # 对域名进行筛选
        try:
            if ret['ResponseMetadata']['HTTPStatusCode'] != 200 or 'DistributionList' not in ret.keys():
                content = self.__warning + '\r\n' + str(ret).replace('<', '&lt;').replace('>', '&gt;')[:2047]
                sendTelegramAlert(content)
                return [], False

        except Exception as e:
            message['text'] = self.__warning + '\r\n' + str(e).replace('<', '&lt;').replace('>', '&gt;')[:2047]
            logger.error(message['text'])
            sendTelegram(message).send()
            return [], False

        else:
            tmplist = []
            for item in ret['DistributionList']['Items']:
                li = item['Comment'].replace(' ', '').split('-') # 获取注释，并拆分为列表
                if len(li) < 2: continue
                if li[0] in product: # 如果产品在所新人的列表中，则录入
                    tmpdict = {
                            'item':     item,
                            'Id':       item['Id'],
                            'domains':  item['Aliases']['Items'],
                            'product':  li[0],
                            'customer': li[1],
                        }
                    tmplist.append(tmpdict)
            logger.info("%s: aws 账号 cdn云域名获取成功。" %self.__username)
            return tmplist, True

    def purge(self, Id, uri=['/']):
        '''
            每个云资源实例，都有一个特定的ARN，通过ARN 清理云缓存
            默认清理 ['/']
        '''
        # 建立aws 客户端
        client = self.createCli()

        # 警告信息
        self.__warning = "\r\n".join([ 
                    'Attention: aws域名缓存清理失败，请检查:',
                    'aws账号: %s' %self.__username,
                    '实例Id: %s' %Id,
                ])
        
        # 

        # 清理云缓存
        try:
            ret = client.create_invalidation(
                    DistributionId    = Id,
                    InvalidationBatch = {
                            'Paths': {
                                    'Quantity': len(uri),
                                    'Items': uri
                                },
                            'CallerReference': datetime.datetime.now().strftime('%Y%m%d%H%M%S') # 生成随机时间
                        }
                )

        except Exception as e:
            content = self.__warning + '\r\n' + str(e).replace('<', '&lt;').replace('>', '&gt;')[:2047]
            sendTelegramAlert(content)
            return {}, False

        else:
            if ret['ResponseMetadata']['HTTPStatusCode'] != 201:
                content = self.__warning + '\r\n' + str(ret).replace('<', '&lt;').replace('>', '&gt;')[:2047]
            return ret, True

if __name__ == '__main__':
    print "网宿"
