import datetime
import django
from nltk import word_tokenize
import os
import re
from slacker import Slacker
from sutime import SUTime
import tweepy
from tweepy.api import API 

# need to point Django at the right settings to access pieces of app
os.environ["DJANGO_SETTINGS_MODULE"] = "twotebotapi.settings"
django.setup()

from twotebotapp.bot_utils import db_utils, tweet_utils, time_utils
import twotebotapp.secrets as s
from twotebotapi.settings import BASE_DIR


class StreamListener(tweepy.StreamListener):
    """Object that defines the callback actions passed to tweepy.Stream"""
    def __init__(self, streambot, api=None):
        self.api = api or API()
        # needed ref to streambot so method can be called
        self.streambot = streambot
        self.tw_bot_id = 841013993602863104
        self.ignored_users = []
        
    def update_ignore_users(self):
        """Check app config table to get list of ignored twitter ids"""
        ignore_list = db_utils.get_ignored_users()
        ignore_list.append(self.tw_bot_id)
        self.ignored_users = ignore_list

    def on_status(self, status):
        """Take a tweet with matching keyword save and trigger retweet_logic"""
        
        self.update_ignore_users()

        if status.user.id in self.ignored_users:
            print("tweet from account on ignore list")
            return

        # create or update user and tweet records in Django models
        db_utils.get_or_create_user_and_tweet(status)

        # trigger logic to handle tweet and decide on response in Streambot
        self.streambot.retweet_logic(status.text, status.id_str, 
                                    status.user.screen_name, status.user.id)  
        
    def on_error(self, status_code):
        if status_code == 420:
            print(status_code, "error with tweepy")
            return False


class Streambot:
    """Stream Twitter and look for tweets that contain targeted words,
    when tweets found look for datetime and room, if present save tweet 
    to OutgoingTweet model.

    Ex.
    bot = Streambot()
    # to run a stream looking for tweets about PyCon
    bot.run_stream(["PyCon"])
    """
    def __init__(self):
        self.api = self.setup_auth()
        self.stream_listener = StreamListener(self)
        jar_files = os.path.join(BASE_DIR, "python-sutime", "jars") 
        self.sutime = SUTime(jars=jar_files, mark_time_ranges=True)
        self.slacker = Slacker(s.SLACK_TOKEN)

    def setup_auth(self):
        """Set up auth stuff for api and return tweepy api object"""
        auth = tweepy.OAuthHandler(s.listener["CONSUMER_KEY"], 
                                   s.listener["CONSUMER_SECRET"])
        auth.set_access_token(s.listener["ACCESS_TOKEN"], 
                              s.listener["ACCESS_TOKEN_SECRET"])

        api = tweepy.API(auth)
        return api

    def run_stream(self, search_list=None):
        """Start stream, when matching tweet found on_status method called. 
        search_list arg is a list of terms that will be looked for in tweets
        """
        if search_list == None:
            raise ValueError("Need a list of search terms as arg to run_stream")

        stream = tweepy.Stream(auth=self.api.auth, listener=self.stream_listener)
        stream.filter(track=search_list)

    def send_mention_tweet(self, screen_name):
        """Mention a user in a tweet from bot letting them know that
        their tweet has been recieved and that we will send out reminders
        about thier event.
        """
        time = datetime.datetime.now()
        mention = "@{} We saw your openspaces tweet! {}".format(screen_name, time)
        self.api.update_status(status=mention)

    def parse_time_room(self, tweet):
        """Get time and room number from a tweet using SUTime and tweet_utils"""
        extracted_time = self.sutime.parse(tweet)
        time_and_room = tweet_utils.get_time_and_room(tweet, extracted_time)
        return time_and_room

    def retweet_logic(self, tweet, tweet_id, screen_name, user_id):
        """Use SUTime to try to parse a datetime out of a tweet, if successful
        save tweet to OutgoingTweet to be retweeted
        """
        # use SUTime to parse a datetime out of tweet
        time_room = self.parse_time_room(tweet)

        # make sure both time and room extracted and only one val each
        val_check = [val for val in time_room.values() if len(val) == 1]

        if len(val_check) == 2:
            talk_room = time_room["room"][0]
            parsed_time = time_room["date"][0]
            talk_time = time_utils.convert_to_utc(parsed_time)

            # check for a time and room conflict, only one set of retweets per event
            conflict = db_utils.check_time_room_conflict(talk_time, talk_room)

            if not conflict:
                # send message to slack when a tweet is scheduled to go out
                slack_message = "{} From: {}, id: {}".format(tweet, screen_name, user_id)
                self.slacker.chat.post_message('#outgoing_tweets', slack_message)
                
                self.send_mention_tweet(screen_name)

                # This record lets us check that retweets not for same event
                db_utils.create_event(
                                      description=tweet,
                                      start=talk_time, 
                                      location=talk_room,
                                      creator=screen_name
                                     )

                # schedules reminder tweets to be sent out before event
                tweet_utils.schedule_tweets(screen_name, tweet, tweet_id, talk_time)


if __name__ == '__main__':
    bot = Streambot()
    keyword = "adlsjlflkjdhsfla"
    print(keyword)
    bot.run_stream([keyword])
    
