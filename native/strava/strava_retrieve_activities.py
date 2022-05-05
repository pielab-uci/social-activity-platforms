# strava_retrieve_activities.py
import pandas as pd
import json
from scraper_api import ScraperAPIClient
from collections import defaultdict
import concurrent.futures
import re
import strava_metadata

CLIENT = ScraperAPIClient('API Key')
NUM_RETRIES = 2
NUM_THREADS = 50


## HELPER FUNCTIONS ##
def _get_raw_text(body):
  '''
  Gets the raw text of a comment 
  given the comment body
  '''
  raw_text = ''
  for d in body:
    raw_text += d['text']
  return raw_text

def _get_adjusted_text(body):
  '''
  Returns the adjusted text version
  of the comment given the comment body
  '''
  adjusted_text = ''
  mention_count = 0
  for d in body:
    if d['type'] == 'mention_token':
      adjusted_text += '@'
      mention_count += 1
    adjusted_text += d['text']
  return adjusted_text, mention_count

def _get_comment_dict(body):
  '''
  Formats and returns the comment
  body as a dictionary
  '''
  comment_dict = dict()
  comment_dict['raw_text'] = _get_raw_text(body)
  comment_dict['adjusted_text'], comment_dict['mention_count'] = _get_adjusted_text(body)
  return comment_dict

def _get_athlete_id(athlete):
  '''
  Returns the athelete id given 
  the athlete dictionary
  '''
  url = athlete['followAthleteUrl']
  athlete_id = re.search('athlete_id=(\d+)&', url).group(1)
  return int(athlete_id)

def _get_comments(comments):
  '''
  Returns the comments as a 
  dictionary given the list of comments
  '''
  comments_dict = defaultdict(list)
  for comment in comments:
    comments_dict[comment['athlete_id']].append(_get_comment_dict(comment['body']))
  return dict(comments_dict)

def _form_row_as_list(activity_dict):
  '''
  Returns the given activity dict as a list 
  representing a row in dataframe
  '''
  comments = _get_comments(activity_dict['comments'])
  return [activity_dict['date'], 0 if activity_dict['kudosCount'] == 0 else 1, activity_dict['kudosCount'], 0 if activity_dict['commentCount'] == 0 else 1,
          activity_dict['commentCount'], len(comments), comments, 
          activity_dict['name'], activity_dict['activity_description'], activity_dict['photos_count'], activity_dict['achievementsCount'], 
          _get_athlete_id(activity_dict['athlete']), activity_dict['athlete']['followersCount']]

def _scrape_strava_activity(tweet_id, strava_link):
  '''
  If strava_link leads to public activity, returns the list 
  formatted row of all the activity data, otherwise, returns
  None if private or handled an unexpected exception
  '''
  try:
    source = CLIENT.get(strava_link, retry = NUM_RETRIES).text
    match = re.search('strava\.com\/activities\/(\d+)', source)
    if match != None:
      activity = strava_metadata.get_activity(source)
      print(f'{strava_link} scraped successfully')
      return [match.group(1), tweet_id] + _form_row_as_list(activity)
    else:
      print(f'{strava_link} is private or not found')
      return None
  except Exception as e:
    print(f'***tweet_id [{tweet_id}] with link [{strava_link}] caused exception: {e}***')
    return None

## PRIMARY RETRIEVAL FUNCTION ##
def retrieve_activities(df):
    '''
    Given a df of strava tweets, returns a 
    df with the correlating strava activities data
    '''
    cols = ['strava_activity_id', 'matching_tweet_id', 'created_at', 'has_kudos','kudos_count', 
            'has_comments', 'comment_count', 'unique_comment_count',
            'comments','activity_title','activity_description', 'photos_count', 
            'achievements_count','athlete_id','athlete_followers_count']

    executor_thread = concurrent.futures.ThreadPoolExecutor(max_workers = NUM_THREADS) # Use Threadpool to speed up data collection process
    strava_activity_data_list = []

    for res in executor_thread.map(_scrape_strava_activity, df['tweet_id'], df['strava_link']):
        if res != None:
          strava_activity_data_list.append(res)
    
    strava_activities = pd.DataFrame(strava_activity_data_list, columns = cols)
    
    return strava_activities

