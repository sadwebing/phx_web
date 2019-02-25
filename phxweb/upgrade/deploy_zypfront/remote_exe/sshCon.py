#!/usr/bin/python3
#-_- coding: utf-8 -_-

from config import logging

import paramiko

class sshCon(object):
    '''
        创建ssh 连接，执行远程命令
    '''
    def __init__(self, host, port=22, username="root", password=None):
        '''
            获取连接参数，建立ssh连接
        '''
        self.mc = paramiko.SSHClient()
        self.mc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.mc.connect(host, port=port, username=username, password=password)

    def ExeCmd(self, cmd):
        '''
            执行远程命令
        '''
        #logging.info("1: " + cmd)
        if not cmd: return None #命令不存在，不做任何操作

        retcod = None

        try:
            stdin, stdout, stderr = self.mc.exec_command(cmd)
            retcod = stderr.read().decode('utf8')
            if not retcod:
                retcod = stdout.read().decode('utf8')

            logging.info(retcod)
            return retcod

        except Exception as e:
            return str(e)