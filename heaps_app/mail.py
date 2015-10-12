# coding: utf8
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

REGISTER_NOTIFICATION_TEMPLATE = u"""
Добро пожаловать на Heaps.me
Данные для доступа к Вашему аккаунту:
Email: {0}
Password: {1}
"""


def send_validation(strategy, backend, code):
    url = '{0}?verification_code={1}'.format(
        reverse('social:complete', args=(backend.name,)),
        code.code
    )
    url = strategy.request.build_absolute_uri(url)
    send_mail('Validate your account', 'Validate your account {0}'.format(url),
              settings.EMAIL_FROM, [code.email], fail_silently=False)


def register_notification(email, password):
    send_mail('Welcome to Heaps.me', REGISTER_NOTIFICATION_TEMPLATE.format(email, password),
              settings.EMAIL_FROM, [email])
