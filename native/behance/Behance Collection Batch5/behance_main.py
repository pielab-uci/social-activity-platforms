# behance_main.py
import os
import pandas as pd
import re
import behance_format_tweets
import behance_retrieve_projects

directory = 'Raw Behance Tweets/'
for filename in os.listdir(directory):

    # Get file_num
    file_num = re.search('behance_tweets(\d+)', filename).group(1)
    
    # Get full file path
    full_path = os.path.join(directory, filename)

    # Get formatted_df
    formatted_df = behance_format_tweets.get_formatted_data(full_path)
    # print(formatted_df)

    # Get correlating behance projects df
    behance_projects = behance_retrieve_projects.retrieve_projects(formatted_df)

    # Updated tweets df
    matching_tweet_ids = list(behance_projects['matching_tweet_id'])
    boolean_series = formatted_df.tweet_id.isin(matching_tweet_ids)
    updated_behance_tweets = formatted_df[boolean_series]
    updated_behance_tweets.reset_index(inplace = True, drop = True)
    
    # Create behance_projects[file_num].csv
    behance_projects.to_csv(f'Behance Projects/behance_projects{file_num}.csv')
    # Create behance_tweets[file_num].csv
    updated_behance_tweets.to_csv(f'Behance Tweets/behance_tweets{file_num}.csv')

    print(f'=== FINISHED WITH {filename} ===')
