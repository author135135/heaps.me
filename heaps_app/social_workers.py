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


# Request helpers
class RequestsWrapper(object):
    def make_request(self, method, url, *args, **kwargs):
        result = None

        # Change some default params
        kwargs.update(kwargs.get('verify', {'verify': False}))

        # Make request
        response = requests.request(method, url, *args, **kwargs)
        response.raise_for_status()

        try:
            result = response.json()
        except ValueError:
            result = response

        return result


class Oauth2Wrapper(object):
    def make_request(self, client, method, url, *args, **kwargs):
        if not isinstance(client, oauth2.Client):
            raise ValueError('Invalid client instance')

        response_headers, response_data = client.request(url, method, *args, **kwargs)

        response_data = json.loads(response_data)

        if response_headers['status'] != 200 and 'errors' in response_data:
            raise requests.HTTPError('. '.join(map(lambda error: error['message'], response_data['errors'])))

        return response_data


# Workers
class TwitterWorker(Oauth2Wrapper):
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

        response_data = self.make_request(self.client, 'GET', request_tweets_url)

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


class FacebookWorker(RequestsWrapper):
    media_data_url = 'https://graph.facebook.com/v2.2/{}'
    posts_data_url = 'https://graph.facebook.com/v2.2/{}/posts'
    posts_paginate_by = 5

    def __init__(self, user_id):
        self.user_id = user_id
        self.client_id = settings.SOCIAL_AUTH_FACEBOOK_KEY
        self.client_secret = settings.SOCIAL_AUTH_FACEBOOK_SECRET

    def get_posts(self, page=None):
        posts_data = {
            'data': [],
            'has_next': False,
            'next_page_id': None,
        }

        request_posts_url = self.posts_data_url.format(self.user_id)
        request_posts_params = {
            'access_token': '{}|{}'.format(self.client_id, self.client_secret),
            'limit': self.posts_paginate_by + 1,  # + 1 fix for pagination on posts
            'fields': """id,from{name,picture},type,message,full_picture,link,source,name,description,caption,object_id,
                      created_time""",
        }

        if page:
            page = int(page)
            request_posts_params.update({'offset': self.posts_paginate_by * page})

        response_data = self.make_request('GET', request_posts_url, params=request_posts_params)

        response_posts = response_data['data']

        if len(response_posts) > self.posts_paginate_by:
            response_posts.pop()
            posts_data['has_next'] = True
            posts_data['next_page_id'] = page + 1 if page else 1

        for post in response_posts:
            posts_data['data'].append(self._build_post(post))

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


# Now it's not working
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


class SoundcloudWorker(RequestsWrapper):
    soundclound_url = 'https://soundcloud.com/'
    api_url = 'http://api.soundcloud.com/'

    def __init__(self, user_id):
        self.user_id = user_id

    def get_posts(self, *args, **kwargs):
        posts = {
            'data': [],
            'has_next': False,
            'next_page_id': None,
        }

        posts['data'].append(self._get_oembed_content())

        return posts

    def _get_oembed_content(self):
        post = dict()

        response_data = self.make_request('GET', self.soundclound_url + 'oembed', params={
            'format': 'json',
            'color': '#FF5510',
            'url': self.soundclound_url + self.user_id
        })

        post['avatar'] = response_data['thumbnail_url']
        post['publisher'] = response_data['author_name']
        post['player_url'] = 'https://w.soundcloud.com/player/?{}'.format(urllib.urlencode({
            'visual': 'false',
            'url': self.soundclound_url + self.user_id
        }))

        return post


class YoutubeWorker(RequestsWrapper):
    video_paginate_by = 5

    def __init__(self, user):
        self.user = user
        self.user_info = {}
        self.key = settings.GOOGLE_API_SERVER_KEY

    def get_posts(self, page=None):
        posts_data = {
            'data': [],
            'has_next': False,
            'next_page_id': None,
        }

        # Try to get user channel info
        response = self.make_request('GET', 'https://www.googleapis.com/youtube/v3/channels', params={
            'key': self.key,
            'part': 'contentDetails',
            'forUsername': self.user,
            'maxResults': 1,
            'fields': 'items',
        })

        if not len(response['items']):
            return posts_data

        playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        google_plus_id = response['items'][0]['contentDetails']['googlePlusUserId']

        # Get user info from Google Plus
        self.user_info = self.make_request('GET', 'https://www.googleapis.com/plus/v1/people/{}'.format(google_plus_id),
                                           params={'key': self.key})

        # Get channel video items
        playlist_items_params = {
            'key': self.key,
            'part': 'snippet',
            'maxResults': self.video_paginate_by,
            'playlistId': playlist_id
        }

        if page:
            playlist_items_params.update({'pageToken': page})

        response = self.make_request('GET', 'https://www.googleapis.com/youtube/v3/playlistItems',
                                     params=playlist_items_params)

        if response['nextPageToken']:
            posts_data['has_next'] = True
            posts_data['next_page_id'] = response['nextPageToken']

        for post in response['items']:
            posts_data['data'].append(self._build_post(post))

        return posts_data

    def _build_post(self, data):
        post = dict()

        post['avatar'] = self.user_info['image']['url']
        post['publisher'] = self.user_info['displayName']
        post['video_url'] = 'https://www.youtube.com/watch?v={}'.format(data['snippet']['resourceId']['videoId'])
        post['created_time'] = parse(data['snippet']['publishedAt'])

        post['title'] = data['snippet']['title']
        post['description'] = data['snippet']['description']

        if 'maxres' in data['snippet']['thumbnails']:
            post['thumb'] = data['snippet']['thumbnails']['maxres']['url']
        elif 'standart' in data['snippet']['thumbnails']:
            post['thumb'] = data['snippet']['thumbnails']['standard']['url']
        else:
            post['thumb'] = data['snippet']['thumbnails']['high']['url']

        post['video_src'] = 'https://www.youtube.com/embed/{}'.format(data['snippet']['resourceId']['videoId'])

        return post
