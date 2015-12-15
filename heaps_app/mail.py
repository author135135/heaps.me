from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

EMAIL_VALIDATION_TEMPLATE = _('Validate your account {0}')

REGISTER_NOTIFICATION_TEMPLATE = _("""
Welcome to HeapsMe
Your account settings:
Email: {0}
Password: {1}
""")

FORGOTTEN_PASSWORD_TEMPLATE = _("""
Your password have been reset.
You can change it in the settings of your account.
New password for your account: {0}
""")

ACCOUNT_CHANGE_EMAIL_TEMPLATE = _("""
You have applied to address mapping {0} to your page on the website HeapsMe.
If you did not, please ignore this letter.

To complete the binding , click here:

{1}
""")


def email_validation(strategy, backend, code):
    url = '{0}?verification_code={1}'.format(
        reverse('social:complete', args=(backend.name,)),
        code.code
    )
    url = strategy.request.build_absolute_uri(url)
    send_mail(_('Validate your account'), EMAIL_VALIDATION_TEMPLATE.format(url),
              settings.EMAIL_FROM, [code.email], fail_silently=False)


def register_notification(email, password):
    send_mail(_('Welcome to HeapsMe'), REGISTER_NOTIFICATION_TEMPLATE.format(email, password),
              settings.EMAIL_FROM, [email])


def forgotten_password(email, password):
    send_mail(_('Reset password'), FORGOTTEN_PASSWORD_TEMPLATE.format(password), settings.EMAIL_FROM, [email])


def account_change_email_notification(email, link_url):
    send_mail(_('Binding E-Mail to the page'), ACCOUNT_CHANGE_EMAIL_TEMPLATE.format(email, link_url),
              settings.EMAIL_FROM, [email])
