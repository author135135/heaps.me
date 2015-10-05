# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import heaps_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(upload_to=heaps_app.models.rename_file),
        ),
        migrations.AlterField(
            model_name='socialnetwork',
            name='social_network',
            field=models.CharField(max_length=75, choices=[(b'facebook', b'Facebook'), (b'vk', b'Vk'), (b'instagram', b'Instagram')]),
        ),
    ]
