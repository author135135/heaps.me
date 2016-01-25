import hashlib
import urllib
from urlparse import urlparse
from django.utils import timezone
from django.core.cache import cache
from django.views.generic import ListView, CreateView, DetailView, TemplateView
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.db.models import Q
from django.template.loader import get_template
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from heaps_app import models, forms, mail, social_workers
from django.utils.translation import ugettext, ugettext_lazy as _


class CelebritiesFilterMixin(object):
    def get_queryset(self):
        qs = super(CelebritiesFilterMixin, self).get_queryset()

        filter_tags = self.request.GET.get('filter_tags', None)

        if filter_tags:
            filter_tags = filter_tags.split(',')
            filter_career = models.Filter.objects.filter(pk__in=filter_tags, filter_type='career')
            filter_social_network = models.Filter.objects.filter(pk__in=filter_tags, filter_type='social_network')

            if filter_career:
                qs = qs.filter(filter__in=filter_career)

            if filter_social_network:
                qs = qs.filter(filter__in=filter_social_network)

            qs = qs.distinct()

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
                'celebrities': celebrities_template.render({
                    'celebrities': result.context_data['celebrities'],
                    'request': request,
                }),
                'paginate_has_next': result.context_data['page_obj'].has_next(),
            })
        return result


class FormResponseMixin(object):
    def form_valid(self, form):
        response = super(FormResponseMixin, self).form_valid(form)

        if self.request.is_ajax():
            return JsonResponse({
                'success': True,
                'message': self.success_message
            })
        else:
            return response

    def form_invalid(self, form):
        response = super(FormResponseMixin, self).form_invalid(form)

        if self.request.is_ajax():
            return JsonResponse({
                'errors': form.errors
            })
        else:
            return response


class IndexView(CelebritiesPaginatedAjaxMixin, ListView):
    template_name = 'heaps_app/index.html'
    queryset = models.Celebrity.public_records.get_queryset()
    context_object_name = 'celebrities'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        if 'partial_pipeline' in self.request.session:
            context['backend'] = self.request.session['partial_pipeline']['backend']
            context['email_verification_form'] = forms.EmailVerificationForm()

        email_validation_address = self.request.session.get('email_validation_address')

        if 'validation_sent' in self.request.GET and email_validation_address:
            context['message'] = _(
                'An email validation was sent to {0}. Click the link sent to finish the authentication process.'
            ).format(email_validation_address)
            context['email_url'] = '//{0}'.format(email_validation_address.split('@')[1])

        return context


class SearchView(CelebritiesFilterMixin, CelebritiesPaginatedAjaxMixin, ListView):
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

        # Update object stat
        self.object.update_stat(self.request)

        related_celebrities = models.Celebrity.public_records.filter(
            filter__pk__in=self.object.filter.all(),
            filter__filter_type='career').distinct().exclude(pk=self.object.pk)

        paginator = Paginator(related_celebrities, 6)
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


