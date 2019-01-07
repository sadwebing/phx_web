# coding: utf8
from phxweb.customer   import DefConsumer
from phxweb            import settings
from phxweb.svn_api    import SvnApi
from phxweb.upgrade.comp_files        import get_svn_lock_files, is_file_in_list
from phxweb.upgrade.update_svn_record import updateSvnRecord
from saltstack.saltapi import SaltAPI
from monitor.models    import project_t, minion_t, minion_ip_t, svn_master_t
from upgrade.models    import svn_customer_t
from upgrade.models    import svn_gray_lock_t
from saltstack.command import Command
from accounts.limit    import LimitAccess
from accounts.views    import getIp, getProjects
from accounts.models   import user_project_authority_t
from detect.telegram   import sendTelegram
from detect.models     import department_user_t

import json, logging, time, urlparse, requests

logger = logging.getLogger('django')

#telegram 参数
message = settings.message_TEST

class UpgradeExecute(DefConsumer):
    # Set to True to automatically port users from HTTP cookies
    # (you don't need channel_session_user, this implies it)
    http_user = True
    channel_session_user = True

    # Set to True if you want it, else leave it out
    strict_ordering = False

    def receive(self, text=None, bytes=None, **kwargs):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        #self.close()

        self.clientip = '127.0.0.1'
        self.username = self.message.user.username
        try:
            self.role = self.message.user.userprofile.role
        except:
            self.role = 'none'

        data = json.loads(self.message['text'])
        step = 0

        ### step one ###
        info = {}
        info['step'] = 'one'
        self.message.reply_channel.send({'text': json.dumps(info)})

        ### final step ###
        info = {}
        info['step'] = 'final'
        info['results'] = {}
        svn_customer_dict = {}
        info['results'][data['minion_id']] = ""

        #给升级的产品上锁
        project = project_t.objects.get(id=data['id'])

        if project.svn_mst_lock == 1:
            info['results'][data['minion_id']] = "此环境的升级已被锁，请等待其他人升级完成，或者请联系管理员！"
            self.message.reply_channel.send({'text': json.dumps(info)})
            self.close()
            return False
        else:
            project.svn_mst_lock = 1
            project.save()

        #获取需要同步的文件
        svn_files = []
        svn_files_all = []
        for svn_record in data['svn_records']:
            changelist = svn_record['changelist']
            if not isinstance(changelist, list):
                for i in changelist[1:-1].split('], ['):
                    svn_files.append([i.split('\'')[1], i.split('\'')[3]])
                    svn_files_all.append([i.split('\'')[1], i.split('\'')[3]])
            else:
                svn_files += changelist
                svn_files_all += changelist

        #给升级到灰度的svn 文件上锁以及解锁
        if len(data['codeEnv']) == 1 and data['codeEnv'][0] == 'gray_env':
            for svn_record in data['svn_records']:
                sr = svn_gray_lock_t(
                    revision   = svn_record['revision'],
                    author     = svn_record['author'],
                    date       = svn_record['date'],
                    log        = svn_record['log'],
                    changelist = svn_record['changelist'],
                )
                try:
                    sr.save()
                except Exception as e:
                    logger.error("svn 记录锁已存在：%s" %svn_record)
                    sr = svn_gray_lock_t.objects.get(revision=svn_record['revision'])
                else:
                    logger.info("svn 记录锁：%s" %svn_record)

                try:
                    svn_master = svn_master_t.objects.get(id=data['svn_master_id'])
                    svn_master.svn_gray_lock.add(sr)
                except Exception as e:
                    message['text'] = "@arno\r\nsvn 记录锁 存入svn master 失败：%s\r\n%s" %(svn_record, str(e))
                    info['results'][data['minion_id']] = "svn 记录锁 存入svn master 失败：%s\r\n%s" %(svn_record, str(e))
                    logger.error(message['text'])
                    sendTelegram(message).send()
                    project.svn_mst_lock = 0
                    project.save()
                    self.message.reply_channel.send({'text': json.dumps(info)})
                    self.close()
                    return False

            #info['results'][data['minion_id']] = "svn 记录锁 存入svn master 成功：%s" %svn_record
        
        elif len(data['codeEnv']) == 1 and data['codeEnv'][0] == 'online_env':
            #判断是否存在文件冲突
            islock = False
            status, svn_lock_files = get_svn_lock_files(data['svn_master_id'], data['svn_records'])
            logger.info(svn_lock_files)
            for fileT in svn_files:
                if is_file_in_list(fileT[1], svn_lock_files):
                    islock = True
                    logger.info(fileT[1])
                    info['results'][data['minion_id']] += str(fileT)
            if islock:
                info['results'][data['minion_id']] = "文件锁存在，无法将灰度升级到运营：\r\n%s" %info['results'][data['minion_id']]
                logger.info(info['results'][data['minion_id']])
                project.svn_mst_lock = 0
                project.save()
                self.message.reply_channel.send({'text': json.dumps(info)})
                self.close()
                return False

            #判断是需要将灰度锁删除
            if int(data['isdeletegraylock'][0]) == 1:
                for svn_record in data['svn_records']:
                    try:
                        sr = svn_gray_lock_t.objects.filter(revision=svn_record['revision']).delete()
                    except Exception as e:
                        info['results'][data['minion_id']] = "svn 记录锁删除失败：%s" %svn_record
                        logger.error(info['results'][data['minion_id']])
                        self.message.reply_channel.send({'text': json.dumps(info)})
                        self.close()
                        return False
                    else:
                        pass
                        #info['results'][data['minion_id']] = "svn 记录锁删除成功：%s" %svn_record
                        #logger.info(info['results'][data['minion_id']])

        elif len(data['codeEnv']) == 2:
            #判断是否存在文件冲突
            islock = False
            status, svn_lock_files = get_svn_lock_files(data['svn_master_id'])
            logger.info(svn_lock_files)
            for fileT in svn_files:
                if is_file_in_list(fileT[1], svn_lock_files):
                    islock = True
                    info['results'][data['minion_id']] += str(fileT)
            if islock:
                info['results'][data['minion_id']] = "文件锁存在，无法直接升级到运营：\r\n%s" %info['results'][data['minion_id']]
                logger.info(info['results'][data['minion_id']])
                project.svn_mst_lock = 0
                project.save()
                self.message.reply_channel.send({'text': json.dumps(info)})
                self.close()
                return False

        else:
            info['results'][data['minion_id']] = "要升级的环境[%s]不存在，请联系管理员！" %data['codeEnv']
            logger.error(info['results'][data['minion_id']])
            project.svn_mst_lock = 0
            project.save()
            self.message.reply_channel.send({'text': json.dumps(info)})
            self.close()
            return False

        #获取需要同步的客户
        svn_customer_l = []
        for svn_customer_name in data['customer']['real']:
            #customer_name = svn_customer_name.split(',')[0]
            #info['results'][data['minion_id']] += name + '\r\n'
            count = 1
            for customer_name in svn_customer_name.split(','):
                customer_name = customer_name.strip()
                try:
                    svn_customer = svn_customer_t.objects.get(name=customer_name)
                except Exception as e:
                    message['text'] = "所选中的客户[%s] 记录不存在，请联系管理员！" %customer_name + '\nException: ' + str(e)
                    logger.error(message['text'])
                    sendTelegram(message).send()
                    info['results'][data['minion_id']] = message['text']
                    project.svn_mst_lock = 0
                    project.save()
                    self.message.reply_channel.send({'text': json.dumps(info)})
                    self.close()
                    return False
                else:
                    if svn_customer.isrsynccode == 0: continue
                    svn_customer_l.append(svn_customer)
                    svn_customer_dict[svn_customer.name] = {
                        'master_ip': [ ip.strip() for ip in svn_customer.master_ip.split('\r\n') if ip.strip() != "" ],
                        'ip': [ ip.strip() for ip in svn_customer.ip.split('\r\n') if ip.strip() != "" ],
                        'port': svn_customer.port,
                        'ismaster': True if svn_customer.ismaster == 1 else False, 
                        'isrsynccode': True if count == 1 else False,
                        'cmd': [cmd.strip() for cmd in svn_customer.cmd.split('\r\n') if cmd.strip() != "" ],
                        'gray_domain':   svn_customer.gray_domain,
                        'online_domain': svn_customer.online_domain,
                        'src_d': svn_customer.src_d,
                        'dst_d': svn_customer.dst_d,
                    }
                    count += 1

        #获取需要通知的部门同事
        atUsers = {}
        for id in data['department']:
            department = department_user_t.objects.get(id=int(id), status=1)
            atUsers[department.name] = {
                'department': department.department,
                'atUsers': department.AtUsers(),
            }

        #调用接口执行代码同步
        while len(svn_files) !=0:
            #svn_files_c = svn_files[:20]
            #svn_files   = svn_files[20:]
            svn_files_c = svn_files_all
            svn_files   = []
            try:
                svn_master = svn_master_t.objects.get(id=data['svn_master_id'])
                api = svn_master.api.strip('/') + '/svn_code'
                logger.info('posting: %s' %api)
                #logger.info('posting: %s' %svn_customer_dict)
                ret = requests.post(api, data=json.dumps({
                    'author': self.username.replace('_', ''),
                    'svn_records': data['svn_records'],
                    'changelist_c': svn_files_c,
                    'changelist': svn_files_all,
                    'code_env': data['codeEnv'],
                    'svn_customer_dict': svn_customer_dict,
                    'atUsers': atUsers,
                }))
            except Exception as e:
                message['text'] = api + '\nException: ' + str(e)
                logger.error(message['text'])
                sendTelegram(message).send()
                info['results'][data['minion_id']] = message['text']
            else:
                info['results'][data['minion_id']] += ret.content
            
            break

        #更新svn记录
        for svn_record in data['svn_records']:
            if len(data['codeEnv']) == 1 and data['codeEnv'][0] == 'gray_env':
                updateSvnRecord(revision=svn_record['revision'], svn_gray_l=svn_customer_l)
            elif len(data['codeEnv']) == 1 and data['codeEnv'][0] == 'online_env':
                updateSvnRecord(revision=svn_record['revision'], svn_online_l=svn_customer_l)
            elif len(data['codeEnv']) == 2:
                updateSvnRecord(revision=svn_record['revision'], svn_gray_l=svn_customer_l, svn_online_l=svn_customer_l)

        #给升级的产品解锁
        project.svn_mst_lock = 0
        project.save()

        self.message.reply_channel.send({'text': json.dumps(info)})
        self.close()