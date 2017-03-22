import tweepy
import twotebotapp.secrets as s 
import json
from sutime import SUTime
from twotebotapp import models

class StreamListener(tweepy.StreamListener):
    """
    Object that defines the callback actions passed to tweepy.Stream 
    """

    def on_status(self, status):
        # include logic for what bot should do when it recives a tweet 
        # save tweet to StreamTweet model
        # on model save use signal to fire the date parsing action and make decision there 
        # wheter to save tweet to OutgoingTweet model 

        user, created = models.User.objects.get_or_create(id_str=str(status.user.id))
        user.verified = status.user.verified  # v4
        user.time_zone = status.user.time_zone  # v4
        user.utc_offset = status.user.utc_offset  # -28800 (v4)
        user.protected = status.user.protected  # v4
        user.location = status.user.location  # Houston, TX  (v4)
        user.lang = status.user.lang  # en  (v4)
        user.screen_name = status.user.screen_name
        user.followers_count = status.user.followers_count
        user.statuses_count = status.user.statuses_count
        user.friends_count = status.user.friends_count
        user.favourites_count = status.user.favourites_count
        user.save()

        # save tweet record to Streamed tweet model
        tweet_record, created = models.StreamedTweet.objects.get_or_create(id_str=status.id_str)
        tweet_record.id_str = status.id_str
        tweet_record.user = user
        tweet_record.favorite_count = status.favorite_count
        tweet_record.text = status.text
        tweet_record.source = status.source
        tweet_record.save()

        
        
    def on_error(self, status_code):
        if status_code == 420:
            return False


def setup_auth():
    """
    Set up auth stuff for api and return tweepy api object
    """
    auth = tweepy.OAuthHandler(s.CONSUMER_KEY, s.CONSUMER_SECRET)
    auth.set_access_token(s.ACCESS_TOKEN, s.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    return api


def run_stream():
    api = setup_auth()
    stream_listener = StreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

    stream.filter(track=["justaddzebras"])



#User(contributors_enabled=False, created_at=datetime.datetime(2017, 3, 12, 19, 52, 16), statuses_count=10, lang='en', geo_enabled=False, default_profile_image=True, is_translator=False, description=None, listed_count=0, protected=False, profile_use_background_image=True, profile_sidebar_fill_color='DDEEF6', profile_background_color='F5F8FA', screen_name='tw_testy', notifications=None, _api=<tweepy.api.API object at 0x103381be0>, profile_link_color='1DA1F2', name='tw_test', id=841013993602863104, default_profile=True, following=False, profile_image_url_https='https://abs.twimg.com/sticky/default_profile_images/default_profile_3_normal.png', favourites_count=0, profile_text_color='333333', verified=False, profile_background_tile=False, follow_request_sent=None, time_zone=None, url=None, _json={'contributors_enabled': False, 'created_at': 'Sun Mar 12 19:52:16 +0000 2017', 'profile_sidebar_border_color': 'C0DEED', 'lang': 'en', 'geo_enabled': False, 'default_profile_image': True, 'is_translator': False, 'location': None, 'following': None, 'follow_request_sent': None, 'profile_use_background_image': True, 'profile_sidebar_fill_color': 'DDEEF6', 'profile_background_color': 'F5F8FA', 'screen_name': 'tw_testy', 'notifications': None, 'profile_link_color': '1DA1F2', 'favourites_count': 0, 'id': 841013993602863104, 'default_profile': True, 'listed_count': 0, 'profile_image_url_https': 'https://abs.twimg.com/sticky/default_profile_images/default_profile_3_normal.png', 'name': 'tw_test', 'profile_text_color': '333333', 'verified': False, 'profile_background_tile': False, 'protected': False, 'profile_background_image_url': '', 'url': None, 'id_str': '841013993602863104', 'utc_offset': None, 'statuses_count': 10, 'followers_count': 0, 'description': None, 'profile_image_url': 'http://abs.twimg.com/sticky/default_profile_images/default_profile_3_normal.png', 'time_zone': None, 'profile_background_image_url_https': '', 'friends_count': 0}, id_str='841013993602863104', utc_offset=None, profile_sidebar_border_color='C0DEED', followers_count=0, location=None, friends_count=0, profile_background_image_url='', profile_background_image_url_https='', profile_image_url='http://abs.twimg.com/sticky/default_profile_images/default_profile_3_normal.png')





