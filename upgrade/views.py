# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http      import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from accounts.views   import HasPermission, HasServerPermission, getIp, getProjects
from monitor.models   import project_t, svn_master_t
from detect.models    import department_user_t
from upgrade.models   import svn_gray_lock_t, svn_customer_t, svn_record_t
from phxweb.svn_api   import SvnApi

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf   import csrf_exempt, csrf_protect

import json, logging, requests, datetime
logger = logging.getLogger('django')

# Create your views here.
@csrf_protect
@login_required
def Operate(request):
    title = u'升级中心-升级与APA推送'
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

    atUsers = {}
    for department in department_user_t.objects.filter(status=1).all():
        atUsers[department.name] = {
            'id': department.id,
            'department': department.department,
            'users': [ 
                {
                    'name': user.name,
                    'user': user.user,
                    'user_id': user.user_id,
                }
                for user in department.user.filter(status=1).all() ],
            'atUsers': department.AtUsers(),
            'display': department.display().replace(' ', ''),
        }

    logger.info(atUsers)

    items = []
    for project in projects:
        if project.svn_mst_alive == 0: continue
        svn_customer_together = [ svn_customer.replace(' ', '') for svn_customer in project.svn_customer_together.split('\r\n') if svn_customer.strip() != "" ] if project.svn_customer_together else []
        svn_customer_single   = []
        svn_customer_all      = []
        svn_customer_tmp      = []

        for rec in svn_customer_together:
            for i in rec.strip().split(','):
                if i.strip() != '': svn_customer_tmp.append(i.strip())

        for rec in project.svn_customer.all():
            name = rec.name.replace(' ', '')
            tmpdict = {
                'id': rec.id,
                'name': name,
                'isrsynccode': rec.isrsynccode,
            }
            svn_customer_all.append(tmpdict)
            if rec.isrsynccode == 0: continue
            if name not in svn_customer_tmp:
                    svn_customer_single.append(name)

        tmpdict = {
            'id':       project.id,
            'envir':    (project.envir, project.get_envir_display()),
            'product':  (project.product, project.get_product_display()),
            'project':  (project.project, project.get_project_display()),
            'customer': (project.customer, project.get_customer_display()),
            'server_type': (project.server_type, project.get_server_type_display()),
            'info':     project.info,
            'svn_master':  {
                'id':         project.svn_master.id,
                'name':       project.svn_master.name,
                'minion_id':  project.svn_master.minion_id.minion_id,
                'api':        project.svn_master.api,
                'gray_env':   [cmd.strip() for cmd in project.svn_master.gray_env.split('\r\n') if cmd.strip() != "" ],
                'online_env': [cmd.strip() for cmd in project.svn_master.online_env.split('\r\n') if cmd.strip() != "" ],
                'rollback':   [cmd.strip() for cmd in project.svn_master.rollback.split('\r\n') if cmd.strip() != "" ],
            },
            'svn_customer': {
                'in': svn_customer_all,
                'ex': svn_customer_single + svn_customer_together,
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
            'atUsers':  json.dumps(atUsers),
        }
    )

@csrf_protect
@login_required
def Current(request):
    title = u'升级中心-当前SVN记录'
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

    return render(
        request,
        'upgrade/current.html',
        {
            'title':    title,
            'clientip': clientip,
            'role':     role,
            'username': username,
        }
    )

