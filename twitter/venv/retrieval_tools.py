import requests
import config
import pandas as pd
import time
import json


def make_request(next_token='') -> dict:
    headers = {"Authorization": "Bearer {}".format(config.BEARER_TOKEN_DANIEL)}
    url = config.search_url.format('&next_token=' + next_token if next_token != '' else '')
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 429:
        print('Rate limit exhausted, pausing for 15 minutes')
        time.sleep(900)
        response = requests.request("GET", url, headers=headers)
    response_in = response.json()
    with open('latest_request.json', 'w') as f:
        json.dump(response_in, f)

    try:
        df = pd.DataFrame(response_in['data'])
    except KeyError:
        if response_in['meta']['result_count'] == 0:
            print("ANOTHER EMPTY PAGE")
            df = pd.DataFrame(columns=['test'])
            return {'response_df': df, 'next_token': response_in['meta']['next_token'], 'empty': True}
    next_token = response_in['meta']['next_token']

    attachment_counts = []
    for tw in response_in['data']:
        attachments = tw.get('attachments', False)
        if not attachments:
            attachment_counts.append(0)
        else:
            count_sum = 0
            for media in tw['attachments'].keys():
                count_sum += len(tw['attachments'][media])
            attachment_counts.append(count_sum)
    df.insert(5, "media_count", attachment_counts, True)
    return {'response_df': df, 'next_token': next_token, 'empty': False}


def get_user_follower_count(tweet) -> int:
    headers = {"Authorization": "Bearer {}".format(config.BEARER_TOKEN_DANIEL)}
    url = 'https://api.twitter.com/2/users/{}/followers'.format(tweet['author_id'])
    response = requests.request('GET', url, headers=headers)
    if response.status_code == 429:
        print('Rate limit exhausted, pausing for 15 minutes')
        time.sleep(900)
        response = requests.request("GET", url, headers=headers).json()
    else:
        response = response.json()
    return response['meta']['result_count']


def get_reply_count(tweet)-> int:
    headers = {"Authorization": "Bearer {}".format(config.BEARER_TOKEN_DENNIS)}
    url = "https://api.twitter.com/2/tweets/search/all?query=conversation_id:{}" \
          "&tweet.fields=in_reply_to_user_id,author_id,created_at,conversation_id".format(tweet.get_convo_id())
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 429:
        print('rate limit exceeded. Pausing for 15 minutes')
        time.sleep(900)
        response = requests.request("GET", url, headers=headers).json()
    else:
        response = response.json()
    return response['meta']['result_count']

