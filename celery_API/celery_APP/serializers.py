from rest_framework import serializers
from . import models

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tweets
        fields = ('id', 'tweet', 'approved', 'time_interval')
        


class AppConfigSerializer(serializers.ModelSerializer):
    class Meta: 
        model = models.AppConfig
        fields = '__all__'
