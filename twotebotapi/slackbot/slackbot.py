from slacker import Slacker
from .slackbot_settings import SLACK_TOKEN  

def send_message():
    slack = Slacker(SLACK_TOKEN)

    slack.chat.post_message('#outgoing_tweets', 'Slack bot test')
