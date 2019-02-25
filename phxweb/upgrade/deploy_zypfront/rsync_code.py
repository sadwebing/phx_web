#!/usr/bin/env python
#-_- coding:utf-8 -_-
#Author: Arno
#Introduction:
#    同步代码
#version: 1.0 20181018 实现基本功能
#         2.0 20181115 给灰度加锁

import requests, sys, os, datetime, json, svn.local, time
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from hashlib    import sha256
from bs4        import BeautifulSoup
from tzlocal    import get_localzone
from dependent  import myThread

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#获取当前脚本路径
basedir = os.path.abspath(os.path.dirname(__file__))

class rsyncCode(object):
    '''
        同步文件到远程服务器
    '''
    def __init__(self, code_env):
        self.__code_env = code_env
        if len(self.__code_env) == 1 and self.__code_env[0] == 'gray_env':
            self.src_d = '/home/centos/zyp'
            self.dst_d =  ['/home/centos/gray/v1/zyp']

        elif len(self.__code_env) == 1 and self.__code_env[0] == 'online_env':
            self.src_d = '/home/centos/zyp'
            self.dst_d = ['/home/centos/zyp']
        
        elif len(self.__code_env) == 2:
            self.src_d = '/home/centos/zyp'
            self.dst_d = ['/home/centos/gray/v1/zyp', '/home/centos/zyp']

        else:
            result = "代码环境错误，请检查！"
            return False, result

    def exeCmd(self, master_ip, port, ip, fileT, isrsyncwhole=0):
        if isrsyncwhole == 0:
            fileT_dir = '/'.join(fileT[1].split('/')[:-1])
        else:
            fileT_dir = "/"
            fileT     = ""
        cmd_l = []

        if master_ip:
            if not fileT:
                if ip.strip() == '127.0.0.1':
                    #cmd = 'ssh -p {port} {master_ip} "rsync -rptvz {src_d}{fileT} {dst_d}{fileT_dir}"'
                    cmd = 'rsync -rptvz --delete --exclude=.git --exclude=.svn {src_d}{fileT} {dst_d}{fileT_dir}'
                else:
                    cmd = 'rsync -rptvz --delete --exclude=.git --exclude=.svn {src_d}{fileT} {ip}:{dst_d}{fileT_dir}'
                fileR = "/"
            else:
                if fileT[0] == 'M':
                    if ip.strip() == '127.0.0.1':
                        #cmd = 'ssh -p {port} {master_ip} "rsync -rptvz {src_d}{fileT} {dst_d}{fileT_dir}"'
                        cmd = 'rsync -rptvz {src_d}{fileT} {dst_d}{fileT_dir}'
                    else:
                        cmd = 'rsync -rptvz {src_d}{fileT} {ip}:{dst_d}{fileT_dir}'
                elif fileT[0] == 'A':
                    if ip.strip() == '127.0.0.1':
                        cmd = 'rsync -rptvz {src_d}{fileT} {dst_d}{fileT_dir}'
                    else:
                        cmd = 'rsync -rptvz {src_d}{fileT} {ip}:{dst_d}{fileT_dir}'
                elif fileT[0] == 'D':
                    if ip.strip() == '127.0.0.1':
                        cmd = 'rm -rf {dst_d}{fileT}'
                    else:
                        cmd = 'ssh {ip} rm -rf {dst_d}{fileT}'
                fileR = fileT[1]

        else:
            if not fileT:
                if ip.strip() == '127.0.0.1':
                    #cmd = 'ssh -p {port} {master_ip} "rsync -rptvz {src_d}{fileT} {dst_d}{fileT_dir}"'
                    cmd = 'rsync -rptvz --delete --exclude=.git --exclude=.svn  {src_d}{fileT} {dst_d}{fileT_dir}'
                else:
                    cmd = 'rsync -rptvz --delete --exclude=.git --exclude=.svn  {src_d}{fileT} {ip}:{dst_d}{fileT_dir}'
                fileR = "/"
            else:
                if fileT[0] == 'M':
                    if ip.strip() == '127.0.0.1':
                        cmd = 'rsync -rptvz {src_d}{fileT} {dst_d}{fileT_dir}'
                    else:
                        cmd = 'rsync -rptvz {src_d}{fileT} {ip}:{dst_d}{fileT_dir}'
                elif fileT[0] == 'A':
                    if ip.strip() == '127.0.0.1':
                        cmd = 'rsync -rptvz {src_d}{fileT} {dst_d}{fileT_dir}'
                    else:
                        cmd = 'rsync -rptvz {src_d}{fileT} {ip}:{dst_d}{fileT_dir}'
                elif fileT[0] == 'D':
                    if ip.strip() == '127.0.0.1':
                        cmd = 'rm -rf {dst_d}{fileT}'
                    else:
                        cmd = 'ssh {ip} rm -rf {dst_d}{fileT}'
                fileR = fileT[1]

        for dst_d in self.dst_d:
            cmd_l.append(cmd.format(master_ip=master_ip, port=port, src_d=self.src_d, ip=ip, dst_d=dst_d, fileT=fileR, fileT_dir=fileT_dir))

        return cmd_l