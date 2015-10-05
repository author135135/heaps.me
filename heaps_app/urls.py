from django.conf.urls import include, url
from heaps_app import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^person/add/$', views.CelebrityAddView.as_view(), name='celebrity-add'),
    url(r'^person/(?P<slug>[\w-]+)/$', views.CelebrityView.as_view(), name='celebrity-view'),
]
