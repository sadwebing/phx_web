# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db       import models
from django.utils    import timezone
from phxweb.settings import choices_customer, choices_product, choices_permission, choices_s, choices_proj
# Create your models here.

class svn_customer_t(models.Model):
    '''
        客户表，记录各家客户的升级参数，包括服务IP等
    '''
    name          = models.CharField(max_length=32, unique=True, null=False)
    customer      = models.IntegerField(choices=choices_customer, default=29)
    project       = models.CharField(max_length=10, choices=choices_proj, default='caipiao')
    master_ip     = models.TextField(blank=True, null=True)
    port          = models.CharField(max_length=6, null=False, default='22')
    ip            = models.TextField(blank=True, null=True)
    ismaster      = models.IntegerField(choices=choices_s, default=0)
    isrsynccode   = models.IntegerField(choices=choices_s, default=0)
    cmd           = models.TextField(blank=True, null=True)
    gray_domain   = models.CharField(max_length=128, blank=True)
    online_domain = models.CharField(max_length=128, blank=True)
    src_d         = models.CharField(max_length=128, blank=True)
    dst_d         = models.CharField(max_length=128, blank=True)
    status        = models.IntegerField(choices=choices_s, default=1)
    info          = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('name', 'customer' ,'project')

    def __str__(self):
        return " - ".join([self.name, self.get_customer_display(), self.get_project_display(), "主控: "+self.get_ismaster_display(), "状态: "+self.get_status_display()])

class svn_gray_lock_t(models.Model):
    '''
        svn灰度锁，记录锁住的svn记录
    '''
    revision   = models.IntegerField(unique=True, null=False)
    author     = models.CharField(max_length=32, null=False)
    date       = models.CharField(max_length=32, null=False)
    log        = models.TextField(blank=True, null=True)
    changelist = models.TextField(blank=False, null=False)

    def __str__(self):
        return " - ".join([str(self.revision), self.author, self.date, self.log])

class svn_record_t(models.Model):
    '''
        svn记录，每个环境升级了哪些客户
    '''
    revision   = models.IntegerField(unique=True, null=False)
    author     = models.CharField(max_length=32, null=False)
    date       = models.CharField(max_length=32, null=False)
    log        = models.TextField(blank=True, null=True)
    changelist = models.TextField(blank=False, null=False)
    svn_gray   = models.ManyToManyField(svn_customer_t, related_name="gray" , blank=True, db_constraint=False)
    svn_online = models.ManyToManyField(svn_customer_t, related_name="online" ,blank=True, db_constraint=False)
    mod_date   = models.DateTimeField('解析最后修改日期', default=timezone.now)

    def __str__(self):
        return " - ".join([str(self.revision), self.author, self.date, self.log])
