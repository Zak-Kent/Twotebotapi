import django_filters
from twotebotapp.models import Tweets

class OutgoingTweetFilter(django_filters.FilterSet):
    hashtag = django_filters.CharFilter(name='tweet', lookup_expr='icontains')

    class Meta:
        model = Tweets
        fields = ['tweet', 'approved']