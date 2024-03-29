import os
import tweepy
from scraping.services import logger

consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def tweet(msg, in_reply_to_status_id=None):
    logger.info(f"tweet: `{msg}`")
    return api.update_status(msg, in_reply_to_status_id=in_reply_to_status_id)
