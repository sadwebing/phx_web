#-_- coding:utf-8 -_-

import threading, requests, json, subprocess, datetime, time, pytz, sys, os, logging
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from req_ws_api import getWsdomains, purgeWsdomains, username, apikey

#日志设置
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%d/%b/%Y:%H:%M:%S',
                filename='logs/access.log',
                filemode='a')

#获取当前脚本路径
basedir = os.path.abspath(os.path.dirname(__file__))

#静态文件后缀
file_ext = ['jpg', 'png', 'css', 'js', 'gif', 'flv', 'ico', 'swf', 'html', 'jepg', 'rar', 'zip', 'pdf', 'mp3', 'mp4', 'eot', 'otf', 'fon', 'font', 'ttf', 'ttc', 'woff', 'woff2']

#telegram 参数
message = {} # 信息主体
message['doc']        = False
message['bot']        = "sa_monitor_bot" #AuraAlertBot: 大魔王 | sa_monitor_bot: 鬼来电
message['text']       = ""
message['group']      = "kindergarten"  #'kindergarten'
message['parse_mode'] = "HTML"
message['doc_name']   = "message.txt"

def timeNow():
    current_time = datetime.datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y/%m/%d %H:%M:%S')
    return current_time

#telegram 通知
def sendTelegram(message):
    #telegram 通知
    try:
        ret = requests.post('http://sa.l510881.com/detect/send_telegram', data=json.dumps(message))
    except Exception as e:
        print (str(e))

#调用接口清理腾讯云缓存
def purgeTencent(data):
    #telegram 通知
    try:
        ret = requests.post('http://sa.l510881.com/saltstack/reflesh/purge', data=json.dumps(data))
    except Exception as e:
        print (str(e))

#判断字符串是否在列表中
def is_file_in_list(fileT, listT):
    for re in listT:
        if fileT == re:
            return True
    else:
        return False

#灰度升级的锁机制
class grayLock(object):
    '''
        给灰度升级加一个锁机制，如果当前有代码升级在灰度，下次升级只能升级灰度，或者将灰度升级到运营
    '''

    def __init__(self):
        self.lockfile = '%s/grayLock.txt' %basedir
        if not os.path.exists(self.lockfile):
            with open(self.lockfile, 'w') as f:
                f.writelines('1')

    def getLock(self):
        with open(self.lockfile, 'r') as f:
            lock = f.readlines()[0].replace('\n', '')
        if lock == '1':
            return True
        else:
            return False
    
    def updateLock(self, setLock):
        if setLock:
            value = '1'
        else:
            value = '0'
        with open(self.lockfile, 'w') as f:
            f.writelines(value)

def get_t_result(li):
    ret_text = ""
    for t in li:
        isbreak = False
        t.join()
        #if t.get_result(): ret_text += t.get_result() + '\r\n'
        count = 0
        while t.get_result() != 0:
            count += 1
            logging.info(t.cmd + ": 执行失败，重新执行。")
            t.run()
            if t.get_result() == 0:
                ret_text += t.ip + " " + str(t.fileT) + '重复推送 %d次 成功！\r\n' %count
                isbreak = True
                break
            if count == 2: break
        if t.get_result() != 0:
            logging.info(t.ip + " " + str(t.fileT) + ': 同步失败！\r\n')
            ret_text += t.ip + " " + str(t.fileT) + ': 同步失败！\r\n'
        else:
            if not isbreak:
                ret_text += t.ip + " " + str(t.fileT) + '\r\n'
    return ret_text

#多线程执行同步
class myThread(threading.Thread):
    def __init__(self, cmd, fileT='', ip=''):
        super().__init__()
        self.cmd = cmd
        self.ip  = ip
        self.fileT  = fileT
        self.result = None
        
    def run(self):
        #self.result = subprocess.getoutput(self.cmd)
        self.result = os.system(self.cmd)
        #count = 0
        #while self.result != 0:
        #    count += 1
        #    logging.info(t.cmd + ": 执行失败，重新执行。")
        #    self.result = os.system(self.cmd)
        #    if count == 2: break

    def get_result(self):
        #with open('%s/timeout.log' %basedir, 'a') as f:
        #    f.writelines(timeNow()+' '+self.cmd+'\n')
        #print self.cmd
        if self.result != None:
            return self.result
            #return self.cmd + '\n' +self.result
            #print (self.cmd + '\n' +self.result)
        else:
            return None

def TheadAlive(li):
    isStuck = False
    try:
        for t in li:
            if t.is_alive():
                t.get_result()
                isStuck = True
    except Exception as e:
        isStuck = True
        print (str(e))
    return isStuck

