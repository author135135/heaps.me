from django.conf.urls import include, url
from heaps_app import views
from heaps_app import mail

account_patterns = [
    url(r'^login/$', views.account_login, name='account-login'),
    url(r'^registration/$', views.account_registration, name='account-registration'),
    url(r'^logout/$', views.account_logout, name='account-logout'),
    url(r'^my-subscribes/$', views.AccountMySubscribes.as_view(), name='account-my-subscribes'),
    url(r'^settings/$', views.AccountSettings.as_view(), name='account-settings'),
    url(r'^forgotten-password/$', views.account_forgotten_password, name='account-forgotten-password'),
    url(r'^add-person/$', views.AccountCelebrityAddView.as_view(), name='account-celebrity-add'),
]

person_patterns = [
    url(r'^email-sent/$', mail.email_validation),
    url(r'^(?P<slug>[\w-]+)/$', views.CelebrityView.as_view(), name='celebrity-view'),
    url(r'^(?P<slug>[\w-]+)/subscribe/$', views.celebrity_subscribe, name='celebrity-subscribe'),
    url(r'^(?P<slug>[\w-]+)/unsubscribe/$', views.celebrity_unsubscribe, name='celebrity-unsubscribe'),
]

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^person/', include(person_patterns)),
    url(r'^account/', include(account_patterns)),
]
