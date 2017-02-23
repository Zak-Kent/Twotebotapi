from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'info/$', views.ListCreateTweets.as_view()),
    url(r'^update/(?P<pk>[0-9]+)$', views.outbound_tweets),
]