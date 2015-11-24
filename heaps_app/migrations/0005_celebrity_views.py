# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0004_auto_20151122_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='celebrity',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
