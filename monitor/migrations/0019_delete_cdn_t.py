# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0018_auto_20180629_2119'),
    ]

    operations = [
        migrations.DeleteModel(
            name='cdn_t',
        ),
    ]
