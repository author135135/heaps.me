from heaps_app import forms
from heaps_app import models


def heaps_context_data(request):
    context = dict()

    # Get search form
    if 'query' in request.GET and request.GET['query'].strip():
        context['search_form'] = forms.SearchForm(request.GET['query'])
    else:
        context['search_form'] = forms.SearchForm()

    # Get filter form and current filter tags
    context['current_tags'] = []

    if 'filter_tags' in request.GET and request.GET['filter_tags']:
        filter_tags = request.GET['filter_tags'].split(',')

        context['filter_form'] = forms.FilterForm({
            'filter_tags': filter_tags
        })

        context['current_tags'] = models.Filter.objects.filter(pk__in=filter_tags)
    else:
        context['filter_form'] = forms.FilterForm()

    return context
