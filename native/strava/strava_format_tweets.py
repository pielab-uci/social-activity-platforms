# strava_format_tweets.py
import pandas as pd
import numpy as np
import ast

## HELPER FUNCTIONS ##
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
    # GET RAW DATA
    raw_df = pd.read_csv(file)
    
    # FORMATTING & FILTER COLUMNSs
    # Rename id, url, and media column
    rename_dict = {'id': 'tweet_id', 'expanded_url': 'strava_link', 'media_count': 'photos_count'}
    strava_tweets_df = raw_df.rename(columns = rename_dict)
    
    filter_cols = ['tweet_id', 'author_id', 'created_at', 'text', 'public_metrics', 'photos_count', 'conversation_id', 'strava_link']
    strava_tweets_df = strava_tweets_df[filter_cols]  

    # Breaking public metrics into 4 columns 'like_count', 'has_likes', 'reply_count', 'has_replies'
    strava_tweets_df['like_count'] = strava_tweets_df.apply(lambda row: _get_like_count(row), axis = 1)
    strava_tweets_df['has_likes'] = strava_tweets_df.apply(lambda row: 1 if row.like_count else 0, axis = 1)
    strava_tweets_df['reply_count'] = strava_tweets_df.apply(lambda row: _get_reply_count(row), axis = 1)
    strava_tweets_df['has_replies'] = strava_tweets_df.apply(lambda row: 1 if row.reply_count else 0, axis = 1)
    strava_tweets_df = strava_tweets_df.drop(columns = ['public_metrics'])

    # Filter out any tweets with no public metrics
    strava_tweets_df = strava_tweets_df.dropna(subset=['like_count']) 
    strava_tweets_df = strava_tweets_df.dropna(subset=['reply_count']) 

    return strava_tweets_df