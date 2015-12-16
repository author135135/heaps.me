from django.db import models
from heaps_app.models import Celebrity


class SocialLinkClicks(models.Model):
    celebrity = models.ForeignKey(to=Celebrity)
    social_network = models.CharField(max_length=75)
    clicks_count = models.IntegerField()

    class Meta:
        verbose_name_plural = 'social link clicks'


class SocialLinkClicksStat(models.Model):
    social_link_clicks = models.ForeignKey(to=SocialLinkClicks)
    ip = models.GenericIPAddressField()
    date = models.DateField(auto_now_add=True)
