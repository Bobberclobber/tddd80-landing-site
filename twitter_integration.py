CONSUMER_KEY = 'z6oJgiVEoqJcPcSvDXFSQ'
CONSUMER_SECRET = '9U6NNVoJLjjw1KwXDOdJ7R5vlOk8q7TdFEN9zQpbE'
ACCESS_TOKEN_KEY = '2326990880-nZQPGOH3HhWFgj0PsYYqI4NDeUBOWSz4lqM7xco'
ACCESS_TOKEN_SECRET = 'iLZtouAlfA5wyejJc5aWn1LHwmLmDYfy5nAgInXgA2Da5'

__author__ = 'josfa'

from TwitterAPI import TwitterAPI
from flask import Flask

app = Flask(__name__)
app.debug = True
api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)


# Posts a tweet on twitter
def tweet(f_name, l_name, registered_people):
    reg_nr = "th"
    if registered_people == 1:
        reg_nr = "st"
    elif registered_people == 2:
        reg_nr = "nd"
    elif registered_people == 3:
        reg_nr = "rd"
    msg = f_name + " " + l_name + " is the " + str(
        registered_people) + reg_nr + " person to register interest for Agora! #Agora"

    post_tweet = api.request('statuses/update', {'status': msg})
    print(post_tweet.status_code)


# Creates a list where each list item is a dict containing a user name, a url and a tweet
def get_tweet_list():
    tweet_list = []
    get_tweets = api.request('search/tweets', {'q': '#Agora'})
    for item in get_tweets.get_iterator():
        user = item['user']['screen_name']
        user_url = "https://twitter.com/" + user
        text = item['text']
        tweet_list += [{'user': user, 'user_url': user_url, 'text': text}]
    return tweet_list[:11]
