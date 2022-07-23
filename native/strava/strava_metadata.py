import re
import json
from collections import defaultdict
import pandas as pd
from bs4 import BeautifulSoup

def _parse_activity_info(public_info, activity_description):
  '''
  Returns a dictionary of desired parsed out information
  from the activity
  '''
  full_activity_info = json.loads(public_info.attrs['data-react-props'])
  activity_info = full_activity_info['activity']
  
  keys = ['name', 'achievementsCount', 'athlete', 'commentCount', 'comments', 'kudosCount', 'date']
  activity_dict = {prop : activity_info[prop] for prop in keys}
  activity_dict['photos_count'] = len(full_activity_info['photos'])
  activity_dict['activity_description'] = activity_description
  
  return activity_dict

def get_activity(source_text):
  '''
  Returns the activity as a dictionary of 
  its info if public. Returns None if 
  the activity is private.
  '''
  soup = BeautifulSoup(source_text, "lxml")
  description_prop = soup.find(attrs = {'property': 'og:description'})
  if description_prop != None and 'content' in description_prop.attrs:
    activity_description = description_prop.attrs['content']
  else:
    activity_description = ''
  public_info = soup.find('div', {'data-react-class': 'ActivityPublic'})
  if public_info != None:
    activity = _parse_activity_info(public_info, activity_description)
    return activity
  return None

