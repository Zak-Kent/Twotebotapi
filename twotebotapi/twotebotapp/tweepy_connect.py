import tweepy
from . import secrets  


def get_api():
    auth = tweepy.OAuthHandler(secrets.CONSUMER_KEY, secrets.CONSUMER_SECRET)
    auth.set_access_token(secrets.ACCESS_TOKEN, secrets.ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)

def tweepy_send_tweet(tweet):
    api = get_api()
    status = api.update_status(status=tweet)
    return None

def tweepy_send_dm(user_id, tweet):
    api = get_api()
    dm = api.send_direct_message(user_id, tweet)
    return None