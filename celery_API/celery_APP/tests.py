from django.test import TestCase, Client
# from unittest.mock import MagicMock
# from django.db.models import signals
import json

from .models import Tweets, AppConfig

        
class OutBoundTweetsEndpoints(TestCase):
    """
    Simple test of endpoints
    """
    fixtures = ["TEST_FIXTURE"] 
    
    def setUp(self):
        self.c = Client()
        self.put_data = {"tweet": "fake tweet", "approved": 1, "time_interval": 10}

    def test_get_sends_200(self):
        response = self.c.get("/twitter/update/1")
        self.assertEqual(response.status_code, 200)

    def test_put_sends_200(self):
        response = self.c.put("/twitter/update/2", data=json.dumps(self.put_data), \
                             content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_after_DB_change_all__approved_tweets_scheduled(self):
        # response = self.c.put("/twitter/update/2", data=json.dumps(self.put_data), \
        #                      content_type="application/json")
        # self.assertEqual(response.status_code, 200)
        tweets = Tweets.objects.filter(approved__exact=1) \
                           .filter(scheduled_time__isnull=True) 
        print(tweets)

    def test_after_DB_change_all_unapproved_tweets_not_scheduled(self):
        print("place holder")














