# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0007_auto_20151216_1212'),
    ]

    operations = [
        migrations.CreateModel(
            name='CelebrityFacebookPosts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_id', models.CharField(unique=True, max_length=50)),
                ('post_avatar', models.URLField(max_length=300)),
                ('post_publisher', models.CharField(max_length=100)),
                ('post_link', models.URLField()),
                ('type', models.CharField(max_length=50)),
                ('message', models.TextField(null=True, blank=True)),
                ('picture', models.TextField(null=True, blank=True)),
                ('link', models.URLField(max_length=300, null=True, blank=True)),
                ('source', models.TextField(null=True, blank=True)),
                ('name', models.CharField(max_length=150, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('caption', models.TextField(null=True, blank=True)),
                ('created_time', models.DateTimeField()),
                ('celebrity', models.ForeignKey(related_name='celebrity_facebook_posts', to='heaps_app.Celebrity')),
            ],
        ),
    ]
