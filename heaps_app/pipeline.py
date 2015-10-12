from django.shortcuts import redirect
from social.pipeline.partial import partial


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new:
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
        else:
            return redirect('/?modal=email-required')
