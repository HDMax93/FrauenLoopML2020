from twython import TwythonStreamer
import csv
import json
import pandas as pd
import random

# Load credentials from json file
with open("twitter_credentials.json", "r") as file:
    creds = json.load(file)

# Filter out unwanted data
def process_tweet(tweet):
    d = {}
    d['hashtags'] = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]
    d['text'] = tweet['text']
    d['user'] = tweet['user']['screen_name']
    d['user_loc'] = tweet['user']['location']
    return d


# Create a class that inherits TwythonStreamer
class MyStreamer(TwythonStreamer):

    # Received data
    def on_success(self, data):

        # Only collect tweets in English
        if data['lang'] == 'en':
            tweet_data = process_tweet(data)
            self.save_to_csv(tweet_data)

    # Problem with the API
    def on_error(self, status_code, data):
        print(status_code, data)
        self.disconnect()

    # Save each tweet to csv file
    def save_to_csv(self, tweet):
        with open(r'saved_tweets.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow(list(tweet.values()))


# Instantiate from our streaming class
stream = MyStreamer(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'],
                    creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
# Start the stream
stream.statuses.filter(track='women tech')

# import our data from the "saved_tweets.csv" file, sampling only 30 observatons and print out a few rows

n = sum(1 for line in open("saved_tweets.csv")) #number of records in file
s = 30 #desired sample size
skip = sorted(random.sample(range(n),n-s))
tweets = pd.read_csv("saved_tweets.csv", skiprows=skip)
tweets.head()

# What are the most common hashtags that go with our keywords "women tech"?
from collections import Counter
import ast

# Extract hashtags and put them in a list
list_hashtag_strings = [entry for entry in tweets.hashtags]
list_hashtag_lists = ast.literal_eval(','.join(list_hashtag_strings))
hashtag_list = [ht.lower() for list_ in list_hashtag_lists for ht in list_]

# Count most common hashtags
counter_hashtags = Counter(hashtag_list)
counter_hashtags.most_common(20)

# Next, we can use the user location to answer - which areas of the world tweet most about "women tech"?

from geopy.geocoders import Nominatim
import gmplot

geolocator = Nominatim()

# Go through all tweets and add locations to 'coordinates' dictionary
coordinates = {'latitude': [], 'longitude': []}
for count, user_loc in enumerate(tweets.location):
    try:
        location = geolocator.geocode(user_loc)

        # If coordinates are found for location
        if location:
            coordinates['latitude'].append(location.latitude)
            coordinates['longitude'].append(location.longitude)

    # If too many connection requests
    except:
        pass

# Instantiate and center a GoogleMapPlotter object to show our map
gmap = gmplot.GoogleMapPlotter(30, 0, 3)

# Insert points on the map passing a list of latitudes and longitudes
gmap.heatmap(coordinates['latitude'], coordinates['longitude'], radius=20)

# Save the map to html file
gmap.draw("python_heatmap.html")
