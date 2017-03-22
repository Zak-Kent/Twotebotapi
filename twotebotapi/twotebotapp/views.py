from rest_framework import generics

from . import serializers
from . import models
from . import filters 


class RetriveUpdateOutgoingTweets(generics.RetrieveUpdateAPIView):
    """
    Endpoint that lets a user send PUT or PATCH request to updat a tweet object
    """
    queryset = models.Tweets.objects.all()
    serializer_class = serializers.TweetSerializer


class ListCreateAppConfig(generics.ListCreateAPIView):
    """
    Endpoint to update current config settings by adding a config object to table
    """
    queryset = models.AppConfig.objects.all()
    serializer_class = serializers.AppConfigSerializer


class OutgoingTweets(generics.ListCreateAPIView):
    """
    Tweet endpoint to display tweet info used by front end.

    Two filter options are available through the use of querystring params.

    Option one: "approved" - lets user filter on current level of tweet approval
    Tweet approval choices:
        0 - needs_approval
        1 - approved
        2 - denied

    Option two: "pending" - T/F flag filters if tweet is still waiting to be sent

    Ex.
    /twitter/tweets/?approved=1 --> returns all tweets that are approved

    /twitter/tweets/?pending=True --> returns all tweets still waiting to be sent

    /twitter/tweets/?approved=0&pending=True --> you can combine these query params in any order
    """
    serializer_class = serializers.TweetSerializer
    filter_class = filters.TweetFilter

    def get_queryset(self):
        queryset = models.Tweets.objects.all()
        pending = self.request.query_params.get('pending', None)

        # needed to convert querystring True or False to look for tweets pending
        # but not yet sent there has to be a better way to do this!!!
        # right now you're returning False with any value that isn't True. 

        if pending is not None:
            pend = True if pending == 'True' else False
            queryset = queryset.filter(sent_time__isnull=pend)
        return queryset


class RetrieveDestroyTweets(generics.RetrieveDestroyAPIView):
    """
    Utility endpoint used to clean out tweets when manually testing
    """
    queryset = models.Tweets.objects.all()
    serializer_class = serializers.TweetSerializer


# ------------------------------------------------------------------
class ListUser(generics.ListAPIView):
    """
    
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class ListStreamedTweet(generics.ListAPIView):
    """
    
    """
    queryset = models.StreamedTweet.objects.all()
    serializer_class = serializers.StreamedTweetSerializer














