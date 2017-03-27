import datetime
import sys
import time
import tweepy

from e2e_secrets import listener, sender 


class TwitterBot:
    """
    Class that helps run the actions in an end to end test of the twitter bot
    """
    def __init__(self, account):
        self.tw_api = self.setup_tw_api(account)
        self.user_id = self.get_user_id()

    def setup_tw_api(self, account):
        auth = tweepy.OAuthHandler(account["CONSUMER_KEY"], account["CONSUMER_SECRET"])
        auth.set_access_token(account["ACCESS_TOKEN"], account["ACCESS_TOKEN_SECRET"])
        return tweepy.API(auth)

    def get_user_id(self):
        return self.tw_api.me()._json["id"]

    def get_time(self):
        return datetime.datetime.utcnow()

    def sleep(self):
        time.sleep(3)

    def send_tweet(self, tweet):
        """
        Send tweet with unique datetime, write id to tweets list, and sleep.
        """
        tweet += ": {}".format(self.get_time())
        status = self.tw_api.update_status(tweet)
        # self.tweets_list.append(status._json["id"])
        self.sleep()

    # def clean_tweets(self):
    #     """
    #     Delete all tweets sent by account.
    #     """
    #     for status_id in self.tweets_list:
    #         self.tw_api.destroy_status(status_id)

    #     self.tweets_list = []

    def clean_tweets(self):
        """
        Get 20 most recent tweets from user and delete 
        """
        tweets = self.tw_api.user_timeline(self.user_id)
        tweet_ids = [status._json["id"] for status in tweets]

        for tw_id in tweet_ids:
            self.tw_api.destroy_status(tw_id)


def test_listening_on_stream_works(bot, keyword):
    """
    Send a tweet with keyword stream is listening for, test that stream picks 
    up tweet and saves it to Django db.
    """
    # tweet doesn't meet room schedule criteria so should only be saved 
    # tweet = "fake tweet: {}".format(keyword)
    # bot.send_tweet(tweet)

    # maybe drop all of this and test only from the perspective of someone 
    # looking at twitter form the outside 
    




def interface(keyword):
    """
    interface that starts the end to end testing
    """
    bot = TwitterBot(listener)
    # bot2 = TwitterBot(sender)

    # bot.send_tweet("send 3")
    # bot.send_tweet("send 3")
    # bot.send_tweet("send 3")
    # bot.clean_tweets()

    print(keyword)
    print(bot.user_id)

    bot.clean_tweets()

    # test_listening_on_stream_works(1, 4)

    return 


def cli_interface():
    """
    wrapper_cli method that interfaces from commandline to function space
    call the script with: 
    python end_to_end.py <keyword: Should be keyword stream is filtering on> 
    """
    try:
        keyword = sys.argv[1]

    except:
        print("usage: {} <keyword stream is filering on>".format(sys.argv[0]))
        sys.exit(1)
    interface(keyword)


if __name__ == "__main__":
    cli_interface()