from django.test import TestCase, Client
import json

class OutBoundTweetsEndpoint(TestCase):
    fixtures = ["TWEET_FIXTURE"] 
    
    def setUp(self):
        self.c = Client()


    def test_get_sends_200(self):
        response = self.c.get("/twitter/update/1")
        self.assertEqual(response.status_code, 200)

    # def test_put_sends_200(self):
    #     response = self.

    # def test_
