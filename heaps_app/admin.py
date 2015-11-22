from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from heaps_app import models
from heaps_app import forms


class UserAdmin(DefaultUserAdmin):
    form = forms.UserChangeForm
    add_form = forms.UserCreationForm

    list_display = ('email', 'first_name', 'last_name', 'is_admin', 'is_superuser')
    list_per_page = 20
    list_filter = ('is_admin', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('avatar', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


class SocialNetworksInline(admin.TabularInline):
    model = models.SocialNetwork
    extra = 1


class PhotoInline(admin.TabularInline):
    model = models.Photo
    extra = 1


class FilterAdmin(admin.ModelAdmin):
    list_display = ('title', 'filter_type')
    list_per_page = 20


class CelebrityAdmin(admin.ModelAdmin):
    list_display = ('lastname', 'firstname', 'nickname', 'get_filters', 'created_at', 'status')
    list_per_page = 20
    fieldsets = (
        ('Main information', {
            'fields': ('firstname', 'lastname', 'nickname', 'slug', 'excerpt', 'description', 'created_at', 'filter', 'status')
        }),
        ('Seo information', {'fields': ('meta_title', 'meta_description', 'meta_keywords')}),
    )
    prepopulated_fields = {'slug': ('lastname', 'firstname')}
    inlines = [SocialNetworksInline, PhotoInline]
    form = forms.CelebrityAdminForm


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Filter, FilterAdmin)
admin.site.register(models.Celebrity, CelebrityAdmin)
