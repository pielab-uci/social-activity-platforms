import os
import config
import json
import requests
import time
import collection_analysis


def conv_collection_loop(conv_ids: set):
    #In case of error, replace 0 with the latest collected index found in console printout
    for id in conv_ids[0:]:
        print(id, conv_ids.index(id))
        time.sleep(1.1)
        current_token = config.BEARER_TOKEN_DANIEL
        #Specify the directory to store the conversations in the string below
        with open('/Users/mykytaturpitka/Desktop/PIE_Lab/MMR conversations/{}.json'.format(id), 'w+') as f:
            json.dump(make_conv_request(id, current_token), f)
            print('done')


def make_conv_request(id, token):
    headers = {"Authorization": "Bearer {}".format(token)}
    url = "https://api.twitter.com/2/tweets/search/all?query=conversation_id:{}" \
          "&tweet.fields=in_reply_to_user_id,author_id,created_at,conversation_id" \
          "&start_time=2009-10-01T00:00:00Z&end_time=2022-02-17T12:00:01Z".format(id)
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 429:
        if token == config.BEARER_TOKEN_DANIEL:
            headers = {"Authorization": "Bearer {}".format(config.BEARER_TOKEN_DENNIS)}
        else:
            headers = {"Authorization": "Bearer {}".format(config.BEARER_TOKEN_DANIEL)}
            print('switching tokens')
        response = requests.request("GET", url, headers=headers)
    return response.json()


if __name__ == '__main__':
    #Specify the directory with the .csv files below
    directory = r'/Users/mykytaturpitka/Desktop/PIE_Lab/MapMyRun/'

    united_df = collection_analysis.united_dataframe(directory)
    tweets = collection_analysis.tweet_array(united_df)
    has_replies = []
    for t in tweets:
        has_replies.append(t.has_replies())
    united_df.insert(11, "has_replies", has_replies, True)

    has_replies_df = united_df[united_df.has_replies != 0]
    print(has_replies_df.tail())
    ids = list(has_replies_df.conversation_id.unique())
    conv_collection_loop(ids)