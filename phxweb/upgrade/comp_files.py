# coding: utf8
from phxweb.customer   import DefConsumer
from phxweb            import settings
from phxweb.svn_api    import SvnApi
from saltstack.saltapi import SaltAPI
from monitor.models    import project_t, minion_t, minion_ip_t, svn_master_t
from upgrade.models    import svn_customer_t
from upgrade.models    import svn_gray_lock_t
from saltstack.command import Command
from accounts.limit    import LimitAccess
from accounts.views    import getIp, getProjects
from accounts.models   import user_project_authority_t
from detect.telegram   import sendTelegram

import json, logging, time, urlparse, requests

logger = logging.getLogger('django')

#telegram 参数
message = settings.message_TEST

def get_svn_lock_files(svn_master_id, excepts=[], key=None):
    file_list = []
    try:
        svn_master = svn_master_t.objects.get(id=svn_master_id)
    except Exception as e:
        message['text'] = "@arno\r\nsvn master[id%s] 不存在\r\n%s" %(svn_master_id, str(e))
        logger.error(message['text'])
        sendTelegram(message).send()
        return False, file_list
    else:
        if key == "fenghuang_caipiao":
            locks = svn_master.svn_gray_lock.all()
        elif key == "fenghuang_zyp":
            locks = svn_master.svnzyp_gray_lock.all()
        else:
            locks = []

        for svn_record in locks:
            isExcept = False
            for excepti in excepts:
                if svn_record.revision == excepti['revision']:
                    logger.info("排除svn锁: %s" %excepti['revision'])
                    isExcept = True
                    break
            if isExcept: continue
            for change in svn_record.changelist[1:-1].split('], ['):
                file_list.append(change.split('\'')[3])
        return True, file_list

def is_file_in_list(fileT, listT):
    for re in listT:
        if fileT == re:
            return True
    else:
        return False
