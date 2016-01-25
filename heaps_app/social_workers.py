from __future__ import unicode_literals
import requests
import re
import oauth2
import urllib
import json
from dateutil.parser import parse
from datetime import datetime
from django.utils.dateformat import format
from heaps import settings


class TwitterWorker(object):
    tweets_data_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    tweets_paginate_by = 5

    def __init__(self, user_id):
        self.user_id = user_id

        consumer = oauth2.Consumer(key=settings.SOCIAL_AUTH_TWITTER_KEY, secret=settings.SOCIAL_AUTH_TWITTER_SECRET)
        token = oauth2.Token(key=settings.TWITTER_ACCESS_TOKEN, secret=settings.TWITTER_ACCESS_TOKEN_SECRET)

        self.client = oauth2.Client(consumer, token, disable_ssl_certificate_validation=True)

    def get_posts(self, page=None):
        tweets_data = {
            'data': [],
            'has_next': False,
            'next_page_id': None,
        }

        request_tweets_params = {
            # 'count': self.tweets_paginate_by + 1, Now it not work, possibly Twitter API errors
            'include_rts': 1,
            'screen_name': self.user_id,
        }

        if page:
            request_tweets_params.update({'max_id': page})

        request_tweets_url = '{}?{}'.format(self.tweets_data_url, urllib.urlencode(request_tweets_params))

        response_headers, response_data = self.client.request(request_tweets_url, 'GET')

        if response_headers['status'] == '200':
            response_data = json.loads(response_data)
        else:
            return tweets_data

        if len(response_data) > self.tweets_paginate_by:
            response_data = response_data[:self.tweets_paginate_by + 1]
            last_tweet = response_data.pop()
            tweets_data['has_next'] = True
            tweets_data['next_page_id'] = last_tweet['id_str']

        for tweet in response_data:
            tweets_data['data'].append(self._build_post(tweet))

        return tweets_data

    def _build_post(self, data):
        post = dict()

        post_id = int(data['id_str'])

        # Check if retweeted
        post['retweeted_status'] = None

        if 'retweeted_status' in data:
            post['retweeted_status'] = self._build_post(data['retweeted_status'])

        # Check quote status
        post['quoted_status'] = None

        if 'quoted_status' in data:
            post['quoted_status'] = self._build_post(data['quoted_status'])

        post['avatar'] = data['user']['profile_image_url']
        post['name'] = data['user']['name']
        post['screen_name'] = data['user']['screen_name']
        post['link'] = 'https://twitter.com/{}/status/{}'.format(self.user_id, post_id)
        post['created_time'] = parse(data['created_at'])

        # Create link in tweet text
        tweet_text = data['text']

        for url_info in data['entities']['urls']:
            tweet_text = tweet_text.replace(url_info['url'],
                                            '<a href="{}">{}</a>'.format(url_info['url'], url_info['display_url']))

        post['text'] = tweet_text

        post['media_type'] = None

        # Handle additional content in tweet
        if 'extended_entities' in data:
            entities_type = data['extended_entities']['media'][0]['type']
            post['media_type'] = entities_type

            if entities_type == 'photo':
                post['photo'] = data['extended_entities']['media'][0]['media_url']
            elif entities_type == 'video' or entities_type == 'animated_gif':
                post['photo'] = data['extended_entities']['media'][0]['media_url']
                post['video'] = None

                for variant in data['extended_entities']['media'][0]['video_info']['variants']:
                    if variant['content_type'] == 'video/webm':
                        post['video'] = variant['url']
                        break

                if post['video'] is None:
                    post['video'] = data['extended_entities']['media'][0]['video_info']['variants'][0]['url']

        return post


class FacebookWorker(object):
    access_token_url = 'https://graph.facebook.com/oauth/access_token'
    media_data_url = 'https://graph.facebook.com/v2.2/{}'
    posts_data_url = 'https://graph.facebook.com/v2.2/{}/posts'
    access_token = None
    posts_paginate_by = 5

    def __init__(self, user_id):
        response = requests.request(
            'GET',
            self.access_token_url,
            params={
                'client_id': settings.SOCIAL_AUTH_FACEBOOK_KEY,
                'client_secret': settings.SOCIAL_AUTH_FACEBOOK_SECRET,
                'grant_type': 'client_credentials',
                'redirect_uri': settings.FACEBOOK_REDIRECT_URI,
            },
            verify=False
        )

        if response.status_code != 200:
            raise requests.HTTPError('Invalid client credentials')

        self.access_token = response.content.split('=')[1]
        self.user_id = user_id

    def get_posts(self, page=None):
        posts_data = {
            'data': [],
            'has_next': False,
            'next_page_id': None,
        }

        request_posts_url = self.posts_data_url.format(self.user_id)
        request_posts_params = {
            'access_token': self.access_token,
            'limit': self.posts_paginate_by + 1,  # + 1 fix for pagination on posts
            'fields': """id,from{name,picture},type,message,picture,full_picture,link,source,name,description,caption,
                         object_id,                      created_time""",
        }

        if page:
            page = int(page)
            request_posts_params.update({'offset': self.posts_paginate_by * page})

        response_data = requests.request('GET', request_posts_url, params=request_posts_params, verify=False).json()

        response_posts = response_data['data']

        if len(response_posts) > self.posts_paginate_by:
            response_posts.pop()
            posts_data['has_next'] = True
            posts_data['next_page_id'] = page + 1 if page else 1

        for post in response_posts:
            clear_post = self._build_post(post)

            if clear_post:
                posts_data['data'].append(clear_post)

        return posts_data

    def _build_post(self, data):
        post = dict()

        # Get all post data
        post['id'] = data.pop('id')
        post['avatar'] = data['from']['picture']['data']['url']
        post['publisher'] = data.pop('from')['name']
        post['post_link'] = 'https://facebook.com/{}/posts/{}'.format(self.user_id, post['id'].split('_')[1])
        post['created_time'] = parse(data.pop('created_time'))

        post_type = data['type']
        object_id = data.pop('object_id', None)

        # Handle additional content in post
        if post_type == 'video':
            source = None

            # Build valid video url for iframe
            if object_id:
                source = 'https://www.facebook.com/video/embed?video_id={}'.format(object_id)
            else:
                video_hosts = [
                    {
                        'pattern': re.compile('^https://www\.facebook\.com/[\w\.]+/videos/([0-9]+)/$'),
                        'url': 'https://www.facebook.com/video/embed?video_id={}',
                    },
                    {
                        'pattern': re.compile('^https?://video\.rutube\.ru/([0-9]+)$'),
                        'url': '//rutube.ru/play/embed/{}',
                    },
                ]

                for video_host in video_hosts:
                    for url in [data['link'], data['source']]:
                        result = video_host['pattern'].match(url)

                        if result is not None:
                            source = video_host['url'].format(result.group(1))
                            break

            if source:
                data['source'] = source

                if 'www.facebook.com' in source:
                    data['picture'] = None

        elif post_type == 'photo':
            data['picture'] = data.get('full_picture')

        post.update(data)

        return post


