import requests
import re
from dateutil.parser import parse
from heaps import settings


class FacebookWorker(object):
    access_token_url = 'https://graph.facebook.com/oauth/access_token'
    access_token = None

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

        # self.paging = False
        self.access_token = response.content.split('=')[1]
        self.user_id = user_id
        self.request_media_data_url = 'https://graph.facebook.com/v2.2/{}'
        self.request_posts_url = 'https://graph.facebook.com/v2.2/{user_id}/posts'.format(user_id=self.user_id)
        self.request_posts_params = {
            'access_token': self.access_token,
            'limit': 100,
            'fields': 'id,from,type,message,picture,link,source,name,description,caption,object_id,created_time',
        }

        user_info_data = requests.request(
            'GET',
            'https://graph.facebook.com/v2.2/{user_id}'.format(user_id=user_id),
            params={'access_token': self.access_token, 'fields': ','.join(['picture'])}
        ).json()

        self.picture = user_info_data['picture']['data']['url']

    def get_posts(self):
        posts = list()

        response_data = requests.request('GET', self.request_posts_url, params=self.request_posts_params).json()

        response_posts = response_data['data']

        for post in response_posts:
            clear_post = self._build_post(post)

            if clear_post:
                posts.append(clear_post)

        return posts

    def _build_post(self, data):
        post = dict()

        # Get all post data
        post['post_id'] = data.pop('id')
        post['post_avatar'] = self.picture
        post['post_publisher'] = data.pop('from')['name']
        post['post_link'] = 'https://facebook.com/{}/posts/{}'.format(self.user_id, post['post_id'].split('_')[1])
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
                self.request_media_data_url.format(object_id),
                params={'access_token': self.access_token, 'fields': 'source'}
            ).json()

            data['picture'] = photo_data.get('source', data['picture'])

        post.update(data)

        return post
