#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from dwebsocket                     import require_websocket, accept_websocket
from models                         import domains, department_user_t, telegram_chat_group_t 
from monitor.models                 import telegram_ssl_alert_t
from accounts.limit                 import LimitAccess
from telegram                       import sendTelegram
from phxweb                         import settings
import json, logging, requests, re

logger = logging.getLogger('django')

@csrf_protect
@login_required
def TelegramGroup(request):
    title = u'Telegram-群组信息'
    global username, role, clientip
    username = request.user.username
    try:
        role = request.user.userprofile.role
    except:
        role = 'none'
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        clientip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        clientip = request.META['REMOTE_ADDR']
    logger.info('%s is requesting %s' %(clientip, request.get_full_path()))

    # 获取需要@的群组人员
    atUsers = {}
    if request.user.is_superuser:
        atUsersSelects = department_user_t.objects.filter(status=1).all()
    elif role == "sa":
        atUsersSelects = department_user_t.objects.filter(status=1).all()
    else:
        atUsersSelects = department_user_t.objects.filter(status=1).all()

    # 获取需要发送信息的群组
    groups = {}
    if request.user.is_superuser:
        groupSelects = telegram_chat_group_t.objects.filter(status=1).all()
    elif role == "sa":
        groupSelects = telegram_chat_group_t.objects.filter(status=1, group__in=['kindergarten', 'zhuanyepan', 'yunwei']).all()
    else:
        groupSelects = telegram_chat_group_t.objects.filter(status=1, group__in=['kindergarten', 'zhuanyepan']).all()

    for department in atUsersSelects:
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

    for group in groupSelects:
        groups[group.group] = {
            'id': group.id,
            'group': group.group,
            'name':  group.name,
            'group_id': group.group_id,
        }


    return render(
        request,
        'detect/telegram_group.html',
        {
            'title':    title,
            'clientip': clientip,
            'role':     role,
            'username': username,
            'atUsers':  json.dumps(atUsers),
            'groups':   json.dumps(groups),
        }
    )

@csrf_exempt
def SendTelegram(request):
    title = u'发送telegram信息'
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        clientip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        clientip = request.META['REMOTE_ADDR']
    logger.info('%s is requesting %s' %(clientip, request.get_full_path()))

    if request.method == 'POST':
        try:
            message = json.loads(request.body)
            if not isinstance(message, dict): 
                logger.error('%s is not dict.' %message)
                s = sendTelegram({'text': clientip + ': 发送telegram信息失败，参数不是字典！', 'bot': 'sa_monitor_bot', 'group': 'arno_test'}) #arno_test
                if s.send():
                    return HttpResponse(content='参数错误！', status=500)
                else: 
                    return HttpResponse(content='telegram 发送失败！', status=502)
        except Exception, e:
            logger.error(e.message)
            s = sendTelegram({'text': clientip + ': 发送telegram信息失败！\r\n' + e.message, 'bot': 'sa_monitor_bot', 'group': 'arno_test'}) #arno_test
            if s.send():
                return HttpResponse(content='参数错误！', status=500)
            else: 
                return HttpResponse(content='telegram 发送失败！', status=502)


        s = sendTelegram(message)
        if s.send():
            return HttpResponse('发送成功！')
        else: 
            return HttpResponse(content='telegram 发送失败，参数错误！', status=502)
    else:
        return HttpResponse(status=403)

