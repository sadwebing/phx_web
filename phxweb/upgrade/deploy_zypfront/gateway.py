#!/usr/bin/python3
#-_- coding: utf-8 -_-

from dependent  import sendTelegram, myThread, sendAlert, timeNow, purge, is_file_in_list, message, get_t_result
from rsync_code import rsyncCode
from remote_exe.remoteExe import remote_exe

import json, os, subprocess, time

def deploy_svn_code(data):
    ret_text = ""
    try:
        data = json.loads(request.get_data().decode("utf-8"))
    except Exception as e:
        ret_text += "参数转换成json失败，请检查！%s" %request.get_data()
        logger.error(ret_text)

    rc = rsyncCode(data['code_env'])
    log = "\r\n"
    domains = ""
    customers = ", ".join(data['svn_customer_dict'].keys())
    attention = '注意: 测试完成后，请提交运维升级运营环境。\r\n'

    #获取svn 提交的信息
    user_d = ""
    user_l = []
    for svn_record in data['svn_records']:
        if svn_record['log'] and '@' in svn_record['log']:
            user_l += svn_record['log'].lower().replace(' ', '').split('@')[-1].split(',')
            svn_record['log'] = ''.join(svn_record['log'].split('@')[:-1])
        
        if svn_record['author'] == "phexussa":
            author = 'arno'
        else:
            author = svn_record['author']
        log += "%s %s @%s:\r\n%s\r\n" %(svn_record['revision'], svn_record['date'], author, svn_record['log'])

    #if user_l: log += "@" + ",".join(list(set(user_l)))

    for customer in data['svn_customer_dict'].keys():
        ret_text += customer + '\r\n'
        info = data['svn_customer_dict'][customer]
        li = []
        domains += "".join([
                customer+":\n",
                "    灰度环境: %s\n" %info['gray_domain'],
                "    运营环境: %s\n" %info['online_domain'],
            ])

        #同步杀率
        if customer == 'shalv': 
            if 'server_x_new' in str(data['changelist']) and data['changelist'][0] == data['changelist_c'][0]:
                src_d = '/home/centos/caipiao/server_x_new'
                for ip in info['ip']:
                    cmd = 'rsync -rptvz --delete --exclude=.svn /home/centos/caipiao/server_x_new {ip}:/home/centos/html/'.format(ip=ip)
                    #ret_text += cmd + '\r\n'
                    t = myThread(cmd, src_d, ip)
                    li.append(t)
                    t.start()
                ret_text += get_t_result(li)

            continue

        #判断是否需要同步
        if not info['isrsynccode']: continue

        if data['isrsyncwhole'] == 1:
            cmd = ""
            cmd_l = []
            fileT = ""
            if info['ismaster']:
                if len(info['master_ip']) == 0:
                    ret_text += "%s 没有配置主控IP，请检查！" %customer
                    logger.error(ret_text)
                    return Response(ret_text, status=500)
                else:
                    master_ip = info['master_ip'][0]

                for ip in info['ip']:
                    cmd_l += rc.exeCmd(master_ip, info['port'], ip, fileT, isrsyncwhole=data['isrsyncwhole'])
                    #ret_text += cmd + '\r\n'
                cmd = 'ssh -p {port} {master_ip} "{cmd}"'.format(port=info['port'], master_ip=master_ip, cmd=" && ".join(cmd_l))
                logger.info(cmd)
                t = myThread(cmd, fileT, master_ip)
                li.append(t)
                t.start()
            else:
                for ip in info['ip']:
                    cmd = " && ".join(rc.exeCmd(None, info['port'], ip, fileT, isrsyncwhole=data['isrsyncwhole']))
                    logger.info(cmd)
                    ##ret_text += cmd + '\r\n'
                    t = myThread(cmd, fileT, ip)
                    li.append(t)
                    t.start()
            log = "全目录升级"

        for fileT in data['changelist_c']:
            logger.info(str(fileT))
            #ret_text += str(fileT) + '\r\n'
            cmd = ""
            cmd_l = []
            if info['ismaster']:
                if len(info['master_ip']) == 0:
                    ret_text += "%s 没有配置主控IP，请检查！" %customer
                    logger.error(ret_text)
                    return Response(ret_text, status=500)
                else:
                    master_ip = info['master_ip'][0]

                for ip in info['ip']:
                    cmd_l += rc.exeCmd(master_ip, info['port'], ip, fileT)
                    #ret_text += cmd + '\r\n'
                cmd = 'ssh -p {port} {master_ip} "{cmd}"'.format(port=info['port'], master_ip=master_ip, cmd=" && ".join(cmd_l))
                logger.info(cmd)
                t = myThread(cmd, fileT, master_ip)
                li.append(t)
                t.start()
            else:
                for ip in info['ip']:
                    cmd = " && ".join(rc.exeCmd(None, info['port'], ip, fileT))
                    logger.info(cmd)
                    #ret_text += cmd + '\r\n'
                    t = myThread(cmd, fileT, ip)
                    li.append(t)
                    t.start()

        ret_text += get_t_result(li)

    #发送telegram 信息
    if is_file_in_list('online_env', data['code_env']):
        env = 'online'
        isrsyncOnline = True
    else:
        env = 'gray'
        isrsyncOnline = False

    if data['author'] == 'phexussa': #phexussa
        message['group'] = 'arno_test2'
        isrsyncOnline = False
        
    if data['isrsyncwhole'] == 1 or data['changelist'][-1] == data['changelist_c'][-1]:
        sendAlert(message, env, log, data['author'], timeNow(), data['atUsers'], user_l, customers, isrsyncOnline, domains, attention)

        #清理缓存
        #if isrsyncOnline:
        #    try:
        #        result = purge(message, data['changelist'])
        #        if not result:
        #            #logger.info('ceshi: 123456')
        #            ret_text = "清理缓存：获取网宿域名失败！\r\n" + ret_text
        #    except Exception as e:
        #        ret_text = "%s\r\n"%str(e) + ret_text

if __name__ == '__main__':
    print "do no more"