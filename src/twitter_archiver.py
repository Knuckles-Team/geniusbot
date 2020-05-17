#https://pypi.org/project/twitter-scraper/
from twitter_scraper import get_tweets

for tweet in get_tweets('realdonaldtrump', pages=1):
    print(tweet['text'])