from django.contrib import admin
from heaps_app import models
from heaps_app import forms


class SocialNetworksInline(admin.TabularInline):
    model = models.SocialNetwork
    extra = 1


class PhotoInline(admin.TabularInline):
    model = models.Photo
    extra = 1


class FilterAdmin(admin.ModelAdmin):
    list_display = ('title', 'filter_type')


class CelebrityAdmin(admin.ModelAdmin):
    list_display = ('lastname', 'firstname', 'nickname', 'get_filters', 'created_at', 'status')
    fieldsets = (
        ('Main information', {
            'fields': ('firstname', 'lastname', 'nickname', 'excerpt', 'description', 'created_at', 'filter', 'status')
        }),
        ('Seo information', {'fields': ('meta_title', 'meta_description', 'meta_keywords')}),
    )
    inlines = [SocialNetworksInline, PhotoInline]
    form = forms.CelebrityAdminForm


admin.site.register(models.Filter, FilterAdmin)
admin.site.register(models.Celebrity, CelebrityAdmin)
