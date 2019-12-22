# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models         import svn_customer_t, svn_gray_lock_t, svn_record_t, svn_zyp_lottery_gray_lock_t, svn_zyp_front_gray_lock_t, svn_zyp_front2_gray_lock_t
# Register your models here.

admin.site.register(svn_customer_t)
admin.site.register(svn_gray_lock_t)
admin.site.register(svn_record_t)
admin.site.register(svn_zyp_lottery_gray_lock_t)
admin.site.register(svn_zyp_front_gray_lock_t)
admin.site.register(svn_zyp_front2_gray_lock_t)