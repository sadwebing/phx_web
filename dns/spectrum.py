# coding: utf8
from django.shortcuts import render
from django.http      import HttpResponse, HttpResponseForbidden
from dwebsocket       import require_websocket
from models           import cf_account, dnspod_account
from cf_api           import CfApi
from dnspod           import *
from cf               import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf   import csrf_exempt, csrf_protect

import json, logging, requests, re, datetime
logger = logging.getLogger('django')

@csrf_protect
@login_required
def Index(request):
    title = u'CloudFlare-spectrum主页'
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

    #if request.user.userprofile.manage == 1:
    #    product_list = [ name[0] for name in cf_account.objects.values_list("name").all().order_by("name")]
    #else:
    #    product_list = [ dns.cf_account.name for dns in request.user.userprofile.dns.filter(permission='read').all() if dns.cf_account ]
        
    #product_list.sort()
    #logger.info('%s %s' %(type(product_list), product_list))

    return render(
        request,
        'dns/cloudflare/spectrum_index.html',
        {
            'title': title,
            'clientip':clientip,
            'role': role,
            'username': username,
            #'product_list': product_list,
        }
    )