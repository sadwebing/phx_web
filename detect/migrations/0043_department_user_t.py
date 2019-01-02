# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-02 11:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detect', '0042_domains_auto_m_dns'),
    ]

    operations = [
        migrations.CreateModel(
            name='department_user_t',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('user', models.ManyToManyField(db_constraint=False, to='detect.telegram_user_id_t')),
            ],
        ),
    ]