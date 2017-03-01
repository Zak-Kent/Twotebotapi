from django.test import TestCase, Client
# from unittest.mock import MagicMock
# from django.db.models import signals
import json

from .models import Tweets, AppConfig

        
class OutBoundTweetsEndpoint(TestCase):
    """
    Simple test of endpoint that front end will use to display info about tweets
    """
    fixtures = ["TEST_FIXTURE"] 
    
    def setUp(self):
        self.c = Client()

    def test_get_sends_200(self):
        response = self.c.get("/twitter/tweets/")
        self.assertEqual(response.status_code, 200)

    def test_filter_tweets_by_those_needing_approval(self):
        response = self.c.get("/twitter/tweets/?approved=null")
        print(response)














