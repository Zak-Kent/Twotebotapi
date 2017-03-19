from retweetbot import RetweetBot


def get_pycon_tweets():
    bot = RetweetBot()
    print(bot.get_tweets())

    if bot.tweet_list is not None:
        print(len(bot.tweet_list))

        for tweet in bot.tweet_list:
            print(tweet.text)
            room_time = bot.get_time_and_room(tweet.text)
            print(room_time)
            # will need to add check here to see if room time is usable 

if __name__ == '__main__':
    get_pycon_tweets()