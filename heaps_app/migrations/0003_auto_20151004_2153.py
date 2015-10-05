# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0002_auto_20151002_1832'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='celebrity',
            options={'ordering': ('-created_at',), 'verbose_name_plural': 'celebrities'},
        ),
        migrations.AlterField(
            model_name='celebrity',
            name='filter',
            field=models.ManyToManyField(to='heaps_app.Filter', blank=True),
        ),
    ]
