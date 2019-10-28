# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-28 13:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0098_auto_20191013_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project_t',
            name='customer',
            field=models.IntegerField(choices=[(29, '\u516c\u5171\u5ba2\u6237[pub]'), (1, '\u963f\u91cc[ali]'), (2, '\u5149\u5927[guangda]'), (34, '\u6052\u8fbe[hengda]'), (121001, '\u6052\u4fe1[hengxin]'), (3, '\u4e50\u76c8|\u718a\u732b[leying]'), (4, '\u5f69\u6295[caitou]'), (5, '\u5929\u5929[tiantian]'), (6, '\u4e09\u5fb7|\u5bcc\u8c6a|668[sande]'), (7, 'uc\u5f69\u7968[uc]'), (10, 'ag\u5f69[agcai]'), (23, '\u4ebf\u817e[yiteng]'), (11, '\u4e07\u6e38[klc]'), (39, '68\u5f69[68bet]'), (40, '567\u5f69[567bet]'), (41, '\u4e13\u4e1a\u76d8\u5f69\u7968[zyp]'), (42, '\u98de\u4fe1[feixin]'), (43, '\u4e16\u5f69\u5802[sct]'), (8, '\u8c37\u6b4c[9393cp]'), (9, '\u82f9\u679c[188cp|3535]'), (19, '\u8292\u679c[1717cp]'), (21, '\u4e50\u90fd\u57ce[ldc]'), (36, '\u745e\u94f6[ruiyin|UBS]'), (37, '\u52c7\u58eb[warrior]'), (38, '\u4f53\u5f69[tc]'), (121002, '565sport[565\u4f53\u80b2]'), (121003, 'newregal[\u65b0\u5bcc\u8c6a]'), (13, '\u94bb\u77f3[le7|diamond]'), (32, '\u4e16\u5fb7[shide]'), (33, '\u56fe\u817e[tuteng]'), (31, '\u6052\u9686[henglong]'), (35, '\u8fea\u62dc\u5427[dibaiba]'), (101001, 'BB\u68cb\u724c'), (101002, '\u6c6a\u6c6a\u68cb\u724c'), (101003, 'H5\u68cb\u724c')], default=29),
        ),
        migrations.AlterField(
            model_name='telegram_domain_alert_t',
            name='customer',
            field=models.IntegerField(choices=[(29, '\u516c\u5171\u5ba2\u6237[pub]'), (1, '\u963f\u91cc[ali]'), (2, '\u5149\u5927[guangda]'), (34, '\u6052\u8fbe[hengda]'), (121001, '\u6052\u4fe1[hengxin]'), (3, '\u4e50\u76c8|\u718a\u732b[leying]'), (4, '\u5f69\u6295[caitou]'), (5, '\u5929\u5929[tiantian]'), (6, '\u4e09\u5fb7|\u5bcc\u8c6a|668[sande]'), (7, 'uc\u5f69\u7968[uc]'), (10, 'ag\u5f69[agcai]'), (23, '\u4ebf\u817e[yiteng]'), (11, '\u4e07\u6e38[klc]'), (39, '68\u5f69[68bet]'), (40, '567\u5f69[567bet]'), (41, '\u4e13\u4e1a\u76d8\u5f69\u7968[zyp]'), (42, '\u98de\u4fe1[feixin]'), (43, '\u4e16\u5f69\u5802[sct]'), (8, '\u8c37\u6b4c[9393cp]'), (9, '\u82f9\u679c[188cp|3535]'), (19, '\u8292\u679c[1717cp]'), (21, '\u4e50\u90fd\u57ce[ldc]'), (36, '\u745e\u94f6[ruiyin|UBS]'), (37, '\u52c7\u58eb[warrior]'), (38, '\u4f53\u5f69[tc]'), (121002, '565sport[565\u4f53\u80b2]'), (121003, 'newregal[\u65b0\u5bcc\u8c6a]'), (13, '\u94bb\u77f3[le7|diamond]'), (32, '\u4e16\u5fb7[shide]'), (33, '\u56fe\u817e[tuteng]'), (31, '\u6052\u9686[henglong]'), (35, '\u8fea\u62dc\u5427[dibaiba]'), (101001, 'BB\u68cb\u724c'), (101002, '\u6c6a\u6c6a\u68cb\u724c'), (101003, 'H5\u68cb\u724c')], default=29),
        ),
        migrations.AlterField(
            model_name='telegram_ssl_alert_t',
            name='customer',
            field=models.IntegerField(choices=[(29, '\u516c\u5171\u5ba2\u6237[pub]'), (1, '\u963f\u91cc[ali]'), (2, '\u5149\u5927[guangda]'), (34, '\u6052\u8fbe[hengda]'), (121001, '\u6052\u4fe1[hengxin]'), (3, '\u4e50\u76c8|\u718a\u732b[leying]'), (4, '\u5f69\u6295[caitou]'), (5, '\u5929\u5929[tiantian]'), (6, '\u4e09\u5fb7|\u5bcc\u8c6a|668[sande]'), (7, 'uc\u5f69\u7968[uc]'), (10, 'ag\u5f69[agcai]'), (23, '\u4ebf\u817e[yiteng]'), (11, '\u4e07\u6e38[klc]'), (39, '68\u5f69[68bet]'), (40, '567\u5f69[567bet]'), (41, '\u4e13\u4e1a\u76d8\u5f69\u7968[zyp]'), (42, '\u98de\u4fe1[feixin]'), (43, '\u4e16\u5f69\u5802[sct]'), (8, '\u8c37\u6b4c[9393cp]'), (9, '\u82f9\u679c[188cp|3535]'), (19, '\u8292\u679c[1717cp]'), (21, '\u4e50\u90fd\u57ce[ldc]'), (36, '\u745e\u94f6[ruiyin|UBS]'), (37, '\u52c7\u58eb[warrior]'), (38, '\u4f53\u5f69[tc]'), (121002, '565sport[565\u4f53\u80b2]'), (121003, 'newregal[\u65b0\u5bcc\u8c6a]'), (13, '\u94bb\u77f3[le7|diamond]'), (32, '\u4e16\u5fb7[shide]'), (33, '\u56fe\u817e[tuteng]'), (31, '\u6052\u9686[henglong]'), (35, '\u8fea\u62dc\u5427[dibaiba]'), (101001, 'BB\u68cb\u724c'), (101002, '\u6c6a\u6c6a\u68cb\u724c'), (101003, 'H5\u68cb\u724c')], default=29),
        ),
    ]
