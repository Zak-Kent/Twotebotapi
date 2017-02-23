from rest_framework import generics

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from . import serializers
from . import models

# -----------------------------------------------------------------------
# endpoint to change records in tweet table
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
        serializer = serializers.TweetSerializer(tweet, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # tweet_adder.delay()

            # tweet_info = serializer.data
            # if tweet_info["approved"] == 1:
            #     tweeter.delay(tweet_info["tweet"])

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------------------------------------------------
# tweet endpoint to add info

class ListCreateTweets(generics.ListCreateAPIView):
    queryset = models.Tweets.objects.all()
    serializer_class = serializers.TweetSerializer


# -----------------------------------------------------------------------
