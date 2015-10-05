from django.views.generic import ListView, CreateView
from django.http import JsonResponse
from django.template.loader import get_template
from heaps_app import models, forms


class CelebritiesFilterMixin(object):
    def get_queryset(self):
        qs = super(CelebritiesFilterMixin, self).get_queryset()

        if 'filter_tags' in self.request.GET and self.request.GET['filter_tags']:
            qs = qs.filter(filter__pk__in=self.request.GET['filter_tags'].split(',')).distinct()

        return qs


class IndexView(CelebritiesFilterMixin, ListView):
    template_name = 'heaps_app/index.html'
    model = models.Celebrity
    queryset = models.Celebrity.public_records.get_queryset()
    context_object_name = 'celebrities'
    paginate_by = 6

    def get(self, request, *args, **kwargs):
        result = super(IndexView, self).get(request, *args, **kwargs)

        if request.is_ajax():
            celebrities_template = get_template('heaps_app/_celebrities_block.html')

            return JsonResponse({
                'celebrities': celebrities_template.render({'celebrities': result.context_data['celebrities']}),
                'paginate_has_next': result.context_data['page_obj'].has_next(),
            })
        return result


class AddCelebrityView(CreateView):
    template_name = 'heaps_app/add_celebrity.html'
    form_class = forms.CelebrityForm

    def get_success_url(self):
        from django.core.urlresolvers import reverse

        return reverse('heaps_app:add-celebrity')
