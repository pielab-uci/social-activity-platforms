# strava_main.py
import os
import pandas as pd
import re
import strava_format_tweets
import strava_retrieve_activities

directory = 'Raw Strava Tweets/'
for filename in os.listdir(directory):

    # Get file_num
    file_num = re.search('strava_tweets(\d+)', filename).group(1)
    
    # Get full file path
    full_path = os.path.join(directory, filename)

    # Get formatted_df
    formatted_df = strava_format_tweets.get_formatted_data(full_path)
    
    # Get correlating strava activities df
    strava_activities = strava_retrieve_activities.retrieve_activities(formatted_df)

    # Update tweets df
    matching_tweet_ids = list(strava_activities['matching_tweet_id'])
    boolean_series = formatted_df.tweet_id.isin(matching_tweet_ids)
    updated_strava_tweets = formatted_df[boolean_series]
    updated_strava_tweets.reset_index(inplace = True, drop = True)
    
    # Create strava_activities[file_num].csv
    strava_activities.to_csv(f'Strava Activities/strava_activities{file_num}.csv')

    # Create strava_tweets[file_num].csv
    updated_strava_tweets.to_csv(f'Strava Tweets/strava_tweets{file_num}.csv')

    print(f'=== FINISHED WITH {filename} ===')
