from django.test import TestCase
import time
import tweepy

from twotebotapp.models import Tweets, AppConfig
from twotebotapp.serializers import TweetSerializer
from twotebotapp.secrets import listener, sender 

class TwitterBot:
    """
    Class that helps run the actions in an end to end test of the twitter bot.
    """
    def __init__(self, account):
        # tw_api is access point to all Tweepy methods
        self.tw_api = self.setup_tw_api(account)
        self.user_info = self.get_user_info()

    def setup_tw_api(self, account):
        auth = tweepy.OAuthHandler(account["CONSUMER_KEY"], account["CONSUMER_SECRET"])
        auth.set_access_token(account["ACCESS_TOKEN"], account["ACCESS_TOKEN_SECRET"])
        return tweepy.API(auth)

    def get_user_info(self):
        user_obj = self.tw_api.me()

        result = {}
        result["id"] = user_obj._json["id"]
        result["screen_name"] = user_obj._json["screen_name"]
        return result

    def get_tweets(self):
        return self.tw_api.user_timeline(self.user_info["id"])

    def clean_tweets(self):
        """
        Get 20 most recent tweets from user and delete all.
        """
        tweets = self.tw_api.user_timeline(self.user_info["id"])
        tweet_ids = [status._json["id"] for status in tweets]

        for tw_id in tweet_ids:
            self.tw_api.destroy_status(tw_id)


class TestEndToEnd(TestCase):
    """
    End to end tests that can be run with the command: 
    >>> python manage.py test twotebotapp/end_to_end/
    """

    @classmethod
    def setUpClass(cls):
        super(TestEndToEnd, cls).setUpClass()
        cls.keyword = "adlsjlflkjdhsfla"
        cls.s_bot = TwitterBot(sender)
        cls.l_bot = TwitterBot(listener)

    def setUp(self):
        test_conf = {
        "auto_send": 0,
        "default_send_interval": 1,
        "ignore_users": []
        }
        AppConfig.objects.create(**test_conf)

    def test_correct_keyword_no_time_room(self):
        """
        Send a tweet with keyword stream is listening for, but not including 
        a time and room. Should not get @ mention.
        """
        # user sends a tweet containing the correct keyword but not 
        s_tweet = "test 1: {}".format(self.keyword)
        self.s_bot.tw_api.update_status(s_tweet)
        time.sleep(5)

        # no action should be taken by l_bot, checking that no retweets sent
        l_tweets = self.l_bot.get_tweets()
        self.assertEqual(len(l_tweets), 0)

        self.s_bot.clean_tweets()

    def test_correct_keyword_with_room_time(self):
        """
        Send a tweet with room and time that should get @ mention. 
        """
        s_tweet = "test 2: {} @ 6pm room H112".format(self.keyword)
        self.s_bot.tw_api.update_status(s_tweet)
        time.sleep(5)

        l_tweets = self.l_bot.get_tweets()
        self.assertEqual(len(l_tweets), 1)

        mention = "@{}".format(self.s_bot.user_info["screen_name"])
        self.assertIn(mention, l_tweets[0]._json["text"])

        self.s_bot.clean_tweets()
        self.l_bot.clean_tweets()

