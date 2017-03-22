from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta
from celery.decorators import periodic_task

from twotebotapp.tweepy_connect import tweepy_send_tweet
from .models import Tweets, AppConfig
from twotebotapi.celery import app 
from twotebotapp.openspacesbot import get_pycon_tweets

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Set up periodic tasks with beat after app is finalized and loaded 
    """
    # beat task that runs every 30 seconds and calls beat_tweet_scheduler
    sender.add_periodic_task(30.0, beat_tweet_scheduler.s(), 
                            name='check db for pending tweets')

@app.task
def beat_tweet_scheduler():
    """
    Check for tweets that are scheduled to go out within next minute & schedule 
    """ 
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=1)
    tweets = Tweets.objects.filter(sent_time__isnull=True) \
                           .filter(task_scheduled__exact=False) \
                           .filter(scheduled_time__range=(start_time, end_time)) 

    # schedule tweeter task and then set tweet task_scheduled field to True
    for tweet in tweets:
        tweeter.apply_async((tweet.tweet, tweet.id), eta=tweet.scheduled_time)
        Tweets.objects.filter(pk=tweet.id).update(task_scheduled=True)
    print("beat scheduled")
    return

# ----------------------------------------------------------------------------
# need to link code below to twitter bot 

@app.task(
    bind=True,
    max_retries=3,
    soft_time_limit=5, # 5 seconds before task times out
    # ignore_result=True
)
def tweeter(self, tweet, id):
    """
    Needs to have the process for sending a tweet to Twitter 
    """ 
    time_sent = datetime.utcnow()
    Tweets.objects.filter(pk=id).update(sent_time=time_sent)

    # tweepy_send_tweet(tweet)
    print("tweet sent, indside tweeter : {}".format(tweet))
    
    return 

@app.task(
    bind=True,
    max_retries=3,
    soft_time_limit=5, # 5 seconds before task times out
    # ignore_result=True
)
def tweet_adder(self, tweet):
    """
    Send or stage tweet depending on value in AppConfig table, save tweet record
    """ 
    config_obj = AppConfig.objects.latest("id")
    # Choices on approved field are 0-2 with 0 meaning pending
    approved = 1 if config_obj.auto_send else 0        

    tweet_obj = Tweets(tweet=tweet, approved=approved)
    tweet_obj.save()
    return

@app.task(
    bind=True,
    max_retries=3,
    soft_time_limit=5, # 5 seconds before task times out
    # ignore_result=True
)
def get_tweets_test(self):
    print("inside get_tweets_test task")
    get_pycon_tweets()

    
    