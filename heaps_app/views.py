from django.views.generic import ListView, CreateView, DetailView
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.db.models import Q
from django.template.loader import get_template
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login, authenticate, logout
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from heaps_app import models, forms


class CelebritiesFilterMixin(object):
    def get_queryset(self):
        qs = super(CelebritiesFilterMixin, self).get_queryset()

        filter_tags = self.request.GET.get('filter_tags', None)

        if filter_tags:
            qs = qs.filter(filter__pk__in=self.request.GET['filter_tags'].split(',')).distinct()

        query = self.request.GET.get('query', None)

        if query:
            if query.strip():
                query = query.strip()
                qs = qs.filter(
                    Q(firstname__icontains=query) | Q(lastname__icontains=query) | Q(nickname__icontains=query))
            else:
                qs = qs.none()

        return qs


class CelebritiesPaginatedAjaxMixin(object):
    def get(self, request, *args, **kwargs):
        result = super(CelebritiesPaginatedAjaxMixin, self).get(request, *args, **kwargs)

        if request.is_ajax():
            celebrities_template = get_template('heaps_app/_celebrities_block.html')

            return JsonResponse({
                'celebrities': celebrities_template.render({'celebrities': result.context_data['celebrities']}),
                'paginate_has_next': result.context_data['page_obj'].has_next(),
            })
        return result


class IndexView(CelebritiesFilterMixin, CelebritiesPaginatedAjaxMixin, ListView):
    template_name = 'heaps_app/index.html'
    queryset = models.Celebrity.public_records.get_queryset()
    context_object_name = 'celebrities'
    paginate_by = 6


class CelebrityView(CelebritiesPaginatedAjaxMixin, DetailView):
    template_name = 'heaps_app/celebrity_view.html'
    context_object_name = 'celebrity'
    queryset = models.Celebrity.public_records.get_queryset()

    def get_context_data(self, **kwargs):
        context = super(CelebrityView, self).get_context_data(**kwargs)

        related_celebrities = models.Celebrity.public_records.filter(filter__pk__in=self.object.filter.all()).exclude(
            pk=self.object.pk)

        paginator = Paginator(related_celebrities, 6)
        page_obj = paginator.page(self.request.GET.get('page', 1))

        context['celebrities'] = page_obj.object_list
        context['page_obj'] = page_obj

        return context


class CelebrityAddView(SuccessMessageMixin, CreateView):
    template_name = 'heaps_app/celebrity_add.html'
    form_class = forms.CelebrityForm
    success_message = 'Celebrity record add.'

    def get_success_url(self):
        return reverse('heaps_app:add-celebrity')


def account_login(request):
    if request.is_ajax() and request.method == 'POST':
        form = forms.LoginForm(request.POST)
        response_data = dict()

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)

            if user is not None and user.is_active:
                login(request, user)

                response_data['authenticated'] = True
                response_data['redirect_to'] = reverse('heaps_app:index')
            else:
                response_data['authenticated'] = False
                response_data['errors'] = {
                    'all': ['Invalid email or password. Try again.']
                }
        else:
            response_data['authenticated'] = False
            response_data['errors'] = form.errors

        return JsonResponse(response_data)

    return HttpResponseForbidden("Access denied")


def account_registration(request):
    if request.is_ajax() and request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        response_data = dict()

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if models.User.objects.create_user(email, password):
                user = authenticate(email=email, password=password)

                login(request, user)

                response_data['authenticated'] = True
                response_data['redirect_to'] = reverse('heaps_app:index')
        else:
            response_data['authenticated'] = False
            response_data['errors'] = form.errors

        return JsonResponse(response_data)

    return HttpResponseForbidden("Access denied")


def account_logout(request):
    if request.user.is_authenticated():
        logout(request)
        return HttpResponseRedirect(reverse('heaps_app:index'))

    return HttpResponseForbidden("Access denied")
