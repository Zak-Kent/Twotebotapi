from __future__ import absolute_import, unicode_literals

from celery import shared_task

from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import datetime, timedelta

from .models import Tweets, AppConfig




# callback func used to trigger sending logic task anytime the tweet model saves 
@receiver(post_save)
def tweet_model_callback(sender, **kwargs):
    """
    Callback function that gets triggered on a change to object in model.
    Send tweets needing scheduling to tweet_scheduler
    """
    # grab tweets that need to be scheduled for future with celery 
    tweets = Tweets.objects.filter(approved__exact=1) \
                           .filter(scheduled_time__isnull=True)

    for tweet in tweets: 
        tweet_scheduler(tweet)

    print("Request finished!, inside tweet_callback")
    return 

 
def tweet_scheduler(tweet):
    """
    Schedule tweets for a time in the futre using Celery ETA 
    """

    if tweet.time_interval is None:
        wait_time = AppConfig.objects.latest("id").default_send_interval
        
    else: 
        wait_time = tweet.time_interval

    eta_time = datetime.utcnow() + timedelta(minutes=wait_time)

    Tweets.objects.filter(pk=tweet.id).update(scheduled_time=eta_time)

    tweeter.apply_async((tweet.tweet, tweet.id), eta=eta_time)

    print("tweet scheduled inside tweet_scheduler for: {}".format(eta_time))

    return

    


@shared_task
def tweeter(tweet, id):
    """
    send tweet out 
    """ 
    print("tweet sent, indside tweeter : {}".format(tweet))

    time_sent = datetime.utcnow()
    Tweets.objects.filter(pk=id).update(sent_time=time_sent)

    # still need to add the sending of tweet to twitter

    return 

@shared_task
def tweet_adder(tweet):
    """
    send or stage tweet depending on value in AppConfig table, save tweet record
    """ 
    auto_send_flag = AppConfig.objects.latest("id")
    print("current value of auto send flag: {}".format(auto_send_flag.auto_send))

    if auto_send_flag.auto_send:
        tweeter.delay(tweet)
        approved = 1    
    
    else: 
        approved = None

    tweet_obj = Tweets(tweet=tweet, approved=approved,
                        scheduled_time=datetime.datetime.now())
    tweet_obj.save()

    return