class InstagramTestWorker(object):
    access_token_url = 'https://www.instagram.com/oauth/authorize'
    users_search_url = 'https://api.instagram.com/v1/users/search'
    users_media_url = 'https://api.instagram.com/v1/users/{}/media/recent'
    media_data_url = 'https://api.instagram.com/v1/media/{}'
    medial_comments_url = 'https://api.instagram.com/v1/media/{}/comments'
    media_paginate_by = 12

    def __init__(self, user_id):
        self.user_id = user_id
        self.client_id = settings.SOCIAL_AUTH_INSTAGRAM_KEY

    def get_posts(self, page=None):
        # Search Instagram user id
        request_params = {
            'client_id': self.client_id,
            'q': self.user_id,
        }

        response_data = requests.request('GET', self.users_search_url, params=request_params).json()

        if not response_data['data']:
            raise requests.HTTPError('User not fount')

        for user_data in response_data['data']:
            if user_data['username'] == self.user_id:
                instagram_user_id = user_data['id']
                break
        else:
            raise requests.HTTPError('User not fount')


        media_data = {
            'data': [],
            'has_next': False,
            'next_page_id': None,
        }

        # Get user media
        request_params = {
            'client_id': self.client_id,
            'count': self.media_paginate_by,
        }

        if page:
            request_params.update({'max_id': page})

        response_data = requests.request(
            'GET',
            self.users_media_url.format(instagram_user_id),
            params=request_params
        ).json()

        if response_data['pagination']:
            media_data['has_next'] = True
            media_data['next_page_id'] = response_data['pagination']['next_max_id']

        for media in response_data['data']:
            media_data['data'].append(self._build_post(media))

        return media_data

    def get_popup_content(self, post_id):
        response_data = requests.request('GET', self.media_data_url.format(post_id), params={
            'client_id': self.client_id
        }).json()

        response_data = response_data['data']

        post = dict()

        post['id'] = response_data['id']
        post['avatar'] = response_data['user']['profile_picture']
        post['publisher'] = response_data['user']['username']
        post['link'] = response_data['link']
        post['picture'] = response_data['images']['standard_resolution']['url']
        post['type'] = response_data['type']

        if post['type'] == 'video':
            post['video'] = response_data['videos']['standard_resolution']['url']

        post['likes_count'] = self._format_counters(response_data['likes']['count'])
        
        # Create formated date in current locale
        post['created_time'] = format(datetime.fromtimestamp(int(response_data['created_time'])), 'j E')

        post['caption'] = {
            'user': response_data['caption']['from']['username'],
            'text': response_data['caption']['text'],
        }

        post['comments'] = []
        comments = response_data['comments']['data']

        # Get all comments if more then 8
        if response_data['comments']['count'] > 8:
            response_data = requests.request('GET', self.medial_comments_url.format(response_data['id']), params={
                'client_id': self.client_id
            }).json()

            comments = response_data['data']

        for comment in comments:
            post['comments'].append({
                'id': comment['id'],
                'user': comment['from']['username'],
                'text': comment['text'],
            })

        return post

    def _build_post(self, data):
        post = dict()

        post['id'] = data['id']
        post['avatar'] = data['user']['profile_picture']
        post['picture'] = data['images']['low_resolution']['url']
        post['type'] = data['type']

        post['likes_count'] = self._format_counters(data['likes']['count'])
        post['comments_count'] = self._format_counters(data['comments']['count'])

        return post

    def _format_counters(self, num):
        """
        Create string counter in instagram format
        """
        result = ''

        if num > 9999:
            num_parts = '{0:,}'.format(num).split(',')
            num_parts_len = len(num_parts)
            result = num_parts[0]

            if (num_parts_len > 1 and len(num_parts[0]) < 3) and not num_parts[1].startswith('0'):
                result += '.{}'.format(num_parts[1][0])


            if 1 < num_parts_len < 3:
                result += 'k'
            elif num_parts_len >= 3:
                result += 'm'
        else:
            result = '{0:,}'.format(num)

        return result