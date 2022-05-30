# mymaprun_main.py
import os
import pandas as pd
import re
import mapmyrun_format_tweets
import mapmyrun_retrieve_workouts

directory = 'Raw MapMyRun Tweets/'
for filename in os.listdir(directory):

    # Get file_num
    file_num = re.search('mapmyrun_tweets(\d+)', filename).group(1)
    
    # Get full file path
    full_path = os.path.join(directory, filename)

    # Get formatted_df
    formatted_df = mapmyrun_format_tweets.get_formatted_data(full_path)

    # Get correlating behance projects df
    mymaprun_workouts = mapmyrun_retrieve_workouts.retrieve_workouts(formatted_df, file_num)

    # Updated tweets df
    matching_tweet_ids = list(mymaprun_workouts['matching_tweet_id'])
    boolean_series = formatted_df.tweet_id.isin(matching_tweet_ids)
    updated_mymaprun_tweets = formatted_df[boolean_series]
    updated_mymaprun_tweets.reset_index(inplace = True, drop = True)
    
    # Create behance_projects[file_num].csv
    mymaprun_workouts.to_csv(f'MapMyRun Activities/mapmyrun_workouts{file_num}.csv')
    # Create behance_tweets[file_num].csv
    updated_mymaprun_tweets.to_csv(f'MapMyRun Tweets/mapmyrun_tweets{file_num}.csv')

    print(f'=== FINISHED WITH {filename} ===')