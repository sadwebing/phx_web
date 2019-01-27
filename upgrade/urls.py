# -*- coding: utf-8 -*-

from django.conf.urls          import url, include
from django.views.generic.base import RedirectView
from .       import views
from current import *

urlpatterns = [
    url('^operate$', views.Operate, name='Operate'),
    url('^remote_exe$', views.remoteExe, name='remoteExe'),

    #当前svn记录
    url('^current$', views.Current, name='Current'),
    url('^current/Query$', CurrentQuery, name='CurrentQuery'),
    url('^current/Add$', CurrentAdd, name='CurrentAdd'),

    #升级
    url('^get_svn_customer$', views.GetSvnCustomer, name='GetSvnCustomer'),
    url('^get_svn_records$', views.GetSvnRecords, name='GetSvnRecords'),
    url('^get_svn_lock_records$', views.GetSvnLockRecords, name='GetSvnLockRecords'),
    url('^get_svn_master$', views.GetSvnMaster, name='GetSvnMaster'),
]