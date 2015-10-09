# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='celebrity_subscribe',
            field=models.ManyToManyField(to='heaps_app.Celebrity'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default=b'defaults/default_gravatar.png', null=True, upload_to=b'avatars/%Y/%m/%d', blank=True),
        ),
    ]
