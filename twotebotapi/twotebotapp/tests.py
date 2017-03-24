from django.test import TestCase, Client
import json
from freezegun import freeze_time

# -----------------------------------
from mock import patch, Mock
# import Mock
# -----------------------------------

from .models import Tweets, AppConfig
from .tasks import beat_tweet_scheduler, tweeter
from .streambot import Streambot 

 
class TestOutBoundTweetsEndpoint(TestCase):
    """
    Simple test of endpoint that front end will use to display info about tweets
    """
    fixtures = ["test_fixture"] 
    
    def setUp(self):
        self.c = Client()

    def api_call(self, url):
        response = self.c.get(url)
        json_response = json.loads(response.content.decode('utf-8'))
        return json_response

    def test_get_sends_200(self):
        response = self.c.get("/twitter/tweets/")
        self.assertEqual(response.status_code, 200)

    def test_filter_tweets_by_approved_field(self):
        json_response = self.api_call("/twitter/tweets/?approved=1")
        # 6 tweets in fixture are approved 
        self.assertEqual(len(json_response), 6)

    def test_filter_tweets_waiting_to_be_sent(self):
        json_response = self.api_call("/twitter/tweets/?pending=True")
        # 4 pending tweets in fixture
        self.assertEqual(len(json_response), 4)

    def test_filtering_tweets_with_both_query_params(self):
        json_one = self.api_call("/twitter/tweets/?pending=True&approved=0")
        json_two = self.api_call("/twitter/tweets/?approved=0&pending=True")
        self.assertEqual(json_one, json_two)
        # 2 tweets in fixture match query
        self.assertEqual(len(json_one), 2)


class TestTweetModelSaveMethod(TestCase):
    """
    Test to check that model calcs the scheduled_time field when a tweet 
    object is approved to be sent. 
    """

    def setUp(self):
        AppConfig.objects.create(auto_send=True, default_send_interval=1)

    def test_approved_tweet_gets_scheduled_time_auto_calculated(self):
        Tweets.objects.create(tweet="test tweet", approved=1)
        my_tweet = Tweets.objects.get(tweet="test tweet")

        self.assertEqual(bool(my_tweet.scheduled_time), True)

    def test_non_approved_tweet_gets_no_scheduled_time(self):
        Tweets.objects.create(tweet="non approved tweet", approved=0)
        pending_tweet = Tweets.objects.get(tweet="non approved tweet")

        self.assertEqual(bool(pending_tweet.scheduled_time), False)

    def test_tweet_gets_schedulec_time_when_approved_set_to_true(self):
        """
        A tweet object is created and is pending approval, later it is changed
        to approved and has it's scheduled time is calculated when approved. 
        A tweets scheduled time will only be calculated when the model's save
        method is called. 
        """
        pending_tweet = Tweets.objects.create(tweet="pending tweet", approved=0)
        self.assertEqual(bool(pending_tweet.scheduled_time), False)

        # pending_tweet is approved by user
        pending_tweet.approved = 1
        pending_tweet.save()

        self.assertEqual(bool(pending_tweet.scheduled_time), True)


class TestCeleryTasks(TestCase):
    """
    Check that the celery tasks perform as expected in isolation
    """

    def setUp(self):
        AppConfig.objects.create(auto_send=True, default_send_interval=1)

    @freeze_time("2017-03-03")
    def test_beat_tweet_scheduler_schedules_correct_tweets(self):
        """
        Test that a tweet scheduled to be sent within the beat_tweet_scheduler
        time range is scheduled and added its task_scheduled flag is set to True
        """
        Tweets.objects.create(tweet="test time tweet", approved=1)

        # task is wating to be scheduled in DB so task_scheduled flag = False
        pre_scheduled = Tweets.objects.get(tweet="test time tweet")
        self.assertEqual(pre_scheduled.task_scheduled, False)

        beat_tweet_scheduler()

        post_scheduled = Tweets.objects.get(tweet="test time tweet")
        self.assertEqual(post_scheduled.task_scheduled, True)

    @freeze_time("2017-03-03")
    def test_tweeter_sends_tweet_and_sets_field(self):
        """
        Test that tweeter task sends tweet and writes sent time to Tweet obj
        """
        # create tweet to be sent
        outgoing = Tweets.objects.create(tweet="tweet in tweeter", approved=1, 
                                         task_scheduled=True)
        self.assertEqual(bool(outgoing.sent_time), False)

        tweeter(outgoing.tweet, outgoing.id)

        sent = Tweets.objects.get(pk=outgoing.id)
        self.assertEqual(bool(sent.sent_time), True)

