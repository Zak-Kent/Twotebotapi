from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time 
from .models import Tweets


@shared_task
def tweeter(tweet):
    # when object is marked ok to be sent by front-end PUT request 
    # this task will fire and in production send the tweet 
    print(tweet)
    return 

@shared_task
def tweet_adder():
    # simulates a background process adding tweets into the Tweets model that
    # are waiting for approval before being sent by tweeter 
    
    # in production this task will take data from twitter bot and create new 
    # entry in tweets model for outgoing tweets
    for count in range(3):
        fake_tweet = Tweets(tweet="fake tweet: {} inside task".format(count),
                             needs_approval=True)
        fake_tweet.save()
        print("tweet added")
        time.sleep(5)

    return