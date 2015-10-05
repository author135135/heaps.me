# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Celebrity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meta_title', models.CharField(max_length=100, null=True, blank=True)),
                ('meta_description', models.CharField(max_length=255, null=True, blank=True)),
                ('meta_keywords', models.CharField(max_length=255, null=True, blank=True)),
                ('firstname', models.CharField(max_length=50, null=True, blank=True)),
                ('lastname', models.CharField(max_length=75, null=True, blank=True)),
                ('nickname', models.CharField(max_length=150, null=True, blank=True)),
                ('excerpt', models.CharField(max_length=255, null=True, blank=True)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'draft', max_length=15, choices=[(b'public', b'Public'), (b'draft', b'Draft')])),
            ],
            options={
                'verbose_name_plural': 'celebrities',
            },
        ),
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=75)),
                ('filter_type', models.CharField(max_length=75, choices=[(b'career', b'Career'), (b'social_network', b'Social network')])),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150, null=True, blank=True)),
                ('image', models.ImageField(upload_to=b'photo')),
                ('celebrity', models.ForeignKey(to='heaps_app.Celebrity')),
            ],
            options={
                'verbose_name_plural': 'photo',
            },
        ),
        migrations.CreateModel(
            name='SocialNetwork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('social_network', models.CharField(max_length=75, choices=[(b'facebook', b'Facebook'), (b'vk', b'vk'), (b'instagram', b'Instagram')])),
                ('url', models.URLField()),
                ('celebrity', models.ForeignKey(to='heaps_app.Celebrity')),
            ],
            options={
                'verbose_name_plural': 'social networks',
            },
        ),
        migrations.AddField(
            model_name='celebrity',
            name='filter',
            field=models.ManyToManyField(to='heaps_app.Filter'),
        ),
    ]
