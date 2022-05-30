# mymaprun_format_tweets.py
import pandas as pd
import json
import time
import numpy as np
import ast
import re

def _get_photo_count(row):
  '''
  Given a tweet row, returns the photos count of
  the tweet based off the attachments field
  '''
  if type(row['attachments']) != str:
    return 0
  d = ast.literal_eval(row['attachments'])
  if 'media_keys' in d:
    return len(d['media_keys'])
  else:
    return 0

def _get_like_count(row):
  '''
  Given a tweet row, returns the like count of
  the tweet based off the attachments field
  '''
  try:
    return ast.literal_eval(row.public_metrics)['like_count']
  except:
    return np.NaN

def _get_reply_count(row):
  '''
  Given a tweet row, returns the like count of
  the tweet based off the attachments field
  '''
  try:
    return ast.literal_eval(row.public_metrics)['reply_count']
  except:
    return np.NaN

## MAIN FORMAT FUNCTION ##
def get_formatted_data(file):
    '''
    Returns the formatted strava df of the 
    given file
    '''
    # uncomment for testing purposes: 
    # pd.set_option('display.max_columns', None)
    # GET RAW DATA
    raw_df = pd.read_csv(file)

    # FORMATTING & FILTER COLUMNS
    # Rename id, url, and media column
    rename_dict = {'id': 'tweet_id', 'expanded_url': 'mapmyrun_link', 'media_count': 'photos_count'}
    mymaprun_tweets_df = raw_df.rename(columns = rename_dict)
    
    # Filter down to only the columns we care about from the raw data set
    filter_cols = ['tweet_id', 'author_id', 'created_at', 'text', 'public_metrics', 'photos_count', 'conversation_id', 'mapmyrun_link']
    mymaprun_tweets_df = mymaprun_tweets_df[filter_cols]
        
    # Filter out any tweets with no public metrics
    mymaprun_tweets_df = mymaprun_tweets_df.dropna(subset=['public_metrics'])

    # Breaking public metrics into 4 columns 'like_count', 'has_likes', 'reply_count', 'has_replies'
    mymaprun_tweets_df['like_count'] = mymaprun_tweets_df.apply(lambda row: _get_like_count(row), axis = 1)
    mymaprun_tweets_df['has_likes'] = mymaprun_tweets_df.apply(lambda row: 1 if row.like_count else 0, axis = 1)
    mymaprun_tweets_df['reply_count'] = mymaprun_tweets_df.apply(lambda row: _get_reply_count(row), axis = 1)
    mymaprun_tweets_df['has_replies'] = mymaprun_tweets_df.apply(lambda row: 1 if row.reply_count else 0, axis = 1)
    mymaprun_tweets_df = mymaprun_tweets_df.drop(columns = ['public_metrics'])

    # Filter out any tweets with no public metrics
    mymaprun_tweets_df = mymaprun_tweets_df.dropna(subset=['like_count'])
    mymaprun_tweets_df = mymaprun_tweets_df.dropna(subset=['reply_count'])

    return mymaprun_tweets_df