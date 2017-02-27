from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .models import Tweets, AppConfig

# using this to fake sheduled time for required tweets field 
import datetime

# need to make another task that schedules tweets to be sent out at a later time 
@shared_task
def tweet_scheduler(tweet):
    # need to add sending action here 
    # use apply_async to add task to outgoing que for a later time 
    # use calculate time delta between current time and when we want to send tweet

    scheduled_time = tweet["scheduled_time"]
    current_time = datetime.datetime.now()

    time_delta = scheduled_time - current_time
    print('*' * 80)
    print("time delta inside tweet_scheduler: {}".format(time_delta))
    print('*' * 80)
    return


@shared_task
def tweeter(tweet):
    """
    send tweet out 
    """ 
    print("tweet object : {}".format(tweet))

    time_sent = datetime.datetime.now()
    id_pk = int(tweet["id"])
    print("id_pk value: {}".format(id_pk))

    Tweets.objects.filter(pk=id_pk).update(sent_time=time_sent)

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









