from __future__ import absolute_import, unicode_literals
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from celery.decorators import periodic_task

from .models import Tweets, AppConfig
from twotebotapi.celery import app 

# callback func used to trigger sending logic task anytime the Tweets model saves 
@receiver(post_save, sender=Tweets, dispatch_uid="unique_identifier")
def tweet_model_callback(sender, **kwargs):
    """
    Callback function that gets triggered on a change to object in model.
    Send tweets needing scheduling to tweet_scheduler
    """
    # grab tweets that still need to be scheduled for future with celery 
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

    # tweeter.apply_async((tweet.tweet, tweet.id), eta=eta_time)

    print("tweet scheduled inside tweet_scheduler for: {}".format(eta_time))
    return

# sets up periodic tasks with beat after app is finalized
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, beat_tweet_scheduler.s(), name='check db for pending tweets')

@app.task
def beat_tweet_scheduler():
    # a beat task that runs every 10 seconds checking db for scheduled tweets that need to be sent within 
    # next 2 mins, if those tweets exist calc eta time and set up tweeter task 
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=2)


    tweets = Tweets.objects.filter(sent_time__isnull=True) \
                           .filter(task_scheduled__exact=False) \
                           .filter(scheduled_time__range=(start_time, end_time)) 

    print(tweets)
    print("beat scheduled")
    return

@app.task(
    bind=True,
    max_retries=3,
    soft_time_limit=5, # 5 seconds before task times out
    # ignore_result=True
)
def tweeter(self, tweet, id):
    """
    sends tweet out 
    """ 
    print("tweet sent, indside tweeter : {}".format(tweet))

    time_sent = datetime.utcnow()
    Tweets.objects.filter(pk=id).update(sent_time=time_sent)

    # still need to add the sending of tweet to twitter
    return 

@app.task(
    bind=True,
    max_retries=3,
    soft_time_limit=5, # 5 seconds before task times out
    # ignore_result=True
)
def tweet_adder(self, tweet):
    """
    send or stage tweet depending on value in AppConfig table, save tweet record
    """ 
    config_obj = AppConfig.objects.latest("id")
    # Choices on approved field are 0-2 with 0 meaning pending
    approved = 1 if config_obj.auto_send else 0        

    tweet_obj = Tweets(tweet=tweet, approved=approved)
    tweet_obj.save()
    return









