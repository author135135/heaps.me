import requests
import os
from django.shortcuts import redirect
from social.pipeline.partial import partial
from django.core.files.uploadedfile import SimpleUploadedFile


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new:
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
        else:
            return redirect('/?modal=email-verification')


def save_user_photo(strategy, backend, response, details, user=None, is_new=False, *args, **kwargs):
    if is_new:
        user_photo_url = None

        if backend.name == 'vk-oauth2':
            user_photo_url = response.get('photo_200')
        elif backend.name == 'twitter':
            user_photo_url = response.get('profile_image_url')

            if user_photo_url:
                user_photo_url = user_photo_url.replace('_normal', '_bigger')
        elif backend.name == 'facebook':
            user_photo_url = 'http://graph.facebook.com/{0}/picture?type=large'.format(response['id'])
        elif backend.name == 'google-plus':
            user_photo_url = response['image'].get('url')

            if user_photo_url:
                user_photo_url = user_photo_url.replace('sz=50', 'sz=200')
        elif backend.name == 'instagram':
            user_photo_url = response['data'].get('profile_picture')

        if user_photo_url:
            try:
                response = requests.get(user_photo_url)
                response.raise_for_status()
            except requests.HTTPError:
                return False

            filename = os.path.basename(user_photo_url)
            file_content = response.content

            avatar = SimpleUploadedFile(filename, file_content)

            user.avatar = avatar

            user.save()
