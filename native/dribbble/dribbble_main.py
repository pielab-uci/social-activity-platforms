# dribbble_main.py
import os
import pandas as pd
import dribbble_format_tweets
import dribbble_retrieve_shots
import re


directory = 'Raw Dribbble Tweets/'
filename = os.listdir(directory)[0] # Get the first file in directory

# Get file_num
file_num = re.search('dribbble_tweets(\d+)', filename).group(1)

# Get full file path
full_path = os.path.join(directory, filename)

# Get formatted_df
formatted_df = dribbble_format_tweets.get_formatted_data(full_path)

# Get correlating dribbble shots df
dribbble_shots, hitRateLimit = dribbble_retrieve_shots.retrieve_shots(formatted_df, file_num)

# Update tweets df
matching_tweet_ids = list(dribbble_shots['matching_tweet_id'])
boolean_series = formatted_df.tweet_id.isin(matching_tweet_ids)
updated_dribbble_tweets = formatted_df[boolean_series]
updated_dribbble_tweets.reset_index(inplace = True, drop = True)

if not hitRateLimit:
    # Create dribbble_shots[file_num].csv
    dribbble_shots.to_csv(f'Dribbble Shots/dribbble_shots{file_num}.csv')
    # Create dribbble_tweets[file_num].csv
    updated_dribbble_tweets.to_csv(f'Dribbble Tweets/dribbble_tweets{file_num}.csv')
    print(f'=== FINISHED WITH {filename} ===')
else:
    print('saving scraped info so far')
    # Create dribbble_shots[file_num]_partial.csv
    dribbble_shots.to_csv(f'Dribbble Shots/dribbble_shots{file_num}_partial.csv')
    # Create dribbble_tweets[file_num]_partial.csv
    updated_dribbble_tweets.to_csv(f'Dribbble Tweets/dribbble_tweets{file_num}_partial.csv')

# Delete the file from Raw Dribbble Tweets if fully completed
if not hitRateLimit:
    os.remove(full_path)