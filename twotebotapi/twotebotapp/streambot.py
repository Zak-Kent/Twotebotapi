import tweepy
from tweepy.api import API 
from sutime import SUTime
from nltk import word_tokenize
import re
import os

import twotebotapp.secrets as s
from twotebotapp import models
from twotebotapi.settings import BASE_DIR


class StreamListener(tweepy.StreamListener):
    """
    Object that defines the callback actions passed to tweepy.Stream 
    """

    def __init__(self, streambot, api=None):
        # needed to override __init__ to get ref to Streambot
        # with ref the method retweet_logic can be used in on_status
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

        # trigger time parsing with SUTime inside streambot
        self.streambot.retweet_logic(status.text, status.id_str)  
        
    def on_error(self, status_code):
        if status_code == 420:
            return False


class Streambot:
    def __init__(self):
        self.api = self.setup_auth()
        self.stream_listener = StreamListener(self)

        jar_files = os.path.join(BASE_DIR, 'python-sutime/jars') 
        self.sutime = SUTime(jars=jar_files, mark_time_ranges=True)

    def setup_auth(self):
        """
        Set up auth stuff for api and return tweepy api object
        """
        auth = tweepy.OAuthHandler(s.CONSUMER_KEY, s.CONSUMER_SECRET)
        auth.set_access_token(s.ACCESS_TOKEN, s.ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        return api

    def run_stream(self, search_list=["Pycon"]):
        """
        Start stream, when matching tweet found on_status in StreamListener called 

        search_list arg is a list of terms that will be looked for in tweets
        """
        stream = tweepy.Stream(auth=self.api.auth, listener=self.stream_listener)
        stream.filter(track=search_list)

    def retweet_logic(self, tweet, tweet_id):
        """
        Use SUTime to try to parse a datetime out of a tweet, if successful
        save tweet to OutgoingTweet to be retweeted
        """
        print(tweet, tweet_id)

        time_room = self.get_time_and_room(tweet)

        print(time_room)
        # check to make sure both time and room extracted and only one val for each
        val_check = [val for val in time_room.values() if val != [] and len(val) == 1]

        if len(val_check) == 2:
            # check config table to see if autosend on
            config_obj = models.AppConfig.objects.latest("id")
            approved = 1 if config_obj.auto_send else 0

            tweet_obj = models.Tweets(tweet=tweet, approved=approved)
            tweet_obj.save()

    def get_time_and_room(self, tweet):
        '''
        Get time and room number from a tweet
        Written by Santi @ https://github.com/adavanisanti
        '''
        result = {}
        result['date'] = []
        result['room'] = []

        
        time_slots = self.sutime.parse(tweet)
        tweet_without_time = tweet

        for time_slot in time_slots:
            tweet_without_time = tweet_without_time.replace(time_slot.get('text'),'')
            result['date'].append(time_slot.get('value'))
        
        # filter_known_words = [word.lower() for word in word_tokenize(tweet_without_time) if word.lower() not in (self.stopwords + nltk.corpus.words.words())]
        filter_known_words = [word.lower() for word in word_tokenize(tweet_without_time)]

        # regular expression for room
        room_re = re.compile('([a-zA-Z](\d{3})[-+]?(\d{3})?)')

        for word in filter_known_words:
            if room_re.match(word):
                result['room'].append(room_re.match(word).group())

        return result

if __name__ == "__main__":
    bot = Streambot()
    # start stream 
    bot.run_stream(["jjssaa"])










