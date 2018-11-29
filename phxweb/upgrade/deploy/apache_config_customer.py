# coding: utf8
from phxweb.customer   import DefConsumer
from phxweb            import settings
from saltstack.saltapi import SaltAPI
from monitor.models    import project_t, minion_t, minion_ip_t, svn_master_t
from upgrade.models    import svn_customer_t
from saltstack.command import Command
from accounts.limit    import LimitAccess
from accounts.views    import getIp, getProjects
from accounts.models   import user_project_authority_t
from detect.telegram   import sendTelegram

import json, logging, time, urlparse, requests

logger = logging.getLogger('django')

#telegram 参数
message = settings.message_TEST

class ApacheConfig(DefConsumer):
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

        count = 1
        for customer_id in data['customer']:
            customer_name = 'none'
            for value in data['item']['svn_customer']['in']:
                if int(customer_id) == value['id']:
                    customer_name = value['name']
                    break
            try:
                svn_customer = svn_customer_t.objects.get(id=customer_id)
            except Exception as e:
                message['text'] = "所选中的客户[%s] 记录不存在，请联系管理员！" %customer_name + '\nException: ' + str(e)
                logger.error(message['text'])
                sendTelegram(message).send()
                info['results'][data['minion_id']+'-'+str(count)] = message['text']
                self.message.reply_channel.send({'text': json.dumps(info)})
                self.close()
                return False
                count += 1
            else:
                svn_customer_dict[svn_customer.name] = {
                    'master_ip': [ ip.strip() for ip in svn_customer.master_ip.split('\r\n') if ip.strip() != "" ],
                    'ip': [ ip.strip() for ip in svn_customer.ip.split('\r\n') if ip.strip() != "" ],
                    'port': svn_customer.port,
                    'ismaster': True if svn_customer.ismaster == 1 else False, 
                    'isrsynccode': True if svn_customer.isrsynccode == 1 else False,
                    'cmd': [cmd.strip() for cmd in svn_customer.cmd.split('\r\n') if cmd.strip() != "" ],
                    'gray_domain':   svn_customer.gray_domain,
                    'online_domain': svn_customer.online_domain,
                    'src_d': svn_customer.src_d,
                    'dst_d': svn_customer.dst_d,
                }

        try:
            svn_master = svn_master_t.objects.get(id=data['svn_master_id'])
            api = svn_master.api.strip('/') + '/apache_config'
            logger.info('posting: %s' %api)
            #logger.info('posting: %s' %svn_customer_dict)
            ret = requests.post(api, data=json.dumps(svn_customer_dict))
        except Exception as e:
            message['text'] = 'Exception: ' + str(e)
            logger.error(message['text'])
            sendTelegram(message).send()
            info['results'][data['minion_id']] = message['text']
        else:
            info['results'][data['minion_id']] = ret.content

        self.message.reply_channel.send({'text': json.dumps(info)})
        self.close()