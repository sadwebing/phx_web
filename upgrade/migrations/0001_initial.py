# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-22 16:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='svn_customer_t',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('customer', models.IntegerField(choices=[(29, '\u516c\u5171\u5ba2\u6237[pub]'), (1, '\u963f\u91cc[ali]'), (2, '\u5149\u5927[guangda]'), (34, '\u6052\u8fbe[hengda]'), (3, '\u4e50\u76c8|\u718a\u732b[leying]'), (4, '\u5f69\u6295[caitou]'), (5, '\u5929\u5929[tiantian]'), (6, '\u4e09\u5fb7|\u5bcc\u8c6a|668[sande]'), (7, 'uc\u5f69\u7968[uc]'), (10, 'ag\u5f69[agcai]'), (23, '\u4ebf\u817e[yiteng]'), (11, '\u4e07\u6e38[wanyou]'), (8, '\u8c37\u6b4c[9393cp]'), (9, '\u82f9\u679c[188cp|3535]'), (19, '\u8292\u679c[1717cp]'), (21, '\u4e50\u90fd\u57ce[ldc]'), (36, '\u745e\u94f6[ruiyin|UBS]'), (37, '\u52c7\u58eb[warrior]'), (38, '\u4f53\u5f69[tc]'), (13, '\u94bb\u77f3[le7]'), (32, '\u4e16\u5fb7[shide]'), (33, '\u56fe\u817e[tuteng]'), (31, '\u6052\u9686[henglong]'), (35, '\u8fea\u62dc\u5427[dibaiba]')], default=29)),
                ('master_ip', models.TextField(default='', null=True)),
                ('ip', models.TextField(default='', null=True)),
                ('ismaster', models.IntegerField(choices=[(1, b'\xe5\x90\xaf\xe7\x94\xa8'), (0, b'\xe7\xa6\x81\xe7\x94\xa8')], default=0)),
                ('isrsynccode', models.IntegerField(choices=[(1, b'\xe5\x90\xaf\xe7\x94\xa8'), (0, b'\xe7\xa6\x81\xe7\x94\xa8')], default=0)),
                ('cmd', models.TextField(default='', null=True)),
                ('gray_domain', models.CharField(max_length=128, unique=True)),
                ('online_domain', models.CharField(max_length=128, unique=True)),
                ('src_d', models.CharField(max_length=128, unique=True)),
                ('dst_d', models.CharField(max_length=128, unique=True)),
            ],
        ),
    ]
