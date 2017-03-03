from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from . import serializers
from . import models
from . import filters 


@api_view(['GET', 'PUT'])
def outbound_tweets(request, pk):
    """
    Retrieve or update a tweet instance, used by frontend to trigger scheduling
    """
    try:
        tweet = models.Tweets.objects.get(pk=pk)
    except models.Tweets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = serializers.TweetSerializer(tweet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = serializers.TweetSerializer(tweet, data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetriveUpdateOutgoingTweets(generics.RetrieveUpdateAPIView):
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

















