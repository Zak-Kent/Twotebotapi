import datetime
from django.test import TestCase
from freezegun import freeze_time

from twotebotapp.bot_utils import db_utils, tweet_utils, time_utils
from twotebotapp.models import Tweets, AppConfig


class TestDBUtils(TestCase):
    """Test the utility funcs created to help bot interact with Django models"""

    def setUp(self):
        AppConfig.objects.create(auto_send=True, 
                                default_send_interval=1, ignore_users=[12345,])

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

    # def test_get_or_create_user_and_tweet_saves_correctly(self):
    #     pass


class TestTweetUtils(TestCase):
    """Test that the Tweet utils funcs behave as expected in isolation"""

    def test_get_time_and_room_correctly_returns_time_room_obj(self):
        tweet = "a test tweet R123 2:05pm"

        # what SUTime returns when it parses time in tweet
        extracted_time = [
                            {
                            'type': 'TIME', 
                            'end': 24, 
                            'text': '2:05pm', 
                            'value': '2017-04-11T14:05', 
                            'start': 18
                            }
                          ]
        expected_output = {'room': ['r123'], 'date': ['2017-04-11T14:05']}

        result = tweet_utils.get_time_and_room(tweet, extracted_time)
        self.assertEqual(result, expected_output)

    @freeze_time("2017-08-05")
    def test_schedule_tweets_saves_legit_tweets_to_db(self):
        # need to setup a fake app config object
        AppConfig.objects.create(auto_send=True, 
                                default_send_interval=1, 
                                ignore_users=[12345,])

        # building args for schedule tweets
        screen_name = "tw_testy"
        tweet = "a test tweet"
        tweet_id = 123456
        talk_time = datetime.datetime.now()

        tweets_in_db_before = Tweets.objects.all()
        self.assertEqual(len(tweets_in_db_before), 0)

        tweet_utils.schedule_tweets(screen_name, tweet, tweet_id, talk_time)

        tweets_in_db_after = Tweets.objects.all()
        self.assertEqual(len(tweets_in_db_after), 2)


