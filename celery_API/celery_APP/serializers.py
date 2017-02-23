from rest_framework import serializers
from . import models

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tweets
        fields = '__all__'
        # exclude = (id,)