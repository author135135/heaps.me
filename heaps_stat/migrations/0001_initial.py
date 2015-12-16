# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0007_auto_20151216_1212'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialLinkClicks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('social_network', models.CharField(max_length=75)),
                ('clicks_count', models.IntegerField()),
                ('celebrity', models.ForeignKey(to='heaps_app.Celebrity')),
            ],
        ),
        migrations.CreateModel(
            name='SocialLinkClicksStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField()),
                ('date', models.DateField(auto_now_add=True)),
                ('social_link_clicks', models.ForeignKey(to='heaps_stat.SocialLinkClicks')),
            ],
        ),
    ]
