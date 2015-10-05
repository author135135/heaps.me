from django.conf.urls import include, url
from heaps_app import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^celebrity/add/$', views.AddCelebrityView.as_view(), name='add-celebrity'),
]
