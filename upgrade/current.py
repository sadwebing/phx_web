# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http      import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from accounts.views   import HasPermission, HasServerPermission, getIp, getProjects, timeNow
from monitor.models   import project_t, svn_master_t
from detect.models    import department_user_t
from upgrade.models   import svn_gray_lock_t, svn_customer_t, svn_record_t
from phxweb.svn_api   import SvnApi

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf   import csrf_exempt, csrf_protect

import json, logging, requests, datetime
logger = logging.getLogger('django')

@csrf_exempt
def CurrentQuery(request):
    if request.method == 'GET':
        return HttpResponse('You get nothing!')
    elif request.method == 'POST':
        clientip = getIp(request)
        username = request.user.username
        try:
            role = request.user.userprofile.role
        except:
            role = 'none'
        #if not username:
        #    logger.info('user: 用户名未知 | [POST]%s is requesting. %s' %(clientip, request.get_full_path()))
        #    return HttpResponseServerError("用户名未知！")

        logger.info('[POST]%s is requesting. %s' %(clientip, request.get_full_path()))

        record_list = []
        svn_records = svn_record_t.objects.all()
        for record in svn_records:
            tmpdict = {
                'id':         record.id,
                'revision':   record.revision,
                'author':     record.author,
                'date':       record.date,
                'log':        record.log,
                'changelist': record.changelist,
                'svn_gray':   [ customer.name for customer in record.svn_gray.all() ],
                'svn_online': [ customer.name for customer in record.svn_online.all() ],
                'mod_date':   record.mod_date.strftime('%Y/%m/%d %H:%M:%S'),
            }
            record_list.append(tmpdict)
        return HttpResponse(json.dumps(record_list))
    else:
        return HttpResponse('nothing!')

@csrf_exempt
def CurrentAdd(request):
    if request.method == 'GET':
        return HttpResponse('You get nothing!')
    elif request.method == 'POST':
        clientip = getIp(request)
        username = request.user.username
        try:
            role = request.user.userprofile.role
        except:
            role = 'none'
        #if not username:
        #    logger.info('user: 用户名未知 | [POST]%s is requesting. %s' %(clientip, request.get_full_path()))
        #    return HttpResponseServerError("用户名未知！")

        logger.info('[POST]%s is requesting. %s' %(clientip, request.get_full_path()))

        try:
            data = json.loads(request.body)
            for record in data['records']:
                sr = svn_record_t(
                    revision   = record['revision'],
                    author     = record['author'],
                    date       = record['date'],
                    log        = record['log'],
                    changelist = record['changelist'],
                    mod_date   = timeNow().now(),
                )
                sr.save()
        except Exception as e:
            error = 'failed: %s' %str(e)
            logger.error(error)
            return HttpResponseServerError(error)
        else:
            logger.info("insert svn record: %s. success!" %record['revision'])
            return HttpResponse('success.')
    else:
        return HttpResponse('nothing!')