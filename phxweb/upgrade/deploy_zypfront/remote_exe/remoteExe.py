#!/usr/bin/python3
#-_- coding: utf-8 -_-

from flask      import Flask, request, render_template, abort, send_file, Response, Blueprint
from dependent  import sendTelegram, sendAlert, timeNow, purge, is_file_in_list, message
from config     import logging
from remote_exe.sshCon import sshCon

import json, os, subprocess, time, threading

remote_exe = Blueprint('remote_exe', __name__)

def get_t_result(li):
    ret_text = ""
    for t in li:
        isbreak = False
        t.join()
        #if t.get_result(): ret_text += t.get_result() + '\r\n'
        count = 0
        #logging.info(t.get_result())
        while t.get_result() == None:
            #logging.info(t.get_result())
            count += 1
            logging.info(t.cmd + ": 执行失败，重新执行。")
            #logging.info(t.ip)
            #logging.info(t.cmd + ": 执行失败，重新执行。")
            t.run()
            if t.get_result() != None:
                ret_text += t.info + " " + '重复推送 %d次 成功！\r\n' %count
                isbreak = True
                break
            if count == 2: break
        if t.get_result() == None:
            logging.info(t.info + " " + ': 执行失败！\r\n')
            ret_text += t.info + " " + ': 执行失败！\r\n'
        else:
            if not isbreak:
                ret_text += t.info + t.get_result() + " " + '\r\n'
    return ret_text

#多线程执行同步
class myThread(threading.Thread):
    def __init__(self, ip, port, cmd, sc=None, info=""):
        super().__init__()
        self.cmd  = cmd
        self.ip   = ip
        self.sc   = sc
        self.port = port
        self.info = info
        self.result = None
        
    def run(self):
        if not self.sc:
            self.sc = sshCon(self.ip)

        #self.result = subprocess.getoutput(self.cmd)

        self.result = self.sc.ExeCmd(self.cmd)
        #logging.info("1:" + str(self.result))
        #count = 0
        #while self.result != 0:
        #    count += 1
        #    logging.info(t.cmd + ": 执行失败，重新执行。")
        #    self.result = os.system(self.cmd)
        #    if count == 2: break

    def get_result(self):
        if self.result != None:
            return self.result
            #return self.cmd + '\n' +self.result
            #print (self.cmd + '\n' +self.result)
        else:
            return None

@remote_exe.route('/execute', methods=['POST'])
def remoteExecute():
    if request.method == 'POST':
        ret_text = ""
        try:
            data = json.loads(request.get_data().decode("utf-8"))
        except Exception as e:
            ret_text += "参数转换成json失败，请检查！%s" %request.get_data()
            logging.error(ret_text)
            return Response(ret_text, status=500)

        remote_addr = request.remote_addr

        logging.info('%s is requesting: %s' %(remote_addr, request.url))
        #logging.info(str(data))

        log = "\r\n"
        customers = ", ".join(data['svn_customer_dict'].keys())

        #if user_l: log += "@" + ",".join(list(set(user_l)))

        for customer in data['customers']:
            ret_text += customer + '\r\n'
            info = data['svn_customer_dict'][customer]
            li = []

            cmd = ""
            if info['ismaster']:
                if len(info['master_ip']) == 0:
                    ret_text += "%s 没有配置主控IP，请检查！" %customer
                    logging.error(ret_text)
                    return Response(ret_text, status=500)
                else:
                    master_ip = info['master_ip'][0]

                sc = sshCon(master_ip, port=info['port'])

                for ip in info['ip']:
                    if ip == "127.0.0.1":
                        cmd_l = [
                            'rm -rf /tmp/{ip}.sh',
                            " && ".join([ 'echo """%s""" >> /tmp/{ip}.sh' %line.replace('"', '\\"').replace("'", "\\'") for line in data['script'] ]),
                            'sh /tmp/{ip}.sh',
                        ]
                    else:
                        cmd_l = [
                            'ssh {ip} rm -rf /tmp/{ip}.sh',
                            " && ".join([ 'ssh {ip} \'echo """%s""" >> /tmp/{ip}.sh\'' %line.replace('"', '\\"').replace("'", "\\'") for line in data['script'] ]),
                            'ssh {ip} "sh /tmp/{ip}.sh"',
                        ]
                    cmd=" && ".join(cmd_l).format(ip=ip, script=data['script'])
                    logging.info(cmd)
                    cnn = master_ip + ": " + ip + "\n"
                    #ret_text += cnn + str(sc.ExeCmd(cmd))

                    t = myThread(ip, 22, cmd, sc, info=cnn)
                    li.append(t)
                    t.start()
            else:
                for ip in info['ip']:
                    if ip == "127.0.0.1":
                        continue
                    #sc = sshCon(ip)

                    cmd_l = [
                        'rm -rf /tmp/{ip}.sh',
                        " && ".join([ 'echo """%s""" >> /tmp/{ip}.sh' %line.replace('"', '\\"').replace("'", "\\'") for line in data['script'] ]),
                        'sh /tmp/{ip}.sh',
                    ]
                    cmd = " && ".join(cmd_l).format(ip=ip, script=data['script'])
                    logging.info(cmd)
                    cnn = ip + "\n"
                    #ret_text += cnn + str(sc.ExeCmd(cmd))
                    t = myThread(ip, 22, cmd, info=cnn)
                    li.append(t)
                    t.start()

            ret_text += get_t_result(li)

        #logging.info(ret_text)
        #time.sleep(0.5)
        return Response(str(ret_text), status=200)

    elif request.method == 'HEAD':
        return ('null')




if __name__ == '__main__':
    print ("No more.")