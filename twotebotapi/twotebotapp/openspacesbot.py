from twotebotapp.retweetbot import RetweetBot


def get_pycon_tweets():
    bot = RetweetBot()
    print(bot.get_tweets())

    if bot.tweet_list is not None:
        print(len(bot.tweet_list))

