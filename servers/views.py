# coding: utf8
from django.shortcuts import render
from django.http      import HttpResponse, HttpResponseForbidden
from dwebsocket       import require_websocket
from monitor.models   import project_t, minion_t, minion_ip_t
from accounts.views   import HasPermission, getIp
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf   import csrf_exempt, csrf_protect

import json, logging, requests, re, datetime, rsa, base64
logger = logging.getLogger('django')
setcookieV = {}

@csrf_protect
@login_required
def Index(request):
    title = u'服务器-列表'
    clientip = getIp(request)
    username = request.user.username
    try:
        role = request.user.userprofile.role
    except:
        role = 'none'

    if not username:
        logger.info('user: 用户名未知 | [POST]%s is requesting. %s' %(clientip, request.get_full_path()))
        return HttpResponseServerError("用户名未知！")

    projects = []

    try:
        authoritys = request.user.userprofile.servers.filter(read=1).all()
        for authority in authoritys:
            projects += [ project for project in authority.project.all().order_by('product')]
    except:
        projects = []


    logger.info('%s is requesting %s' %(clientip, request.get_full_path()))

    items = {
            'item': [],
            'envir': [],
            'product':     [],
            'project':     [],
            'customer':     [],
            'server_type': [],}

    #projects = project_t.objects.all()
    for project in projects:
        items['envir'].append((project.envir, project.get_envir_display()))
        items['item'].append(('_'.join([str(project.envir), str(project.product), str(project.project), str(project.server_type)]), '_'.join([project.get_envir_display(), project.get_product_display(), project.get_project_display(), project.get_server_type_display()])))
        items['product'].append((project.product, project.get_product_display())),
        items['project'].append((project.project, project.get_project_display())),
        items['customer'].append((project.customer, project.get_customer_display())),
        items['server_type'].append((project.server_type, project.get_server_type_display())),
    items['envir'] = list(set(items['envir']))
    items['product'] = list(set(items['product']))
    items['project'] = list(set(items['project']))
    items['customer'] = list(set(items['customer']))
    items['server_type'] = list(set(items['server_type']))

    return render(
        request,
        'servers/index.html',
        {
            'title':    title,
            'clientip': clientip,
            'role':     role,
            'username': username,
            'items':    items,
        }
    )

def decryptPasswd(request, project, passwd):
    error = "密码已加密[passwdEncrypted]"
    item  = '_'.join([str(project.envir), str(project.product), str(project.project), str(project.server_type)])
    item_display = '_'.join([project.get_envir_display(), project.get_product_display(), project.get_project_display(), project.get_server_type_display()])
    #解密 服务器密码
    try:
        data = json.loads(request.body)
        privatekey = data['privkey'][item]
        if not privatekey:
            setcookieV[item] = False
            try:
                privatekey = request.COOKIES[item]
            except:
                logger.error("failed to get cookies for %s" %item_display)
        else:
            setcookieV[item] = True
    except Exception, e:
        logger.error(str(e))
        setcookieV[item] = False
        privatekey       = None

    if privatekey:
        try:
            private_key = rsa.PrivateKey.load_pkcs1(privatekey) #获取私钥
            #private_key = rsa.PrivateKey.load_pkcs1(project.privatekey) #获取私钥
            password = rsa.decrypt(base64.decodestring(passwd), private_key).decode() #用私钥解密
        except Exception, e:
            logger.error(item_display+": "+str(e))
            password = error
    else:
        password = error
    return password

def setCookies(request, response, setcookieV):
    try:
        data = json.loads(request.body)
        for key in data['privkey']:
            if setcookieV.has_key(key) and setcookieV[key]:
                response.set_cookie(key, data['privkey'][key], max_age=604800)
    except Exception, e:
        logger.error(e)

def isStrinList(strA, listB):
    for item in listB:
        if strA in item:
            return True
    return False

@csrf_exempt
def GetServersRecords(request):
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
        logger.info('[POST]%s is requesting. %s' %(clientip, request.get_full_path()))

        projects = []

        try:
            data = json.loads(request.body)
            #projects = project_t.objects.filter(envir__in=data['envir'], product__in=data['product'], project__in=data['project'], server_type__in=data['server_type'], ).all()
            authoritys = request.user.userprofile.servers.filter(read=1).all()
            for authority in authoritys:
                projects += [ project for project in authority.project.filter(envir__in=data['envir'], product__in=data['product'], project__in=data['project'], customer__in=data['customer'], server_type__in=data['server_type']).all().order_by('product')]
        except Exception, e:
            logger.error(str(e))
            try:
                authoritys = request.user.userprofile.servers.filter(read=1).all()
                for authority in authoritys:
                    projects += [ project for project in authority.project.all().order_by('product')]
            except:
                projects = []

        servers_list = []
        return_list  = []

        for project in projects: #将项目数据循环获取
            if project.status == 0:
                continue #禁用的项目不做展示

            tmp_dict = {
                'envir':       project.get_envir_display(),
                'product':     project.get_product_display(),
                'project':     project.get_project_display(),
                'customer':    project.get_customer_display(),
                'server_type': project.get_server_type_display(),
                'password':    decryptPasswd(request, project, project.password),
                'user':        project.user,
                'port':        project.port,
                'role':        project.role,
                'uri':         project.uri,
                'info':        project.info,
                'minions':     [],
            }

            for minion in project.minion_id.all(): #将服务器属性数据循环获取
                if minion.status == 0:
                    continue #禁用的服务器不做展示

                ips = minion_ip_t.objects.filter(minion_id=minion.minion_id).all()

                minion_tmp_dict = {
                    'minion_id':    minion.minion_id,
                    'user':         minion.user,
                    'port':         minion.port,
                    'service_type': minion.get_service_type_display(),
                    'password':     decryptPasswd(request, project, minion.password),
                    'price':        minion.price,
                    'provider':     minion.get_provider_display(),
                    'info':         minion.info,
                    'ip':           [i.ip_addr for i in ips if i.status != 0]
                }

                #ip 刷选
                try:
                    data = json.loads(request.body)
                    ips  = data['ips']
                except:
                    tmp_dict['minions'].append(minion_tmp_dict)
                else:
                    if len(ips) != 0:
                        for ip in ips:
                            if isStrinList(ip, minion_tmp_dict['ip']):
                                tmp_dict['minions'].append(minion_tmp_dict)
                                break
                    else:
                        tmp_dict['minions'].append(minion_tmp_dict)

            servers_list.append(tmp_dict)

        response = HttpResponse(json.dumps(servers_list))
        setCookies(request, response, setcookieV)

        return response
    else:
        return HttpResponse('nothing!')