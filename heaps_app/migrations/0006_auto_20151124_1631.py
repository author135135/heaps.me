# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0005_celebrity_views'),
    ]

    operations = [
        migrations.CreateModel(
            name='CelebrityViewsStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField()),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='celebrity',
            options={'ordering': ('-views',), 'verbose_name_plural': 'celebrities'},
        ),
        migrations.AddField(
            model_name='celebrityviewsstat',
            name='celebrity',
            field=models.ForeignKey(to='heaps_app.Celebrity'),
        ),
    ]
