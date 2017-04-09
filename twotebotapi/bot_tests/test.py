from django.test import TestCase
import datetime
from freezegun import freeze_time

from newbot import BaseStreamBot
from twotebotapp.models import Tweets, AppConfig


class TestBotBaseClass(TestCase):
    """
    Tests of the base class of bot without Tweepy and SUTime stuff included
    """

    @classmethod
    def setUpClass(cls):
        super(TestBotBaseClass, cls).setUpClass()
        cls.bot = BaseStreamBot()

    def setUp(self): 
        test_conf = {
        "auto_send": 0,
        "default_send_interval": 1,
        "ignore_users": []
        }
        AppConfig.objects.create(**test_conf)

        self.screen_name = "tweepy"
        self.tweet = "test tweet"
        self.tweet_id = 12345
        self.talk_time = datetime.datetime(2017, 4, 9)
        

    def test_schedule_tweets_saves_tweets_to_db(self):
        """
        Check that a call to schedule_tweets creates the expected two tweets in db
        """
        tweets_in_db = Tweets.objects.all()
        self.assertEqual(len(tweets_in_db), 0)

        self.bot.schedule_tweets(self.screen_name, self.tweet, self.tweet_id, self.talk_time)

        tweets_in_db = Tweets.objects.all()
        self.assertEqual(len(tweets_in_db), 2)

    # @freeze_time("2017-04-09")
    def test_convert_to_utc_converts_time_correctly(self):
        """
        Convert_to_utc should take a local date and convert the given talk_time
        to same date with time offset correct
        """

        string_talk_time = self.talk_time.strftime("%Y %m %d")
        print(string_talk_time)

        self.bot.convert_to_utc(string_talk_time, None)











