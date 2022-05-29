import os
from Tweet import Tweet
import pandas as pd
from collections import defaultdict
import json


# Produce a complete dataframe
def united_dataframe(dr):
    dfs = []
    for filename in os.listdir(dr):
        if filename.endswith('.csv'):
            dfs.append(pd.read_csv(dr + filename, lineterminator='\n'))
    return pd.concat(dfs)


# Translate Dataframe into array of Tweet objects
def tweet_array(dataframe):
    return [Tweet(tw_record) for tw_record in dataframe.itertuples()]


# Produce tweet counts by user for user with 25+ tweets
def tweet_counts_by_user(dr):
    author_ids = defaultdict(int)
    for filename in os.listdir(dr):
        if filename.endswith('.csv'):
            df = pd.read_csv('/Users/mykytaturpitka/Desktop/PIE_Lab/Tweet Collection/' + filename, lineterminator='\n')
            for author in df['author_id']:
                author_ids[author] += 1
    return {k: v for k, v in sorted(author_ids.items(), key=lambda item: item[1], reverse=True)}


# For every user for every tweets compute how many tweets are within 30 days after
def tweets_by_author_stats(array_of_tweets, tweet_dict) -> {int: {int: int}}:
    resulting_dict = defaultdict(lambda: defaultdict(int))
    for user_id in tweet_dict.keys():
        user_tweets = [tweet for tweet in array_of_tweets if tweet.get_author_id() == user_id]
        for tweet in user_tweets:
            for compare_tweet in user_tweets[user_tweets.index(tweet):]:
                if tweet.is_within_timeframe(compare_tweet):
                    resulting_dict[user_id][tweet.get_id()] += 1
            print('tweet ' + str(tweet.get_id()) + ' completed')
        print('user ' + str(user_id) + ' completed')
    return resulting_dict


def split_df(df, size):
    chunks = []
    num_chunks = len(df) // size + 1
    for i in range(num_chunks):
        chunks.append(df[i*size:(i+1)*size])
    return chunks


# The following are two helper functions that are used to identify duplicate
# dribbble and behance posts referenced by tweets for the purpose of their
# subsequent removal. Both return a list of binary values that follow
# the order of the tweets in the dataset that is being filtered. The list is
# later added to the dataframe as a new column and the dataframe is filtered
# based on the binary values. The dribble_duplicates() function was also used
# with MapMyRun tweets.
def dribble_duplicates(tweets):
    shots_ids = defaultdict(int)
    for tw in tweets:
        try:
            shots_ids[tw.get_expanded_url().split('/')[4]] += 1
        except IndexError:
            shots_ids['no_id'] += 1
    return shots_ids


def behance_duplicates(tweets):
    cache = set()
    dupl = []
    for tw in tweets:
        try:
            if any(x in tw.get_expanded_url().split('/')[4] for x in
                   ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
                if tw.get_expanded_url().split('/')[4] in cache:
                    dupl.append(False)
                else:
                    dupl.append(True)
                    cache.add(tw.get_expanded_url().split('/')[4])
            else:
                if tw.get_expanded_url().split('/')[5] in cache:
                    dupl.append(False)
                else:
                    dupl.append(True)
                    cache.add(tw.get_expanded_url().split('/')[5])
        except IndexError:
            dupl.append(False)
    return dupl


if __name__ == '__main__':
    directory = r'/Users/mykytaturpitka/Desktop/PIE_Lab/Dribbble/'
    header = ['id', 'text', 'author_id', 'conversation_id', 'created_at', 'media_count', 'expanded_url',
              'public_metrics', 'entities', 'lang']
    united_df = united_dataframe(directory)
    splitted = split_df(united_df, 1400)
    for d in range(len(splitted)):
        splitted[d].to_csv(os.path.join('/Users/mykytaturpitka/Desktop/PIE_Lab/Dribbble1400/dribbble_tweets{}.csv'.format(str(d+1))), columns=header)

    # tweets = tweet_array(united_df)
    #
    # cache = set()
    # dupl = []
    # for tw in tweets:
    #     try:
    #         if tw.get_expanded_url().split('/')[4] in cache:
    #             dupl.append(False)
    #         else:
    #             dupl.append(True)
    #             cache.add(tw.get_expanded_url().split('/')[4])
    #     except IndexError:
    #         dupl.append(False)
    # united_df.insert(11, 'is_duplicate', dupl, True)
    # united_df = united_df[united_df.is_duplicate != False]
    # united_df = united_df.drop(columns='is_duplicate')


    # is_mrn = []
    # for tw in tweets:
    #     is_mrn.append(tw.is_myrun())
    #     print(tw.is_myrun(), tw.get_expanded_url_behance())
    # united_df.insert(11, 'is_mrn', is_mrn, True)
    #
    # united_df = united_df[united_df.is_mrn != False]
    # united_df = united_df.drop(columns='is_mrn')
    # splitted = split_df(united_df, 2000)
    # for d in range(len(splitted)):
    #     splitted[d].to_csv(os.path.join('/Users/mykytaturpitka/Desktop/PIE_Lab/MapMyRun/mapmyrun_tweets{}.csv'.format(str(d+1))), columns=header)

    # urls = []
    # for tw in tweets:
    #     urls.append(tw.get_expanded_url_behance())
    # united_df.insert(6, "expanded_url", urls, True)
    # splitted = split_df(united_df, 2000)
    # for d in range(len(splitted)):
    #     splitted[d].to_csv(os.path.join('/Users/mykytaturpitka/Desktop/PIE_Lab/MapMyRun with urls/mapmyrun_tweets{}.csv'.format(str(d+1))), columns=header)
    #
