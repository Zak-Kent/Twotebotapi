from nltk import word_tokenize
import re


def get_time_and_room(tweet, extracted_time):
    """Get room number from a tweet while ignoring the time that was extracted
    using SUTime. extracted_time should be equal to the object SUTime parsed 
    """
    result = {}
    result["date"] = []
    result["room"] = []

    tweet_without_time = tweet

    for time_slot in extracted_time:
        tweet_without_time = tweet_without_time.replace(time_slot["text"], "")
        result["date"].append(time_slot.get("value"))
    
    # filter_known_words = [word.lower() for word in word_tokenize(tweet_without_time) if word.lower() not in (self.stopwords + nltk.corpus.words.words())]
    filter_known_words = [word.lower() for word in word_tokenize(tweet_without_time)]

    # regular expression for room
    room_re = re.compile("([a-zA-Z](\d{3})[-+]?(\d{3})?)")

    for word in filter_known_words:
        if room_re.match(word):
            result["room"].append(room_re.match(word).group())

    return result