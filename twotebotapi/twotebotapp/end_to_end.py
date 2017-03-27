import datetime
import sys
import tweepy

from e2e_secrets import listener, sender 


class UtilitySubClass:
    """
    collection of utility methods needed in the class that runs the e2e tests
    """

    def __init__(self):
        return

    def get_time(self):
        return datetime.datetime.utcnow()

    def setup_tw_api(self, api):
        auth = tweepy.OAuthHandler(api["CONSUMER_KEY"], api["CONSUMER_SECRET"])
        auth.set_access_token(api["ACCESS_TOKEN"], api["ACCESS_TOKEN_SECRET"])
        return tweepy.API(auth)

    def update_status(self, api, tweet):
        api.update_status(tweet)
        return 

class EndToEnd(UtilitySubClass):
    """
    Class that helps run the actions in an end to end test of the twitter bot
    """

    def __init__(self):
        self.tw_listener = self.setup_tw_api(listener)








def interface(hashtag):
    print(hashtag)
    test = EndToEnd()

    return 


def cli_interface():
    """
    wrapper_cli method that interfaces from commandline to function space
    call the script with: 
    python end_to_end.py <hashtag: Should be hashtag stream is filtering on> 
    """
    try:
        hashtag = sys.argv[1]

    except:
        print("usage: {} <hashtag stream is filering on>".format(sys.argv[0]))
        sys.exit(1)
    interface(hashtag)


if __name__ == "__main__":
    cli_interface()