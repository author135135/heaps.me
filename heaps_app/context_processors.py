from django.conf import settings
from heaps_app import forms
from heaps_app import models


def heaps_context_data(request):
    context = dict()

    # Get search form
    context['search_form'] = forms.SearchForm(request.GET)

    # Get filter form and current filter tags
    context['current_tags'] = []

    current_tags_pk = request.GET.getlist('filter_tag', None)
    filter_tags = list(models.Filter.objects.all())

    context['filter_tags_career'] = [item for item in filter_tags if item.filter_type == 'career']
    context['filter_tags_social_network'] = [item for item in filter_tags if item.filter_type == 'social_network']

    if current_tags_pk:
        current_tags_pk = [int(item) for item in current_tags_pk]
        context['current_tags'] = [item for item in filter_tags if item.id in current_tags_pk]

    # Login and Register forms
    if not request.user.is_authenticated():
        context['login_form'] = forms.LoginForm()
        context['registration_form'] = forms.RegistrationForm()
        context['password_forgotten_form'] = forms.PasswordForgottenForm()

        # OAuth Google+ required settings
        context['google_plus_key'] = getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None)
        context['google_plus_scope'] = ' '.join(getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_SCOPE', []))

    return context
