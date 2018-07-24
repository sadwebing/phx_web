# coding: utf8
from __future__ import unicode_literals

from django.db                  import models
from django.contrib.auth.models import User
from django.core                import exceptions
from phxweb.settings            import choices_prod
from detect.models              import domains
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#domain_D = domains.objects.get(id=1)

choices_s = (
        (1, '启用'), 
        (0, '禁用'),
        )

class telegram_user_id_t(models.Model):
    user = models.CharField(max_length=32, null=False)
    name = models.CharField(max_length=32, null=False)
    user_id = models.IntegerField()
    class Meta:
        unique_together = ('user' ,'user_id')

    def __str__(self):
        return " | ".join([self.user, self.name, str(self.user_id)])

class minion_ip_t(models.Model):
    minion_id = models.CharField(max_length=32, null=False)
    ip_addr = models.GenericIPAddressField()
    status = models.IntegerField(choices=choices_s, default=1)
    class Meta:
        unique_together = ('minion_id' ,'ip_addr')

    def __str__(self):
        return " - ".join([self.minion_id, self.ip_addr, self.get_status_display()])

class minion_t(models.Model):
    choices_provider = (
            (1, '台湾机房'), 
            (2, '香港机房'),
            (3, 'fent'),
            (4, '星联'),
            (5, '久速'),
            (6, '杜杜'),
            (7, '网时'),
            (8, '优与云'),
            (9, '阿里云'),
        )

    minion_id = models.CharField(max_length=32, unique=True, null=False)
    user      = models.CharField(max_length=24, default='root')
    port      = models.IntegerField(null=False, default=11223)
    password  = models.TextField(null=False, default='/')
    price     = models.IntegerField(null=True)
    provider  = models.IntegerField(choices=choices_provider, null=False, default=1)
    status    = models.IntegerField(choices=choices_s, default=1)
    info      = models.TextField(blank=True)

    def __str__(self):
        return " - ".join([self.minion_id, self.get_provider_display(), self.get_status_display()])

class project_t(models.Model):
    choices_env = (
        (1, '运营环境'), 
        (0, '测试环境'),
        )
    choices_st = (
        ('nginx',  'nginx'), 
        ('apache', 'apache'),
        ('vpn',    'vpn'),
        ('flask',  'flask'),
        )
    choices_role = (
        ('main',   'main'), 
        ('backup', 'backup'),
        )
    choices_proj = (
        ('caipiao', 'caipiao'), 
        ('sport',   'sport'),
        ('houtai',  'houtai'),
        ('pay',     'pay'),
        ('ggz',     'ggz'),
        ('vpn',     'vpn'),
        ('image',   'image'),
        ('httpdns', 'httpdns'),
        )

    envir       = models.IntegerField(choices=choices_env, default=1)
    product     = models.IntegerField(choices=choices_prod)
    project     = models.CharField(max_length=10, choices=choices_proj)
    minion_id   = models.ManyToManyField(minion_t)
    user        = models.CharField(max_length=24, default='root')
    port        = models.IntegerField(null=False, default=11223)
    password    = models.TextField(null=False, default='/')
    server_type = models.CharField(max_length=10, choices=choices_st, default='nginx')
    role        = models.CharField(max_length=10, choices=choices_role, default='main')
    #domain      = models.ForeignKey(domains, default=domain_D.id)
    uri         = models.CharField(max_length=128, default='/')
    status      = models.IntegerField(choices=choices_s, default=1)
    svn         = models.IntegerField(choices=choices_s, default=1)
    privatekey  = models.TextField(null=False, default='thisisdefaultprivatekey')
    publickey   = models.TextField(null=False, default='thisisdefaultpublickey')
    info        = models.CharField(max_length=128, blank=True)
    class Meta:
        unique_together = ('product' ,'project' ,'envir', 'server_type')

    def __str__(self):
        return " - ".join([self.get_envir_display(), self.get_product_display(), self.get_project_display(), self.get_server_type_display(), self.get_status_display()])

class cdn_proj_t(models.Model):
    choices_proj = (
        (0, 'fh_app'),
        (1, 'fh_cp_static'),
        (3, 'fh_sp_static'),
        (2, 'ry_sp_static'),
        (4, 'java_cp_static'),
        )

    project = models.IntegerField(choices=choices_proj, unique=True)
    domain  = models.ManyToManyField(domains)
    #cdn     = models.ManyToManyField(cdn_t)

    def __str__(self):
        return " - ".join([self.get_project_display()])

class project_authority_t(models.Model):
    name    = models.CharField(max_length=128, unique=True)
    project = models.ManyToManyField(project_t, blank=True)
    read    = models.IntegerField(choices=choices_s, default=1)
    write   = models.IntegerField(choices=choices_s, default=0)

    def __str__(self):
        return self.name +" | 读权限: "+ self.get_read_display() +" | 写权限: "+ self.get_write_display()