@csrf_exempt
def GetSvnCustomer(request):
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
        svn_customers = project_t.objects.get(id=25).svn_customer.all()
        for svn_customer in svn_customers:
            tmpdict = {
                'name': svn_customer.name.strip(),
                'customer': (svn_customer.customer, svn_customer.get_customer_display()),
                'project': (svn_customer.project, svn_customer.get_project_display()),
                'master_ip': [ ip.replace(' ', '').replace('\r', '') for ip in svn_customer.master_ip.split('\n') if ip.replace(' ', '').replace('\r', '') != '' ],
                'port': svn_customer.port.strip(),
                'ip': [ ip.replace(' ', '').replace('\r', '') for ip in svn_customer.ip.split('\n') if ip.replace(' ', '').replace('\r', '') != '' ],
                'ismaster': True if svn_customer.ismaster == 1 else False,
                'isrsynccode': True if svn_customer.isrsynccode == 1 else False,
                'cmd': [ cmd.replace(' ', '').replace('\r', '') for cmd in svn_customer.cmd.split('\n') if cmd.replace(' ', '').replace('\r', '') != '' ],
                'gray_domain': svn_customer.gray_domain.strip(),
                'online_domain': svn_customer.online_domain.strip(),
                'src_d': svn_customer.src_d.strip(),
                'dst_d': svn_customer.dst_d.strip(),
                'info': svn_customer.info,
            }
            record_list.append(tmpdict)
        return HttpResponse(json.dumps(record_list))
    else:
        return HttpResponse('nothing!')

@csrf_exempt
def GetSvnRecords(request):
    if request.method == 'GET':
        return HttpResponse('You get nothing!')
    elif request.method == 'POST':
        clientip = getIp(request)
        username = request.user.username
        try:
            role = request.user.userprofile.role
        except:
            role = 'none'
        if not username:
            logger.info('user: 用户名未知 | [POST]%s is requesting. %s' %(clientip, request.get_full_path()))
            return HttpResponseServerError("用户名未知！")

        data = json.loads(request.body)

        logger.info('[POST]%s is requesting. %s' %(clientip, request.get_full_path()))

        try:
            svn_master = svn_master_t.objects.get(id=data['svn_master_id'])
        except Exception as e:
            error = "获取svn master 信息失败："+str(e)
            logger.error(error)
            return HttpResponseServerError(error)
        
        svnapi = SvnApi(svn_master.svn_code_url, svn_master.svn_code_u, svn_master.svn_code_p)
        svn_records = svnapi.GetLog(limit=30)

        return HttpResponse(json.dumps(svn_records))
    else:
        return HttpResponse('nothing!')

@csrf_exempt
def GetSvnLockRecords(request):
    if request.method == 'GET':
        return HttpResponse('You get nothing!')
    elif request.method == 'POST':
        clientip = getIp(request)
        username = request.user.username
        try:
            role = request.user.userprofile.role
        except:
            role = 'none'
        if not username:
            logger.info('user: 用户名未知 | [POST]%s is requesting. %s' %(clientip, request.get_full_path()))
            return HttpResponseServerError("用户名未知！")

        data = json.loads(request.body)

        logger.info('[POST]%s is requesting. %s' %(clientip, request.get_full_path()))

        try:
            svn_master = svn_master_t.objects.get(id=data['svn_master_id'])
        except Exception as e:
            error = "获取svn master 信息失败："+str(e)
            logger.error(error)
            return HttpResponseServerError(error)
        
        svn_records = []

        for svn_record in svn_master.svn_gray_lock.all():
            tmpdict = {
                    'revision':   svn_record.revision,
                    'author':     svn_record.author,
                    'date':       svn_record.date,
                    'log':        svn_record.log,
                    'changelist': svn_record.changelist,
                }
            svn_records.append(tmpdict)

        return HttpResponse(json.dumps(svn_records))
    else:
        return HttpResponse('nothing!')

@csrf_exempt
def GetSvnMaster(request):
    if request.method == 'GET':
        return HttpResponse('You get nothing!')
    elif request.method == 'POST':
        clientip = getIp(request)

        logger.info('[POST]%s is requesting. %s' %(clientip, request.get_full_path()))

        try:
            svn_customers = svn_customer_t.objects.filter(ismaster=1, isrsynccode=1).all()
        except Exception as e:
            error = "获取svn_customer 信息失败："+str(e)
            logger.error(error)
            return HttpResponseServerError(error)
        
        ips = []

        for svn_customer in svn_customers:
            ips += [ ip.strip() for ip in svn_customer.master_ip.split('\r\n') if ip.strip() != "" ]
        
        ips = list(set(ips))

        return HttpResponse(json.dumps(ips))
    else:
        return HttpResponse('nothing!')