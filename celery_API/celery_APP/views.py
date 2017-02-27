from rest_framework import generics

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from . import serializers
from . import models
from .tasks import tweeter, tweet_adder, tweet_scheduler

# -----------------------------------------------------------------------
# endpoint to change records in outgoing tweet table
@api_view(['GET', 'PUT'])
def outbound_tweets(request, pk):
    """
    Retrieve, update or delete a tweet instance.
    """
    try:
        tweet = models.Tweets.objects.get(pk=pk)
    except models.Tweets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = serializers.TweetSerializer(tweet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # needs to have approval and scheduled sending time validated 
        serializer = serializers.TweetSerializer(tweet, data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------------------------------------------------
# endpoint to change config table 
class ListCreateAppConfig(generics.ListCreateAPIView):
    queryset = models.AppConfig.objects.all()
    serializer_class = serializers.AppConfigSerializer

# -----------------------------------------------------------------------
# tweet endpoint to add info
class ListCreateTweets(generics.ListCreateAPIView):
    queryset = models.Tweets.objects.all()
    serializer_class = serializers.TweetSerializer

# -----------------------------------------------------------------------
