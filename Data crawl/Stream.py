'''
This file collects 1% data from the twitter API
'''
import config
from pymongo import MongoClient
import tweepy
import json
import time
from datetime import datetime
from datetime import timedelta


total_time = 90  # how long program should run for (in minutes)
db_name = "stream" # Name of collection to save tweets to

# Setup database connection
client = MongoClient()
db = client.twitterdb

# Converts a tweets created_at field to a python datetime object
def convert_to_datetime(status):
    json_tweet = status._json
    json_tweet["created_at"] = datetime.strptime(json_tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    return json_tweet

# Used for streaming
class Stream(tweepy.StreamListener):
    def on_status(self, status):
        # when a new tweet comes in the stream, add to the database
        db[db_name].insert(convert_to_datetime(status))
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # disconnects the stream
            return False
        print(status_code)
        # reconnects the stream, with backoff.


auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

# Used for timing the stream to only last RUN_TIME
start_time = datetime.now()
time_end =  start_time + timedelta(minutes=total_time)

twitterStream = tweepy.Stream(auth, Stream())
twitterStream.sample(languages=["en"]) # Stream English tweets

while datetime.now() < time_end:
    # sleep 30 seconds to avoid excess loop iterations
    time.sleep(30)

twitterStream.disconnect()
print("Start Time: ", start_time)
print("End Time: ", time_end)


