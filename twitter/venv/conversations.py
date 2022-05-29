import os
import config
import json
import requests
import time
import collection_analysis


def conv_collection_loop(conv_ids: list):
    for id in conv_ids:
        print(id, conv_ids.index(id))
        time.sleep(0.75)
        with open('/Users/mykytaturpitka/Desktop/PIE_Lab/Dribbble conversations/{}.json'.format(id), 'w+') as f:
            json.dump(make_conv_request(id), f)
            print('done')


def make_conv_request(id):
    headers = {"Authorization": "Bearer {}".format(config.BEARER_TOKEN_DENNIS)}
    url = "https://api.twitter.com/2/tweets/search/all?query=conversation_id:{}" \
          "&tweet.fields=in_reply_to_user_id,author_id,created_at,conversation_id" \
          "&start_time=2009-10-01T00:00:00Z&end_time=2022-02-17T12:00:01Z".format(id)
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 429:
        print('Rate limit exhausted, pausing for 15 minutes')
        time.sleep(900)
        response = requests.request("GET", url, headers=headers)
    print(dict(response.json()))
    return response.json()


if __name__ == '__main__':
    directory = r'/Users/mykytaturpitka/Desktop/PIE_Lab/Dribbble/'
    ids = list(collection_analysis.united_dataframe(directory).conversation_id.unique())
    conv_collection_loop(ids)


921