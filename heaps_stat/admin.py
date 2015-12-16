from django.contrib import admin
from heaps_stat import models


class SocialLinkClicksAdmin(admin.ModelAdmin):
    list_display = ('celebrity', 'social_network', 'clicks_count')
    list_per_page = 20
    list_filter = ('social_network',)
    search_fields = ('celebrity__firstname', 'celebrity__lastname', 'celebrity__nickname', 'social_network')

admin.site.register(models.SocialLinkClicks, SocialLinkClicksAdmin)