@csrf_exempt
def Telegramsendgroupmessage(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        clientip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        clientip = request.META['REMOTE_ADDR']
    logger.info('%s is requesting %s' %(clientip, request.get_full_path()))

    if request.method == 'POST':
        message = settings.message_TEST
        try:
            datas = json.loads(request.body)
            if not isinstance(datas, dict): 
                logger.error('%s is not dict.' %datas)
                s = sendTelegram({'text': clientip + ': 发送telegram信息失败，参数不是字典！', 'bot': 'sa_monitor_bot', 'group': 'arno_test'}) #arno_test
                if s.send():
                    return HttpResponse(content='参数错误！', status=500)
                else: 
                    return HttpResponse(content='telegram 发送失败！', status=502)
        except Exception, e:
            logger.error(e.datas)
            s = sendTelegram({'text': clientip + ': 发送telegram信息失败！\r\n' + e.datas, 'bot': 'sa_monitor_bot', 'group': 'arno_test'}) #arno_test
            if s.send():
                return HttpResponse(content='参数错误！', status=500)
            else: 
                return HttpResponse(content='telegram 发送失败！', status=502)

        # 获取需要@的部门或组
        atUsers = []
        atUsersSelects = department_user_t.objects.filter(status=1, id__in=datas['atUsers']).all()
        for department in atUsersSelects:
            atUsers.append(department.department + ': ' + ', '.join([ '@'+user.user for user in department.user.filter(status=1).all() ]))

        for group in datas['group']:
            message['group'] = group
            message['text']  = datas['text'] + '\r\n\r\n' + '\r\n'.join(atUsers)

            s = sendTelegram(message)
            if s.send():
                return HttpResponse('发送成功！')
            else: 
                return HttpResponse(content='telegram 发送失败，参数错误！', status=502)

    else:
        return HttpResponse(status=403)

@csrf_exempt
def TelegramUploadimgs(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        clientip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        clientip = request.META['REMOTE_ADDR']
    logger.info('%s is requesting %s' %(clientip, request.get_full_path()))

    if request.method == 'POST':
        message = settings.message_TEST

        img = request.FILES['txt_file']
        group = request.GET['group']
        
        message['group'] = group
        s = sendTelegram(message)
        if s.sendPhoto(img):
            return HttpResponse(json.dumps({'result': '图片发送成功'}))
        else: 
            return HttpResponse(content=json.dumps({'result': '图片发送失败'}), status=502)

        return HttpResponse(json.dumps({'result': '图片发送成功'}))

    else:
        return HttpResponse(status=403)

@csrf_exempt
def GetDomains(request):
    title = u'获取检测域名'
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        clientip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        clientip = request.META['REMOTE_ADDR']
    logger.info('%s is requesting %s' %(clientip, request.get_full_path()))
    domain_dict = {'domain':[], 'alert':{'default':None, 'others':[]}}

    if request.method == 'POST':
        try:
            product  = json.loads(request.body)['product']
            if str(product).lower() == 'all':
                domain_l = domains.objects.filter(status=1).all()
            else:
                domain_l = domains.objects.filter(status=1, product=product).all()

            alert_l  = telegram_ssl_alert_t.objects.filter(status=1).all()
        except Exception, e:
            logger.error(e.message)
            domain_l = []
            alert_l  = []

        for alert in alert_l:
            tmp_dict = {
                'name': alert.name,
                'chat_group': [ group.group for group in alert.chat_group.all() ],
                'user':       [ user.user for user in alert.user_id.all() ],
                'product':  (alert.product, alert.get_product_display()),
                'customer': (alert.customer, alert.get_customer_display()),
                'ex_one_m':  "",
                'ex_half_y': "",
                'failed':    "",
            }
            if tmp_dict['name'] == "默认":
                domain_dict['alert']['default']=tmp_dict
            else:
                domain_dict['alert']['others'].append(tmp_dict)

        for domain in domain_l:
            tmp_dict = {}
            tmp_dict['name']     = domain.name
            tmp_dict['product']  = (domain.product, domain.get_product_display())
            tmp_dict['customer'] = (domain.customer, domain.get_customer_display())
            tmp_dict['client']   = domain.group.client
            tmp_dict['method']   = domain.group.method
            tmp_dict['ssl']      = domain.group.ssl
            tmp_dict['retry']    = domain.group.retry
            domain_dict['domain'].append(tmp_dict)
        return HttpResponse(json.dumps(domain_dict))
    else:
        return HttpResponse(status=403)

@csrf_exempt
def getAtUsers(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        clientip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        clientip = request.META['REMOTE_ADDR']
    logger.info('%s is requesting %s' %(clientip, request.get_full_path()))

    if request.method == 'POST':
        atUsers = {}
        try:
            for department in department_user_t.objects.filter(status=1).all():
                atUsers[department.name] = {
                    'users': [ 
                        {
                            'name': user.name,
                            'user': user.user,
                            'user_id': user.user_id,
                        }
                        for user in department.user.filter(status=1).all() ],
                    'atUsers': department.AtUsers(),
                    'display': department.display(),
                }
                
        except Exception, e:
            logger.error(e.message)
            s = sendTelegram({'text': clientip + ': 发送telegram信息失败！\r\n' + e.message, 'bot': 'sa_monitor_bot', 'group': 'arno_test'}) #arno_test
            if s.send():
                return HttpResponse(content='参数错误！', status=500)
            else: 
                return HttpResponse(content='telegram 发送失败！', status=502)

        return HttpResponse(json.dumps(atUsers))
    else:
        return HttpResponse(status=403)