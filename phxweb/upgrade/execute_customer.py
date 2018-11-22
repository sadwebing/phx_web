# coding: utf8
from phxweb.customer   import DefConsumer
from phxweb            import settings
from saltstack.saltapi import SaltAPI
from monitor.models    import project_t, minion_t, minion_ip_t
from saltstack.command import Command
from accounts.limit    import LimitAccess
from accounts.views    import getIp, getProjects
from accounts.models   import user_project_authority_t

import json, logging, time, urlparse

logger = logging.getLogger('django')

#telegram 参数
message = settings.message_ONLINE

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

        mount = 1
        for cmd in data['cmd']:
            logger.info(cmd)
            commandexe = Command(data['minion_id'], 'cmd.run', cmd, expr_form='glob')
            result = commandexe.CmdRun()
            for key in result:
                info['results'][key+'-'+str(mount)] = result[key]
                mount += 1
            logger.info(info['results'])

        #给升级的产品解锁
        project.svn_mst_lock = 0
        project.save()

        self.message.reply_channel.send({'text': json.dumps(info)})
        self.close()