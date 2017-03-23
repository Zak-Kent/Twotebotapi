import tweepy
from tweepy.api import API 
from sutime import SUTime

import twotebotapp.secrets as s
from twotebotapp import models

class StreamListener(tweepy.StreamListener):
    """
    Object that defines the callback actions passed to tweepy.Stream 
    """

    def __init__(self, streambot, api=None):
        # needed to override __init__ to get ref to Streambot
        # with ref method to parse datetime can be triggered in on_status callback
        self.api = api or API()
        self.streambot = streambot

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

        # trigger time parsing with SUTime
        # must have instance of stream_bot alread setup for this call to work
        self.streambot.parse_datetime(status.text, status.id_str)  
        
    def on_error(self, status_code):
        if status_code == 420:
            return False


# def setup_auth():
#     """
#     Set up auth stuff for api and return tweepy api object
#     """
#     auth = tweepy.OAuthHandler(s.CONSUMER_KEY, s.CONSUMER_SECRET)
#     auth.set_access_token(s.ACCESS_TOKEN, s.ACCESS_TOKEN_SECRET)
#     api = tweepy.API(auth)

#     return api


# def run_stream():
#     api = setup_auth()
#     stream_listener = StreamListener()
#     stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

#     stream.filter(track=["justaddzebras"])

class Streambot:
    def __init__(self):
        self.api = self._setup_auth()
        self.stream_listener = StreamListener(self)

        # need to chage to use settings.BASE_DIR
        jar_files = '/Users/zakkent/Documents/celery_test/twotebotapi/python-sutime/jars' 
        self.sutime = SUTime(jars=jar_files, mark_time_ranges=True)

    def _setup_auth(self):
        """
        Set up auth stuff for api and return tweepy api object
        """
        auth = tweepy.OAuthHandler(s.CONSUMER_KEY, s.CONSUMER_SECRET)
        auth.set_access_token(s.ACCESS_TOKEN, s.ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        return api

    def run_stream(self):
        """
        Stream data from twitter, when status recived on_status method of 
        StreamListener called
        """
        stream = tweepy.Stream(auth=self.api.auth, listener=self.stream_listener)
        stream.filter(track=["jjssaa"])

    def parse_datetime(self, tweet, tweet_id):
        """
        Use SUTime to try to parse a datetime out of a tweet, if successful
        save tweet to OutgoingTweet to be retweeted
        """
        print(tweet, tweet_id)


# if __name__ == "__main__":
#     bot = Streambot()
#     # start stream 
#     bot.run_stream()










