import requests
import re
import oauth2
import urllib
from json import JSONDecoder
from dateutil.parser import parse
from heaps import settings


class TwitterProcessWorker(object):
    tweets_data_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    tweets_paginated_by = 7

    def __init__(self, user_id):
        self.user_id = user_id

        consumer = oauth2.Consumer(key=settings.SOCIAL_AUTH_TWITTER_KEY, secret=settings.SOCIAL_AUTH_TWITTER_SECRET)
        token = oauth2.Token(key=settings.TWITTER_ACCESS_TOKEN, secret=settings.TWITTER_ACCESS_TOKEN_SECRET)

        self.client = oauth2.Client(consumer, token)

    def get_posts(self, last_id=None):
        tweets_data = {
            'posts': [],
            'has_next': False,
        }

        request_tweets_params = {
            'count': self.tweets_paginated_by,
            'include_rts': 1,
            'screen_name': self.user_id,
        }

        if last_id:
            request_tweets_params.update({'max_id': last_id - 1})

        request_tweets_url = '{}?{}'.format(self.tweets_data_url, urllib.urlencode(request_tweets_params))

        response_headers, response_data = self.client.request(request_tweets_url, 'GET')

        if response_headers['status'] == '200':
            response_data = JSONDecoder().decode(response_data)
        else:
            return tweets_data

        for tweet in response_data:
            tweets_data['posts'].append(self._build_post(tweet))

        return tweets_data

    def _build_post(self, data):
        post = dict()

        post['id'] = int(data['id_str'])
        post['avatar'] = data['user']['profile_image_url']
        post['publisher'] = data['user']['name']
        # post['post_link'] = '' ???????????????
        post['created_time'] = parse(data['created_at'])

        # Create link in tweet text
        tweet_text = data['text']

        for url_info in data['entities']['urls']:
            tweet_text.replace(url_info['url'], '<a href="{}">{}</a>'.format(url_info['url'], url_info['display_url']))

        post['text'] = tweet_text

        # Handle additional content in tweet
        if 'extended_entities' in data:
            entities_type = data['extended_entities']['media'][0]['type']
            post['media_type'] = entities_type

            if entities_type == 'photo':
                post['photo'] = data['extended_entities']['media'][0]['media_url']
            elif entities_type == 'video':
                post['photo'] = data['extended_entities']['media'][0]['media_url']
                post['video'] = data['extended_entities']['media'][0]['video_info']['variants'].pop()['url']

        return post


class FacebookWorker(object):
    access_token_url = 'https://graph.facebook.com/oauth/access_token'
    media_data_url = 'https://graph.facebook.com/v2.2/{}'
    posts_data_url = 'https://graph.facebook.com/v2.2/{}/posts'
    access_token = None
    posts_paginate_by = 5

    def __init__(self, user_id):
        response = requests.request(
            'GET', self.access_token_url,
            params={
                'client_id': settings.SOCIAL_AUTH_FACEBOOK_KEY,
                'client_secret': settings.SOCIAL_AUTH_FACEBOOK_SECRET,
                'grant_type': 'client_credentials',
                'redirect_uri': settings.FACEBOOK_REDIRECT_URI,
            }
        )

        if response.status_code != 200:
            raise requests.HTTPError('Invalid client credentials')

        user_info_data = requests.request(
            'GET',
            'https://graph.facebook.com/v2.2/{user_id}'.format(user_id=user_id),
            params={'access_token': self.access_token, 'fields': ','.join(['picture'])}
        ).json()

        self.picture = user_info_data['picture']['data']['url']
        self.access_token = response.content.split('=')[1]
        self.user_id = user_id

    def get_posts(self, page=None):
        posts_data = {
            'posts': [],
            'has_next': False,
        }

        request_posts_url = self.posts_data_url.format(self.user_id)
        request_posts_params = {
            'access_token': self.access_token,
            'limit': self.posts_paginate_by + 1,    # + 1 fix for pagination on posts
            'fields': 'id,from,type,message,picture,link,source,name,description,caption,object_id,created_time',
        }

        if page:
            request_posts_params.update({'offset': self.posts_paginate_by * page})

        response_data = requests.request('GET', request_posts_url, params=request_posts_params).json()

        response_posts = response_data['data']

        if len(response_posts) > self.posts_paginate_by:
            response_posts.pop()
            posts_data['has_next'] = True

        for post in response_posts:
            clear_post = self._build_post(post)

            if clear_post:
                posts_data['posts'].append(clear_post)

        return posts_data

    def _build_post(self, data):
        post = dict()

        # Get all post data
        post['id'] = data.pop('id')
        post['avatar'] = self.picture
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
            photo_data = requests.request(
                'GET',
                self.media_data_url.format(object_id),
                params={'access_token': self.access_token, 'fields': 'source'}
            ).json()

            data['picture'] = photo_data.get('source', data['picture'])

        post.update(data)

        return post
