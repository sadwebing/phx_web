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

class RemoteExecute(DefConsumer):
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

        #获取需要同步的客户
        svn_customer_l = []
        for svn_customer_name in data['customer']['real']:
            #customer_name = svn_customer_name.split(',')[0]
            #info['results'][data['minion_id']] += name + '\r\n'
            count = 1
            for customer_name in svn_customer_name.split(','):
                customer_name = customer_name.strip()

                #if count > 1: continue

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
                    #if svn_customer.isrsynccode == 0: continue
                    svn_customer_l.append(svn_customer)
                    svn_customer_dict[svn_customer.name] = {
                        'master_ip': [ ip.strip() for ip in svn_customer.master_ip.split('\r\n') if ip.strip() != "" ],
                        'ip': [ ip.strip() for ip in svn_customer.ip.split('\r\n') if ip.strip() != "" ] if count == 1 else [],
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

        #调用接口执行代码同步
        numAll = len(svn_customer_dict)
        #logger.info(numAll)
        numExe = 0
        numCon = 1
        customerNameList = svn_customer_dict.keys()

        while numExe < numAll:
            try:
                svn_master = svn_master_t.objects.get(id=data['svn_master_id'])
                api = svn_master.api.strip('/') + '/remote/execute'
                logger.info('posting: %s' %api)

                ret = requests.post(api, data=json.dumps({
                    'author': self.username.replace('_', ''),
                    'svn_customer_dict': svn_customer_dict,
                    'customers': customerNameList[numExe:numExe+numCon],
                    'script': data['script'].split('\n'),
                }))
                logger.info(customerNameList[numExe:numExe+numCon])
                numExe += numCon
            except Exception as e:
                message['text'] = api + '\nException: ' + str(e)
                logger.error(message['text'])
                sendTelegram(message).send()
                info['results'][data['minion_id']] = message['text']
            else:
                info['results'][data['minion_id']] += ret.content

        #给升级的产品解锁
        project.svn_mst_lock = 0
        project.save()

        self.message.reply_channel.send({'text': json.dumps(info)})
        self.close()