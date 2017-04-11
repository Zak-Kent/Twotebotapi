import datetime
from django.test import TestCase
from freezegun import freeze_time

from twotebotapp.bot_utils import db_utils, tweet_utils, time_utils
from twotebotapp.models import Tweets, AppConfig


class TestDBUtils(TestCase):
    """
    Test the utility funcs created to help bot interact with Django models
    """

    def setUp(self):
        AppConfig.objects.create(auto_send=True, 
                                default_send_interval=1, ignore_users=[12345, ])

    def test_get_ignored_users_returns_correct_list(self):
        ignore_list = db_utils.get_ignored_users()
        self.assertEqual(ignore_list, [12345, ])

    def test_check_for_auto_send_returns_auto_send_flag(self):
        auto_send_flag = db_utils.check_for_auto_send()
        self.assertEqual(auto_send_flag, 1)
    
    @freeze_time("2017-08-05")
    def test_save_outgoing_tweet_func_saves_correctly(self):
        tweet_obj = {
            "message": "a test tweet",
            "approved": 1,
            "remind_time": datetime.datetime.now()
        }

        tweets_before_save = Tweets.objects.all()
        self.assertEqual(len(tweets_before_save), 0)

        db_utils.save_outgoing_tweet(tweet_obj)

        tweets_after_save = Tweets.objects.all()
        self.assertEqual(len(tweets_after_save), 1)