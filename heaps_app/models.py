import os
import hashlib
import random

from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from heaps_app.mail import register_notification


# Custom Managers
class CelebrityManager(models.Manager):
    def get_queryset(self):
        return super(CelebrityManager, self).get_queryset().filter(status='public').prefetch_related(
            'photo_set').prefetch_related('socialnetwork_set')


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, *args, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=UserManager.normalize_email(email))

        if not password:
            password = self.make_random_password()

        user.set_password(password)
        user.save()

        register_notification(user.email, password)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.save()

        return user


# Rewrite User model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d',
                               default='defaults/default_gravatar.png', blank=True,
                               null=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    celebrity_subscribe = models.ManyToManyField('Celebrity')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __unicode__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin

    def get_short_name(self):
        if self.first_name and self.last_name:
            return u'{} {}.'.format(self.first_name, self.last_name[:1])
        return self.email

    def get_full_name(self):
        if self.first_name and self.last_name:
            return u'{} {}'.format(self.last_name, self.first_name)
        return self.email

    def get_social_auth_providers(self):
        if hasattr(self, 'social_auth_providers'):
            return self.social_auth_providers

        providers = self.social_auth.all()
        self.social_auth_providers = []

        provider_classes = {
            'vk-oauth2': 'vk',
            'google-plus': 'plus-google',
        }

        for item in providers:
            self.social_auth_providers.append(provider_classes.get(item.provider, item.provider))
        return self.social_auth_providers


class SeoInformation(models.Model):
    meta_title = models.CharField(max_length=100, blank=True, null=True)
    meta_description = models.CharField(max_length=255, blank=True, null=True)
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True


class Filter(models.Model):
    TAGS_TYPE = (
        ('career', 'Career'),
        ('social_network', 'Social network'),
    )

    title = models.CharField(max_length=75)
    filter_type = models.CharField(max_length=75, choices=TAGS_TYPE)
    css_class = models.CharField(max_length=75)

    def __unicode__(self):
        return self.title


class Celebrity(SeoInformation):
    RECORD_STATUSES = (
        ('public', 'Public'),
        ('draft', 'Draft'),
    )

    firstname = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=75, blank=True, null=True)
    nickname = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(null=True)
    excerpt = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=15, choices=RECORD_STATUSES, default='draft')
    filter = models.ManyToManyField(to=Filter, blank=True)

    object = models.Manager()
    public_records = CelebrityManager()

    class Meta:
        verbose_name_plural = 'celebrities'
        ordering = ('-created_at',)

    def __unicode__(self):
        return u"{0} {1} {2}".format(self.firstname, self.nickname, self.lastname)

    def _get_filters(self):
        filters = self.filter.all()
        return ', '.join(map(unicode, filters)) if filters else ''

    _get_filters.short_description = 'Filter'
    get_filters = property(_get_filters)

    def get_absolute_url(self):
        return reverse('heaps_app:celebrity-view', kwargs={'slug': self.slug})


# Helper function to rename uploading file in model
def rename_file(instance, filename):
    if filename.count('.') > 1:
        filename = filename.replace('.', '_', filename.count('.') - 1)

    name, ext = filename.split('.')
    if instance.pk:
        filename = '{0}.{1}'.format(hashlib.sha1(name + str(instance.pk + random.randrange(0, 9999))).hexdigest(),
                                    ext)
    else:
        filename = '{0}.{1}'.format(hashlib.sha1(name + str(random.randrange(0, 9999))).hexdigest(), ext)
    return os.path.join('photo', filename)


class Photo(models.Model):
    celebrity = models.ForeignKey(Celebrity)
    title = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to=rename_file)

    class Meta:
        verbose_name_plural = 'photo'

    def __unicode__(self):
        return self.title if self.title else 'Untitled image'


class SocialNetwork(models.Model):
    SOCIAL_NETWORKS = (
        ('ask-fm', 'Ask FM'),
        ('wikipedia', 'Wikipedia'),
        ('vk', 'Vk'),
        ('github', 'Github'),
        ('plus-google', 'Google +'),
        ('livejournal', 'Livejournal'),
        ('instagram', 'Instagram'),
        ('linkedin', 'Linkedin'),
        ('myspace', 'Myspace'),
        ('my-mail', 'My world'),
        ('ok-ru', 'Odnoklassniki'),
        ('promodj', 'Promo Dj'),
        ('soundcloud', 'Soundcloud'),
        ('twitter', 'Twitter'),
        ('twitch', 'Twitch'),
        ('facebook', 'Facebook'),
        ('youtube', 'Youtube'),
        ('official-web', 'Official site'),
    )

    celebrity = models.ForeignKey(to=Celebrity)
    social_network = models.CharField(max_length=75, choices=SOCIAL_NETWORKS)
    url = models.URLField()

    class Meta:
        verbose_name_plural = 'social networks'

    def __unicode__(self):
        return self.get_social_network_display()

    def detect_social_by_url(self):
        if not self.url.strip() or self.social_network:
            return False

        social_url = self.url.lower()

        for code, name in self.SOCIAL_NETWORKS:
            if code.replace('-', '.') in social_url:
                self.social_network = code
                return True
        return False
