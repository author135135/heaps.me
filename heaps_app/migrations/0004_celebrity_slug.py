# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0003_auto_20151004_2153'),
    ]

    operations = [
        migrations.AddField(
            model_name='celebrity',
            name='slug',
            field=models.SlugField(null=True),
        ),
    ]
