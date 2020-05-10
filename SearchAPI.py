# Import the Twython class
from twython import Twython
import json
import csv
import pandas as pd
import random

# Load credentials from json file
with open("twitter_credentials.json", "r") as file:
    creds = json.load(file)

# Instantiate an object
python_tweets = Twython(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])

# Create our query
query = {'q': 'women',
        'result_type': 'popular',
        'count': 100,
        'lang': 'en',
        }

# Search tweets
dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': []}
for status in python_tweets.search(**query)['statuses']:
    dict_['user'].append(status['user']['screen_name'])
    dict_['date'].append(status['created_at'])
    dict_['text'].append(status['text'])
    dict_['favorite_count'].append(status['favorite_count'])

# Structure data in a pandas DataFrame for easier manipulation
df = pd.DataFrame(dict_)
df.sort_values(by='favorite_count', inplace=True, ascending=False)
df.to_csv('womentech_tweets.csv')

# import our data from the "saved_tweets.csv" file, sampling only 30 observatons and print out a few rows

n = sum(1 for line in open("womentech_tweets.csv")) #number of records in file
s = 20 #desired sample size
skip = sorted(random.sample(range(n),n-s))
tweets = pd.read_csv("womentech_tweets.csv", skiprows=skip)
print(tweets.head(20))
