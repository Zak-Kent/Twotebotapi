import tweepy
import secrets as s 
from sutime import SUTime


def setup_auth():
    """
    Set up auth stuff for api and return tweepy api object
    """
    auth = tweepy.OAuthHandler(s.CONSUMER_KEY, s.CONSUMER_SECRET)
    auth.set_access_token(s.ACCESS_TOKEN, s.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    return api


class StreamListener(tweepy.StreamListener):
    """
    Object that defines the callback actions passed to tweepy.Stream 
    """

    def on_status(self, status):
        print(status.text)
        
    def on_error(self, status_code):
        if status_code == 420:
            return False


if __name__ == "__main__":
    api = setup_auth()
    stream_listener = StreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

    stream.filter(track=["justaddzebras"])









