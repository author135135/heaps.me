from heaps_app import forms
from heaps_app import models


def heaps_context_data(request):
    context = dict()

    # Get search form
    context['search_form'] = forms.SearchForm(request.GET)

    # Get filter form and current filter tags
    context['current_tags'] = []

    filter_tags = request.GET.get('filter_tags', '')

    if filter_tags:
        filter_tags = filter_tags.split(',')

        context['filter_form'] = forms.FilterForm({
            'filter_tags': filter_tags
        })

        context['current_tags'] = models.Filter.objects.filter(pk__in=filter_tags)
    else:
        context['filter_form'] = forms.FilterForm()

    # Login and Register forms
    if not request.user.is_authenticated():
        context['login_form'] = forms.LoginForm()
        context['registration_form'] = forms.RegistrationForm()

    return context
