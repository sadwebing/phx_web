#!/usr/bin/env python
#-_- coding:utf-8 -_-
#author: Arno
#introduciton:
#    域名故障，自动切换线路，并实时预警
#version: 2018/12/26  实现基本功能
#         2018/12/30  增添一系列限制参数
#         2018/12/31  增添IP判断，发送信息到不同的群组

import os, sys, datetime, multiprocessing, requests, json, pytz, urlparse, threading, platform, commands, re, time
import dnsr.resolver, redis
from check.dependent  import getIp, timeNow, getDomainDns, getHtmlTitle
from check.redis_api  import connRedis
from check.config     import yunwei, redis_cfg, failed_retry, failed_all, failed_timeout, mdns_interval, reck_interval
from check.config     import logging, groupIp
from check.modify_dns import modifyDns

reload(sys)
sys.setdefaultencoding('utf8')

#当前脚本路径
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

#将上层目录加入环境变量，用于引用其他模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

#引用django中的模块和变量
from check.config import sendTelegram, message
from check.config import project_t, minion_t, minion_ip_t
from check.config import domains
from check.config import settings

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

#获取域名
def getDomains():
    '''
        获取需要监控的域名列表
    '''
    domain_list  = []
    domain_l = domains.objects.filter(auto_m_dns=1).all() #获取所有有效的域名
    #domain_l = domains.objects.filter(status=1, auto_m_dns=1).all() #获取所有有效的域名
    for domain in domain_l:
        tmp_dict = {
            'id':         domain.id,
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
            'mod_date':   domain.mod_date.replace(tzinfo=pytz.timezone('Asia/Shanghai')),
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
        self.__timeout  = failed_timeout
        self.__retry    = failed_retry
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
            res.append({error_status: u'连接超时！'})
        except requests.exceptions.ReadTimeout:
            res.append({error_status: u'加载超时！'})
        except requests.exceptions.SSLError:
            res.append({error_status: u'证书认证错误！'})
        #except requests.exceptions.NewConnectionError:
        #    res.append({error_status: u'找不到主机名！'})
        except requests.exceptions.MissingSchema:
            res.append({error_status: u'协议头无效！'})
        except requests.exceptions.ConnectionError:
            res.append({error_status: u'连接错误！'})
        except Exception as e:
            res.append({error_status: str(e)})
        else:
            if len(ret.history) != 0:
                for r in ret.history:
                    res.append({r.status_code: r.url})
            res.append({ret.status_code: ret.url})
            res.append({'title': getHtmlTitle(ret.content)})
        return res

#并发执行
class myThread(threading.Thread):
    def __init__(self, domain):
        threading.Thread.__init__(self)
        self.domain = domain

    def run(self):
        #获取当前时间与上一次修改解析的时间差
        now = timeNow().stamp()
        interval = (now - self.domain['mod_date']).seconds - 360

        rd = ReqDomains(self.domain)
        self.__product  = rd.__dict__['_ReqDomains__product']
        self.__customer = rd.__dict__['_ReqDomains__customer']
        self.__name     = rd.__dict__['_ReqDomains__name']
        self.t  = None
        
        #连接redis，获取域名的失败次数
        rdp = connRe.rdp()
        faildr = rdp.get(self.__name)
        val = int(faildr) if faildr else faildr

        #判断域名是否需要进行检测
        if val and val >= failed_all and interval < reck_interval:
            return False

        for i in range(rd.__dict__['_ReqDomains__retry']):
            if not rd.IsNameVaild() or not rd.IsIpVaild():
                #print (self.domain)
                continue

        if not rd.IsNameVaild():
            error = '域名无效.'
            self.t = ": ".join([self.__product + "_" +self.__customer, rd.__dict__['_ReqDomains__url'], error])
            print (self.t)
        elif not rd.IsIpVaild():
            error = '域名解析无效.'
            self.t = ": ".join([self.__product + "_" +self.__customer, rd.__dict__['_ReqDomains__url'], error])
            print (self.t)
        else:
            for i in range(rd.__dict__['_ReqDomains__retry']):
                res = rd.ExeReq()
                print ": ".join([self.__product + "_" +self.__customer, rd.__dict__['_ReqDomains__url'], str(res)])
                #print ('.', end='')
                if error_status not in res[0].keys() and 200 in res[-2].keys():
                    break
                sleep(1)
            if error_status in res[0].keys():
                error = str(res[0][error_status])
                self.t = ": ".join([self.__product + "_" +self.__customer, rd.__dict__['_ReqDomains__url'], error])
            elif 200 not in res[-2].keys():
                error = str(res)
                self.t = ": ".join([self.__product + "_" +self.__customer, rd.__dict__['_ReqDomains__url'], error])
            else:
                if val and val >= failed_all and interval >= reck_interval:
                    #logging.info(val)
                    message['text'] = "%s: 域名已经恢复。" %self.__name
                    logging.info(message['text'] + "失败次数: %d" %val)
                    sendTelegram(message).send()
                rdp.set(self.__name, 0)

        failed = 0
        if self.t and interval >= mdns_interval:
            if isinstance(val, int): failed += int(val) + 1
            rdp.set(self.__name, failed)   #更新检测失败次数

            mdns = modifyDns(self.__name, self.domain)
            current_route = [mdns.GetDomainRoute()['result']['type'], mdns.GetDomainRoute()['result']['content'], str(mdns.GetDomainRoute()['result']['proxied'])] if mdns.GetDomainRoute() else "获取失败"

            print "开始发送telegram预警：\r\n%s" % self.t
            #message['group'] = "domain_autoMdns"
            #message['group'] = "arno_test2"
            try:
                message['text'] = "".join([
                        "%s\r\n" %ip_str,
                        "时间: %s\r\n" %timeNow().format(),
                        "管理: %s\r\n" %yunwei,
                        "产品: %s\r\n" %self.__product,
                        "客户: %s\r\n" %self.__customer,
                        "当前域名: %s\r\n" %self.__name,
                        "当前线路: %s\r\n" %" - ".join(current_route),
                        "当前解析: %s\r\n" %getDomainDns(self.__name),
                        "检测失败: %d 次\r\n" %failed,
                        "NG解析: %s\r\n" %self.domain['ng_content'] if self.domain['ng_content'] else "",
                        "CF解析: %s\r\n" %self.domain['cf_content'] if self.domain['cf_content'] else "",
                        "ws解析: %s\r\n" %self.domain['ws_content'] if self.domain['ws_content'] else "",
                        "错误信息: %s" %str(error),
                    ])
                sendTelegram(message).send()
            except Exception as e:
                print "发送telegram 信息失败！"
                print str(e)

            if failed >= failed_all :
                #rdp.set(self.__name, 0)   #更新检测失败次数
                #修改域名的解析
                result, mdre = mdns.Modify()

                #修改域名在数据库中的状态
                dm = domains.objects.get(id=self.domain['id'])
                dm.mod_date = timeNow().now()
                dm.save()

                #发送处理状态
                if not result:
                    message['text'] = '%s: 解析修改失败！' %self.__name
                else:
                    message['text'] = '%s: %s\r\n解析修改成功。' %(self.__name, mdre)
                sendTelegram(message).send()

    def get_result(self):
        if self.t:
            return self.t
        else:
            return None

if __name__ == '__main__':
    #获取当前服务器IP
    getip  = getIp()
    ip_str = getip.str()
    ip     = getip.ip()

    #获取 telegram 群组
    #message['group'] = "domain_autoMdns"
    message['group'] = groupIp(ip)

    #连接redis
    connRe = connRedis(password=redis_cfg['password'])
    connRe.test()

    li = []
    results = ""

    for domain in getDomains():
        t = myThread(domain)
        li.append(t)
        t.start()
    #for t in li:
    #    t.join()
    #    if t.get_result(): results += t.get_result()

    #sendAlert(ip_str, results)