from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^tweets/$', views.ListCreateTweets.as_view()),
    url(r'^update/(?P<pk>[0-9]+)$', views.outbound_tweets),
    url(r'^config/$', views.ListCreateAppConfig.as_view()),
]