class AccountSettings(TemplateView):
    template_name = 'heaps_app/account_settings.html'
    account_settings_info_form = forms.AccountSettingsInfoForm
    account_settings_avatar_form = forms.AccountSettingsAvatarForm

    success_message = ugettext('Account settings updated')
    change_email_message = ugettext(
        'An email validation was sent to {0}. Click the link sent to finish the authentication process.')
    ajax_response_data = {}

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AccountSettings, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AccountSettings, self).get_context_data(**kwargs)

        # Set initial data
        context['settings_info_form'] = self.account_settings_info_form(initial={
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
            'email': self.request.user.email,
        })

        context['settings_avatar_form'] = self.account_settings_avatar_form()

        return context

    def get(self, request, *args, **kwargs):
        # Email actions link handler
        action = request.GET.get('action')
        action_hash = request.GET.get('action_hash')

        if action and action_hash:
            action_info = action in request.session and request.session.pop(action)

            if action_info and action_info.pop('action_hash') == action_hash:
                return getattr(self, '_' + action)(**action_info)

        return super(AccountSettings, self).get(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        form_class = request.POST.get('form_type')
        relogin = False

        if not form_class or not hasattr(self, form_class):
            return HttpResponseForbidden("Access denied")

        form = getattr(self, form_class)(request.POST, request.FILES)

        if form.is_valid():
            user = models.User.objects.get(pk=request.user.pk)

            password = 'password' in form.cleaned_data and form.cleaned_data.pop('password')
            password_repeat = 'password_repeat' in form.cleaned_data and form.cleaned_data.pop('password_repeat')
            email = 'email' in form.cleaned_data and form.cleaned_data.pop('email')

            # Check user change password
            if password and password_repeat:
                user.set_password(password)
                relogin = True

            # Save user model attributes
            for attr, value in form.cleaned_data.iteritems():
                if hasattr(user, attr):
                    setattr(user, attr, value)

            user.save()

            if relogin:
                user_credentials = authenticate(email=user.email, password=password)

                login(request, user_credentials)

            # Check user change email
            if email and email != user.email:
                action_hash = hashlib.sha1(str(user.pk) + str(timezone.now())).hexdigest()
                change_email_url = reverse('heaps_app:account-settings') + '?' + urllib.urlencode({
                    'action': 'account_change_email',
                    'action_hash': action_hash,
                })

                change_email_url = self.request.build_absolute_uri(change_email_url)

                self.request.session['account_change_email'] = {
                    'new_email': email,
                    'action_hash': action_hash
                }

                mail.account_change_email_notification(email, change_email_url)

                self.ajax_response_data = {
                    'message': self.change_email_message.format(email),
                    'modal': True,
                    'email_url': '//' + email.split('@')[1]
                }

            # Set default response data
            if not self.ajax_response_data:
                self.ajax_response_data = {
                    'success': True,
                    'message': self.success_message,
                }
        else:
            self.ajax_response_data = {
                'errors': form.errors,
            }

        if request.is_ajax():
            return JsonResponse(self.ajax_response_data)
        else:
            return redirect(reverse('heaps_app:account-settings'))

    # User data manipulation actions
    def _account_change_email(self, new_email):
        user = models.User.objects.get(pk=self.request.user.pk)

        user.email = new_email
        user.save()

        return redirect(reverse('heaps_app:account-settings'))


def account_login(request):
    if request.is_ajax() and request.method == 'POST':
        form = forms.LoginForm(request.POST)
        response_data = {}

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

    return HttpResponseForbidden('Access denied')


def account_registration(request):
    if request.is_ajax() and request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        response_data = {}

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

    return HttpResponseForbidden('Access denied')


def account_forgotten_password(request):
    if request.is_ajax() and request.method == 'POST':
        form = forms.PasswordForgottenForm(request.POST)
        response_data = {}

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

    return HttpResponseForbidden('Access denied')


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


def social_posts_loader(request, slug):
    if request.method == 'GET' and request.is_ajax():
        response = dict()
        block_has_content = request.GET.get('block_has_content')
        social_network = request.GET.get('social_network')
        page = request.GET.get('page', None)

        try:
            celebrity = models.Celebrity.objects.get(slug=slug)
            social_network = celebrity.socialnetwork_set.get(social_network=social_network)
        except (models.Celebrity.DoesNotExist, models.SocialNetwork.DoesNotExist):
            return HttpResponseNotFound()

        worker_class = '{}Worker'.format(social_network.social_network.capitalize())

        header_template = get_template('heaps_app/social_post_blocks/blocks_header.html')

        if hasattr(social_workers, worker_class):
            url_info = urlparse(social_network.url)
            celebrity_id = url_info.path.strip('/')

            cache_key = 'social_posts_{}_{}'.format(celebrity_id, social_network.social_network)

            if page:
                cache_key += '_{}'.format(page)

            posts_data = cache.get(cache_key)

            if not posts_data:
                worker = getattr(social_workers, worker_class)(celebrity_id)

                posts_data = worker.get_posts(page)
                cache.set(cache_key, posts_data, 1800)

            if posts_data['data']:
                content_template = get_template(
                    'heaps_app/social_post_blocks/{}.html'.format(social_network.social_network)
                )

                if not int(block_has_content):
                    response['header'] = header_template.render({
                        'data': posts_data['data'][0],
                        'social_network': social_network,
                        'has_model': True,
                    })

                response['content'] = content_template.render({
                    'data': posts_data['data']
                })

                response['has_next'] = posts_data['has_next']
                response['next_page_id'] = posts_data['next_page_id']
            else:
                response['header'] = header_template.render({
                    'social_network': social_network,
                    'has_model': False,
                })

                response['content'] = get_template('heaps_app/social_post_blocks/coming-soon.html').render()

        else:
            response['header'] = header_template.render({
                'social_network': social_network,
                'has_model': False,
            })

            response['content'] = get_template('heaps_app/social_post_blocks/coming-soon.html').render()

        return JsonResponse(response)

    return HttpResponseForbidden('Access denied')


def social_posts_actions(request, slug):
    if request.method == 'GET' and request.is_ajax():
        response = dict()
        social_network = request.GET.get('social_network')
        action = request.GET.get('action', None)
        action_params = request.GET.getlist('action_params[]')

        try:
            celebrity = models.Celebrity.objects.get(slug=slug)
            social_network = celebrity.socialnetwork_set.get(social_network=social_network)
        except (models.Celebrity.DoesNotExist, models.SocialNetwork.DoesNotExist):
            return HttpResponseNotFound()

        worker_class = '{}Worker'.format(social_network.social_network.capitalize())

        if not hasattr(social_workers, worker_class):
            return HttpResponseNotFound()

        url_info = urlparse(social_network.url)
        celebrity_id = url_info.path.strip('/')

        worker = getattr(social_workers, worker_class)(celebrity_id)

        if not action or not hasattr(worker, action):
            return HttpResponseNotFound()

        try:
            response['data'] = getattr(worker, action)(*action_params)
            response['status'] = True
        except Exception:
            response['status'] = False

        return JsonResponse(response)

    return HttpResponseForbidden('Access denied')


# Custom server errors handlers
def handler404(request):
    return render(request, 'heaps_app/404.html')
