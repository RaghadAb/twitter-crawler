'''
This is an improved version of the 'Stream.py' crawler, as it uses both the REST and the streaming API
Data is stored in mongo , but has been exported as a json file for analysis
'''
import config
import _thread
from pymongo import MongoClient
import tweepy
import time
import queue
from datetime import timedelta
from datetime import datetime

database_name = "Hybrid_Crawler"  # Name of collection to save tweets to
runT = 90  # how long program should run for (in minutes)
GeoID = 23424975  # This is the ID for the location 'UK'
ET = False  # this is a boolean to check whether the time has expired.

add_user_queue = queue.Queue()  # used for storing twitter users

# establish a connection with the database here
client = MongoClient()
db = client.twitterdb


#  created_at field is being converted to a python object
def created_at_convert(status):
    json_tweet = status._json
    json_tweet["created_at"] = datetime.strptime(json_tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    return json_tweet


class Stream(tweepy.StreamListener):
    """""
       Class for streaming live tweets 
       """""

    def on_status(self, status):
        # add user to queue then insert tweet into db
        global add_user_queue
        add_user_queue.put(status.user.id)
        db[database_name].insert(created_at_convert(status))
        return True

    # deal with error , by disconnecting from the stream
    def on_error(self, status_code):
        if status_code == 420:
            # stream is disconnected.
            return False
        print(status_code)


def update_tweets(no_tweets):  # no_ tweets is an abbreviation for Number of tweets.
    # if no tweet information is available it is set to 0
    if no_tweets is None:
        return 0
    return no_tweets


# data is added to the database for each user
def process_user(user_id):
    for status in tweepy.Cursor(api.user_timeline, id=user_id).items():
        db[database_name].insert(created_at_convert(status))
        if ET:
            break


# establishing users (thread), this is the user based probe
def get_user(thread_name):
    print(thread_name + " Started.")
    while not ET:
        if not add_user_queue.empty():
            process_user(add_user_queue.get())


# tweets based on trending topics (thread) , this is the trend based probe
def get_trend(threadName):
    print(threadName + " Running thread.")
    Geo_trend = api.trends_place(  # this ensures that trends are from the UK with the use of GeoID
        GeoID)
    uk_trends = Geo_trend[0]['current trends']  # Extract information
    top_trends = sorted(uk_trends, key=lambda k: update_tweets(k['`Number of Tweets`']),
                        reverse=True)  # sort trends by tweet volume
    for trend in top_trends:
        for status in tweepy.Cursor(api.search, q=trend["name"], count=100, lang="en").items():
            db[database_name].insert(created_at_convert(status))
            if ET:
                break
        if ET:
            break


# tokens are in a config file, since they are to be accessed separatley two times through both crawlers
auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

# the run time is specified 'runT', stream is timed here to meet the requirement
datetime_now = datetime.now()
elapsedT = datetime_now + timedelta(minutes=runT)  # elapsed time

# tweets from the english language are only extracted.
twitterStream = tweepy.Stream(auth, Stream())
twitterStream.sample(languages=["en"])

api = tweepy.API(auth, wait_on_rate_limit=True)

# User based probes and keyword based probes handled on separate threads
try:
    user_thread = _thread.start_new_thread(get_user, ("Users",))
    trend_thread = _thread.start_new_thread(get_trend, ("Top trends",))
except:
    print(" thread cannot be started")

ET = True

# Time expired
twitterStream.disconnect()
