import os
import hashlib
import random

from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse


# Custom Managers
class CelebrityManager(models.Manager):
    def get_queryset(self):
        return super(CelebrityManager, self).get_queryset().filter(status='public').prefetch_related(
            'photo_set').prefetch_related('socialnetwork_set')


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
        return ', '.join(map(unicode, self.filter.all()))

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
        ('facebook', 'Facebook'),
        ('vk', 'Vk'),
        ('instagram', 'Instagram')
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
            if code in social_url:
                self.social_network = code
                return True
        return False
