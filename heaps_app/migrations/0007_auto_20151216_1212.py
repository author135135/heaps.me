# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0006_auto_20151124_1631'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='filter',
            options={'ordering': ('title',)},
        ),
    ]
