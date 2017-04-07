import django_filters
from twotebotapp.models import Tweets

APPROVAL_CHOICES = (
    (0, 'needs_action'),
    (1, 'Approved'),
    (2, 'Denied'),
)

class TweetFilter(django_filters.FilterSet):
    approved = django_filters.ChoiceFilter(choices=APPROVAL_CHOICES)

    class Meta:
        model = Tweets
        fields = ['approved',]

