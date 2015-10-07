from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from heaps_app import views

account_patterns = [
    url(r'^login/$', views.account_login, name='account-login'),
    url(r'^registration/$', views.account_registration, name='account-registration'),
    url(r'^logout/$', views.account_logout, name='account-logout'),
]

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^person/add/$', login_required(views.CelebrityAddView.as_view(), login_url='/'), name='celebrity-add'),
    url(r'^person/(?P<slug>[\w-]+)/$', views.CelebrityView.as_view(), name='celebrity-view'),
    url(r'^account/', include(account_patterns)),
]
