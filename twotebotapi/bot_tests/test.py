from django.test import TestCase

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
        print("setup run")

    def test_schedule_tweets_saves_tweets_to_db(self):
        print(AppConfig.objects.latest("id"))

