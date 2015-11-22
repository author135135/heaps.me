# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0003_auto_20151122_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filter',
            name='css_class',
            field=models.CharField(max_length=75),
        ),
    ]
