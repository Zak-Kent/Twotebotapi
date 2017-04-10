import tweepy
from tweepy.api import API 
from sutime import SUTime
from nltk import word_tokenize
import re
import os
from datetime import datetime, timedelta
from dateutil.parser import parse
import django

import pytz

# need to point Django at the right settings to access pieces of app
os.environ["DJANGO_SETTINGS_MODULE"] = "twotebotapi.settings"
django.setup()

from twotebotapp import db_bot_utils
import twotebotapp.secrets as s
from twotebotapp import models
from twotebotapi.settings import BASE_DIR


class StreamListener(tweepy.StreamListener):
    """
    Object that defines the callback actions passed to tweepy.Stream 
    """
    def __init__(self, streambot, api=None):
        self.api = api or API()
        # needed ref to streambot so method can be called there
        self.streambot = streambot
        self.tw_bot_id = 841013993602863104
        self.ignored_users = [self.tw_bot_id, ]
        
    def update_ignore_users(self):
        """
        Check app config table to get list of ignored twitter ids, ignore bot
        """
        ignore_list = db_bot_utils.get_ignored_users()
        ignore_list.append(self.tw_bot_id)
        self.ignored_users = ignore_list

    def on_status(self, status):
        # call to check for ignored users from AppConfig
        self.update_ignore_users()

        if status.user.id in self.ignored_users:
            print("tweet from account on ignore list")
            return

        # create or update user and tweet records in Django models
        db_bot_utils.get_or_create_user_and_tweet(status)

        # trigger time parsing with SUTime inside streambot
        self.streambot.retweet_logic(status.text, status.id_str, 
                                        status.user.screen_name)  
        
    def on_error(self, status_code):
        if status_code == 420:
            print(status_code, "error with tweepy")
            return False


class BaseStreamBot:
    """
    Base class with functionality not related to Tweepy and SUTime 
    """

    def schedule_tweets(self, screen_name, tweet, tweet_id, talk_time):
        """
        Take tweet and datetime, schedule num of reminder tweets at set intervals 
        """
        # check config table to see if autosend on
        approved = db_bot_utils.check_for_auto_send()

        tweet_url = "https://twitter.com/{name}/status/{tweet_id}"
        embeded_tweet = tweet_url.format(name=screen_name, tweet_id=tweet_id)

        # set num of reminder tweets and interval in mins that tweets sent
        # num_tweets = 2 & interval = 15 sends 2 tweets 30 & 15 mins before 
        num_tweets = 2
        interval = 1

        for  mins in range(interval,(num_tweets*interval+1), interval):
            remind_time = talk_time - timedelta(minutes=mins)
            message = "Coming up in {} minutes! {}".format(mins, embeded_tweet)

            tweet_obj = {
                "message": message,
                "approved": approved,
                "remind_time": remind_time
            }
            print("message should be saved!!!")
            print(tweet_obj)

            # db_bot_utils.save_outgoing_tweet(tweet_obj)

    def convert_to_utc(self, talk_time):
        """
        Convert the datetime string we get from SUTime to utcnow
        """
        # get correct local year, month, dat
        local_date = datetime.now(self.tz)
        local_date_str = datetime.strftime(local_date, "%Y %m %d")
        year, month, day = local_date_str.split(" ")

        # get SUTime parsed talk time and extract hours, mins
        dt_obj = parse(talk_time)
        local_time_str = datetime.strftime(dt_obj, "%H %M")
        hours, mins = local_time_str.split(" ")
        
        # build up correct datetime obj, normalize & localize, switch to utc 
        correct_dt = datetime(int(year), int(month), int(day), int(hours), int(mins))
        tz_aware_local = self.tz.normalize(self.tz.localize(correct_dt))
        local_as_utc = tz_aware_local.astimezone(pytz.utc)
        
        return local_as_utc


class Streambot(BaseStreamBot):
    """
    Stream Twitter and look for tweets that contain targeted words, 
    when tweets found look for datetime and room, if present save tweet to
    OutgoingTweet model.  

    Ex.
    bot = Streambot()
    # to run a stream looking for tweets about PyCon
    bot.run_stream(["PyCon"]) 
    """
    def __init__(self):
        self.api = self.setup_auth()
        self.stream_listener = StreamListener(self)
        self.tz = pytz.timezone('US/Pacific')

        jar_files = os.path.join(BASE_DIR, "python-sutime", "jars") 
        self.sutime = SUTime(jars=jar_files, mark_time_ranges=True)

    def setup_auth(self):
        """
        Set up auth stuff for api and return tweepy api object
        """
        auth = tweepy.OAuthHandler(s.listener["CONSUMER_KEY"], s.listener["CONSUMER_SECRET"])
        auth.set_access_token(s.listener["ACCESS_TOKEN"], s.listener["ACCESS_TOKEN_SECRET"])
        api = tweepy.API(auth)

        return api

    def run_stream(self, search_list=[]):
        """
        Start stream, when matching tweet found on_status in StreamListener called. 
        search_list arg is a list of terms that will be looked for in tweets
        """
        if search_list == []:
            raise ValueError("Need a list of search terms as arg to run_stream")

        stream = tweepy.Stream(auth=self.api.auth, listener=self.stream_listener)
        stream.filter(track=search_list)

    def retweet_logic(self, tweet, tweet_id, screen_name):
        """
        Use SUTime to try to parse a datetime out of a tweet, if successful
        save tweet to OutgoingTweet to be retweeted
        """
        print(tweet, tweet_id)
        time_room = self.get_time_and_room(tweet)

        # check to make sure both time and room extracted and only one val for each
        val_check = [val for val in time_room.values() if len(val) == 1]

        if len(val_check) == 2:
            # way to mention a user after a valid tweet is recieved
            # time_stamp = datetime.datetime.utcnow()

            # mention = "@{} We saw your openspaces tweet!{}".format(screen_name, time_stamp)

            # self.api.update_status(status=mention)

            # need to make time from SUTime match time Django is using
            sutime_stuff = time_room["date"][0]
            print("sutime_stuff: {}".format(sutime_stuff))
            talk_time = self.convert_to_utc(time_room["date"][0])
            print("reult from convet to utc: {}".format(talk_time))

            test = self.schedule_tweets(screen_name, tweet, tweet_id, talk_time)
            
    def get_time_and_room(self, tweet):
        """
        Get time and room number from a tweet
        Written by Santi @ https://github.com/adavanisanti
        """
        result = {}
        result["date"] = []
        result["room"] = []
 
        time_slots = self.sutime.parse(tweet)
        tweet_without_time = tweet

        for time_slot in time_slots:
            tweet_without_time = tweet_without_time.replace(time_slot.get("text"),"")
            result["date"].append(time_slot.get("value"))
        
        # filter_known_words = [word.lower() for word in word_tokenize(tweet_without_time) if word.lower() not in (self.stopwords + nltk.corpus.words.words())]
        filter_known_words = [word.lower() for word in word_tokenize(tweet_without_time)]

        # regular expression for room
        room_re = re.compile("([a-zA-Z](\d{3})[-+]?(\d{3})?)")

        for word in filter_known_words:
            if room_re.match(word):
                result["room"].append(room_re.match(word).group())

        return result


if __name__ == '__main__':
    bot = Streambot()
    keyword = "adlsjlflkjdhsfla"
    print(keyword)
    bot.run_stream([keyword])
