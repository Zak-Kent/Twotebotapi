import tweepy
import twotebotapp.secrets as s 
import json
from sutime import SUTime
from twotebotapp import models

class StreamListener(tweepy.StreamListener):
    """
    Object that defines the callback actions passed to tweepy.Stream 
    """
    def on_status(self, status):
        # save user record to User model
        user, created = models.User.objects.get_or_create(id_str=str(status.user.id))
        user.verified = status.user.verified  # v4
        user.time_zone = status.user.time_zone  # v4
        user.utc_offset = status.user.utc_offset  # -28800 (v4)
        user.protected = status.user.protected  # v4
        user.location = status.user.location  # Houston, TX  (v4)
        user.lang = status.user.lang  # en  (v4)
        user.screen_name = status.user.screen_name
        user.followers_count = status.user.followers_count
        user.statuses_count = status.user.statuses_count
        user.friends_count = status.user.friends_count
        user.favourites_count = status.user.favourites_count
        user.save()

        # save tweet record to StreamedTweet model
        tweet_record, created = models.StreamedTweet.objects.get_or_create(id_str=status.id_str)
        tweet_record.id_str = status.id_str
        tweet_record.user = user
        tweet_record.favorite_count = status.favorite_count
        tweet_record.text = status.text
        tweet_record.source = status.source
        tweet_record.save()      
        
    def on_error(self, status_code):
        if status_code == 420:
            return False


def setup_auth():
    """
    Set up auth stuff for api and return tweepy api object
    """
    auth = tweepy.OAuthHandler(s.CONSUMER_KEY, s.CONSUMER_SECRET)
    auth.set_access_token(s.ACCESS_TOKEN, s.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    return api


def run_stream():
    api = setup_auth()
    stream_listener = StreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

    stream.filter(track=["justaddzebras"])
