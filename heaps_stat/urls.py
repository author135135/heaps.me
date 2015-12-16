from django.conf.urls import include, url
from heaps_stat import views


urlpatterns = [
    url('^social-link-clicks/$', views.social_link_clicks, name='social-link-clicks'),
]
