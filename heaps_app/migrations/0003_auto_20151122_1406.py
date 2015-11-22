# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heaps_app', '0002_auto_20151008_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='css_class',
            field=models.CharField(max_length=75, blank=True),
        ),
        migrations.AlterField(
            model_name='socialnetwork',
            name='social_network',
            field=models.CharField(max_length=75, choices=[(b'ask-fm', b'Ask FM'), (b'wikipedia', b'Wikipedia'), (b'vk', b'Vk'), (b'github', b'Github'), (b'plus-google', b'Google +'), (b'livejournal', b'Livejournal'), (b'instagram', b'Instagram'), (b'linkedin', b'Linkedin'), (b'myspace', b'Myspace'), (b'my-mail', b'My world'), (b'ok-ru', b'Odnoklassniki'), (b'promodj', b'Promo Dj'), (b'soundcloud', b'Soundcloud'), (b'twitter', b'Twitter'), (b'twitch', b'Twitch'), (b'facebook', b'Facebook'), (b'youtube', b'Youtube'), (b'official-web', b'Official site')]),
        ),
    ]
