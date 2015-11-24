from django.views.generic import ListView, CreateView, DetailView, UpdateView, FormView
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from django.db.models import Q
from django.template.loader import get_template
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from heaps_app import models, forms, mail
from django.utils.translation import ugettext, ugettext_lazy as _


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
                    Q(firstname__icontains=query) | Q(lastname__icontains=query) | Q(nickname__icontains=query)
                )
            else:
                qs = qs.none()

        return qs


class CelebritiesPaginatedAjaxMixin(object):
    celebrities_template = 'heaps_app/_celebrities_block.html'

    def get(self, request, *args, **kwargs):
        result = super(CelebritiesPaginatedAjaxMixin, self).get(request, *args, **kwargs)

        if request.is_ajax():
            celebrities_template = get_template(self.celebrities_template)

            return JsonResponse({
                'celebrities': celebrities_template.render({'celebrities': result.context_data['celebrities']}),
                'paginate_has_next': result.context_data['page_obj'].has_next(),
            })
        return result


class FormResponseMixin(object):
    def form_valid(self, form):
        response = super(FormResponseMixin, self).form_valid(form)

        if self.request.is_ajax():
            data = {
                'success': True,
                'message': self.success_message,
            }

            return JsonResponse(data)
        else:
            return response

    def form_invalid(self, form):
        response = super(FormResponseMixin, self).form_invalid(form)

        if self.request.is_ajax():
            data = {'errors': form.errors}

            return JsonResponse(data)
        else:
            return response


class IndexView(CelebritiesPaginatedAjaxMixin, ListView):
    template_name = 'heaps_app/index.html'
    queryset = models.Celebrity.public_records.get_queryset()
    context_object_name = 'celebrities'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        if 'partial_pipeline' in self.request.session:
            context['backend'] = self.request.session['partial_pipeline']['backend']
            context['email_verification_form'] = forms.EmailVerificationForm()

        if 'validation_sent' in self.request.GET:
            email_validation_address = self.request.session.get('email_validation_address')

            context['validation_sent'] = True
            context['message'] = _(
                'An email validation was sent to {0}. Click the link sent to finish the authentication process.'
            ).format(email_validation_address)

        return context


class SearchView(CelebritiesFilterMixin, CelebritiesPaginatedAjaxMixin, ListView):
    template_name = 'heaps_app/index.html'
    queryset = models.Celebrity.public_records.get_queryset()
    context_object_name = 'celebrities'
    paginate_by = 12


class CelebrityView(CelebritiesPaginatedAjaxMixin, DetailView):
    template_name = 'heaps_app/celebrity_view.html'
    context_object_name = 'celebrity'
    queryset = models.Celebrity.public_records.get_queryset()

    def get_context_data(self, **kwargs):
        context = super(CelebrityView, self).get_context_data(**kwargs)

        # Update object stat
        self.object.update_stat(self.request)

        related_celebrities = models.Celebrity.public_records.filter(
            filter__pk__in=self.object.filter.all()).distinct().exclude(pk=self.object.pk)

        paginator = Paginator(related_celebrities, 12)
        page_obj = paginator.page(self.request.GET.get('page', 1))

        context['celebrities'] = page_obj.object_list
        context['page_obj'] = page_obj

        return context


class AccountCelebrityAddView(FormResponseMixin, CreateView):
    template_name = 'heaps_app/account_celebrity_add.html'
    form_class = forms.CelebrityAddForm
    success_message = ugettext('Celebrity record add.')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AccountCelebrityAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('heaps_app:account-celebrity-add')


class AccountMySubscribes(CelebritiesPaginatedAjaxMixin, ListView):
    template_name = 'heaps_app/account_my_subscribes.html'
    model = models.Celebrity
    context_object_name = 'celebrities'
    paginate_by = 6

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AccountMySubscribes, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return models.Celebrity.public_records.filter(pk__in=self.request.user.get_my_subscribes())


class AccountSettings(FormResponseMixin, UpdateView):
    template_name = 'heaps_app/account_settings.html'
    form_class = forms.AccountSettingsForm
    success_message = ugettext('Account settings updated')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AccountSettings, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super(AccountSettings, self).form_valid(form)
        if form.cleaned_data['password'] and form.cleaned_data['password_repeat']:
            email = self.request.user.email
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)

            login(self.request, user)

        return response

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('heaps_app:account-settings')


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
                response_data['redirect_to'] = request.META['HTTP_REFERER']
            else:
                response_data['authenticated'] = False
                response_data['errors'] = {
                    'all': [ugettext('Invalid email or password.')]
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
                response_data['redirect_to'] = request.META['HTTP_REFERER']
        else:
            response_data['authenticated'] = False
            response_data['errors'] = form.errors

        return JsonResponse(response_data)

    return HttpResponseForbidden("Access denied")


def account_forgotten_password(request):
    if request.is_ajax() and request.method == 'POST':
        form = forms.PasswordForgottenForm(request.POST)
        response_data = dict()

        if form.is_valid():
            user = models.User.objects.get(email=form.cleaned_data['email'])
            password = models.User.objects.make_random_password()

            user.set_password(password)
            user.save()

            mail.forgotten_password(form.cleaned_data['email'], password)

            response_data['success'] = True
            response_data['message'] = ugettext('To your email has been sent a letter with the recovery password.')
        else:
            response_data['success'] = False
            response_data['errors'] = form.errors

        return JsonResponse(response_data)

    return HttpResponseForbidden("Access denied")


@login_required
def account_logout(request):
    logout(request)

    return redirect(reverse('heaps_app:index'))


@login_required
def celebrity_subscribe(request, slug):
    try:
        celebrity = models.Celebrity.public_records.get(slug=slug)
    except models.Celebrity.DoesNotExist:
        return HttpResponseNotFound()

    if celebrity in request.user.celebrity_subscribe.all():
        request.user.celebrity_subscribe.remove(celebrity)
    else:
        request.user.celebrity_subscribe.add(celebrity)

    return redirect(reverse('heaps_app:celebrity-view', kwargs={'slug': slug}))
