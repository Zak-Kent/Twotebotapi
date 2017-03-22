from rest_framework import serializers
from . import models

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tweets
        # fields = ('id', 'tweet', 'approved', 'time_interval')
        fields = '__all__'
        # exclude = ('task_scheduled', )
        


class AppConfigSerializer(serializers.ModelSerializer):
    class Meta: 
        model = models.AppConfig
        fields = '__all__'


class StreamedTweetSerializer(serializers.ModelSerializer):
    class Meta: 
        model = models.StreamedTweet
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = models.User
        fields = '__all__'