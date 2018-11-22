# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http      import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from accounts.views   import HasPermission, HasServerPermission, getIp, getProjects
from monitor.models   import project_t

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf   import csrf_exempt, csrf_protect

import json, logging, requests, datetime
logger = logging.getLogger('django')

# Create your views here.
@csrf_protect
@login_required
def Operate(request):
    title = u'升级中心-基本操作'
    clientip = getIp(request)
    username = request.user.username
    try:
        role = request.user.userprofile.role
    except:
        role = 'none'

    if not username:
        logger.info('user: 用户名未知 | [POST]%s is requesting. %s' %(clientip, request.get_full_path()))
        return HttpResponseServerError("用户名未知！")
    
    logger.info('%s is requesting %s' %(clientip, request.get_full_path()))

    projects = getProjects(request, 'execute') #用户必须具有执行权限才能升级

    items = []
    for project in projects:
        if project.svn_mst_alive == 0: continue
        tmpdict = {
            'id':       project.id,
            'envir':    (project.envir, project.get_envir_display()),
            'product':  (project.product, project.get_product_display()),
            'project':  (project.project, project.get_project_display()),
            'customer': (project.customer, project.get_customer_display()),
            'server_type': (project.server_type, project.get_server_type_display()),
            'info':     project.info,
            'svn_master':  {
                'name':       project.svn_master.name,
                'minion_id':  project.svn_master.minion_id.minion_id,
                'gray_env':   [cmd for cmd in project.svn_master.gray_env.split('\n') if cmd.strip() != "" ],
                'online_env': [cmd for cmd in project.svn_master.online_env.split('\n') if cmd.strip() != "" ],
                'rollback':   [cmd for cmd in project.svn_master.rollback.split('\n') if cmd.strip() != "" ],
            },
        }

        items.append(tmpdict)

    return render(
        request,
        'upgrade/operate.html',
        {
            'title':    title,
            'clientip': clientip,
            'role':     role,
            'username': username,
            'items':    json.dumps(items),
        }
    )