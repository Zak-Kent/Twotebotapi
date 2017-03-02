from django.test import TestCase, Client
import json

from .models import Tweets, AppConfig
from mock import patch

        
class OutBoundTweetsEndpoint(TestCase):
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


    @patch(".task.datetime.utcnow")
    def test_scheduler(self, fakeutc):
        fakeutc.return_value = "add datetime object"

        