def purge(message, changelist):
    #获取需要清缓存的文件
    file_m = ''
    files  = []
    for change in changelist:
        if change[0] == 'M' and change[1].split('/')[-1].split('.')[-1] in file_ext:
            files.append(change[1])
            file_m += change[1] + '\n'

    #替换uri
    error = ""
    uri_l = []
    for uri in files:
        if 'client_x' in uri or 'api/tpl' in uri or 'server_x_new' in uri:
            uri_l.append(uri.replace('/client_x', '').replace('/api/tpl', '').replace('/server_x_new', ''))
        else:
            error += uri + '\r\n'
    if error:
        message['text'] = "@arno @%s 未知的文件路径: \r\n%s" %(author, error)
        sendTelegram(message)

    #清理腾讯云缓存
    #if len(uri_l) > 0:
    #    purgeTencent({
    #        'cdn_proj': [1],
    #        "uri": uri_l,
    #    })
    #else:
    #    return True

    #判断是否有需要清缓存的文件
    if len(uri_l) == 0:
        return True

    #获取网宿域名
    domains = getWsdomains(username, apikey)
    if not domains: return False

    #开始自动清网宿缓存
    if len(uri_l) > 10:
        #message['doc']      = True
        #message['text']     = file_m
        #message['caption']  = '@%s 请注意刷新缓存！' %author
        #message['doc_name'] = 'files_need_to_refresh.txt'
        message['doc'] = True
        while len(domains) != 0 :
            domains_c = domains[:100]
            domains   = domains[100:]
            urls, result = purgeWsdomains(domains_c)
            message['text'] = '\n'.join(urls)
            if result:
                message['caption'] = '网宿域名缓存刷新成功！'
            else:
                message['caption'] = '网宿域名缓存刷新失败！'
            sendTelegram(message)
    elif len(uri_l) > 0 and len(uri_l) <= 10:
        while len(domains) != 0 :
            domains_c = domains[:100]
            domains   = domains[100:]
            text_T    = text_F = ""

            for uri in uri_l:
                urls, result = purgeWsdomains(domains_c, uri=uri)

                if result:
                    text_T += '\n'.join(urls) + '\n'
                else:
                    text_F += '\n'.join(urls) + '\n'

            if text_T:
                message['caption'] = '网宿域名缓存刷新成功！'
                message['text']    = text_T
                message['doc']     = True
                sendTelegram(message)
            if text_F:
                message['caption'] = '网宿域名缓存刷新失败！'
                message['text']    = text_F
                message['doc']     = True
                sendTelegram(message)
    return True

def sendAlert(message, env, log, author, date, atUsers={}, user_l=[], customers="", isrsyncOnline=False, domains="", attention=""):
    '''
        发送升级通知
    '''

    #人员分组
    test = atUsers['ceshi']['atUsers'] if "ceshi" in atUsers.keys() else ""

    department_l = ""
    for department in atUsers.keys():
        d_info = atUsers[department]
        department_l = department_l + d_info['department']+": "+d_info['atUsers'] +"\r\n"
        #department_l.append(d_info['department']+": "+d_info['atUsers'])

    #判断环境
    noimg  = u"\u2716"
    yesimg = u"\u2714"
    if env == "gray":
        messageRound = 1
        grayStatus   = yesimg
        if isrsyncOnline:
            onlineStatus = yesimg
        else:
            onlineStatus = noimg
    elif env == "online":
        messageRound = 0
        grayStatus   = yesimg
        onlineStatus = yesimg
    elif env == "rollback":
        messageRound = 0
        grayStatus   = "已回退"
        onlineStatus = "已回退"
    else:
        messageRound = 0
        grayStatus   = noimg
        onlineStatus = noimg

    #获取需要@ 的工程师
    user_d = ""
    if user_l: user_d = "工程师: " + ", ".join(["@"+user for user in user_l]) + '\r\n'
    #if log and '@' in log:
    #    user_l = log.lower().replace(' ', '').split('@')[-1].split(',')
    #    log    = ''.join(log.split('@')[:-1])
    #    if user_l: user_d = "工程师: " + ", ".join(["@"+user for user in user_l]) + '\r\n'

    #初始化telegram主体信息
    message['text'] = "".join([
                        "升级人: @%s\r\n" %author,
                        "版本库: 专业盘彩票后端代码\r\n",
                        "时间 : %s\r\n" %date,
                        "信息 : %s\r\n" %log,
                        "灰度环境: %s\r\n" %grayStatus,
                        "运营环境: %s\r\n" %onlineStatus,
                        ])

    AtUser = "".join([
                        "升级客户: %s\r\n" %customers,
                        "%s" %department_l,
                        #"管理组: %s\r\n" %manage,
                        #"运维组: %s\r\n" %sa,
                        #"测试组: %s\r\n" %test,
                        #"客服组: %s\r\n" %service,
                        "%s" %user_d,
                        ])

    if author not in ['']:
        message['doc'] = False
        #if author == 'arno':
        #    message['group'] = 'arno_test'
        #message['group'] = 'arno_test'
        for i in range(messageRound):
            sendTelegram(message)
        else:
            message['text'] += AtUser
            sendTelegram(message)

    if not isrsyncOnline:
        message['doc']      = True
        message['text']     = domains
        message['doc_name'] = "domains.txt"
        message['caption']  = "测试组: %s\r\n必测功能: 登陆，注册，下注，充值，转账，提款等\r\n请参考附件域名进行测试\r\n%s" %(test, attention) if test else "请参考附件域名进行测试"
        sendTelegram(message)

if __name__ == '__main__':
    print ("no no no")
