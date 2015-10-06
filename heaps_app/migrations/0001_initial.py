# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import heaps_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('avatar', models.ImageField(null=True, upload_to=b'avatars/%Y/%m/%d', blank=True)),
                ('first_name', models.CharField(max_length=50, blank=True)),
                ('last_name', models.CharField(max_length=50, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
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
                ('slug', models.SlugField(null=True)),
                ('excerpt', models.CharField(max_length=255, null=True, blank=True)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'draft', max_length=15, choices=[(b'public', b'Public'), (b'draft', b'Draft')])),
            ],
            options={
                'ordering': ('-created_at',),
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
                ('image', models.ImageField(upload_to=heaps_app.models.rename_file)),
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
                ('social_network', models.CharField(max_length=75, choices=[(b'facebook', b'Facebook'), (b'vk', b'Vk'), (b'instagram', b'Instagram')])),
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
            field=models.ManyToManyField(to='heaps_app.Filter', blank=True),
        ),
    ]
