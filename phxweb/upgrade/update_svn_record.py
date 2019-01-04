# coding: utf8
from phxweb            import settings
from monitor.models    import project_t, minion_t, minion_ip_t, svn_master_t
from upgrade.models    import svn_customer_t, svn_gray_lock_t, svn_record_t
from detect.telegram   import sendTelegram
from accounts.views    import timeNow

import json, logging, time, urlparse, requests

logger = logging.getLogger('django')

#telegram 参数
message = settings.message_TEST

def updateSvnRecord(revision, svn_gray_l=[], svn_online_l=[]):
    try:
        svn_record = svn_record_t.objects.get(revision=revision)
    except Exception as e:
        logger.error("svn record %d not exist: %s" %(revision, str(e)))
        return False
    
    try:
        for svn_customer in svn_gray_l:
            svn_record.svn_gray.add(svn_customer)
        for svn_customer in svn_online_l:
            svn_record.svn_online.add(svn_customer)
        svn_record.mod_date = timeNow().now()
        svn_record.save()

    except Exception as e:
        logger.error("svn record %d update failed: %s" %(revision, str(e)))
        return False
    
    else:
        return True
