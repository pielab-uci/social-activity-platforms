import time
import pandas as pd
import os
from retrieval_tools import make_request


# this function processes the returned data from request to twitter API
# and loads it into a .csv file to the specified directory
def request_loop(pickup):
    if pickup:
        next_token = '1jzu9lk96gu5npw2cd9khdussjw9xahnazwtik78p6d9'
    else:
        next_token = ''
    for iteration in range(1, 9999):
        df = pd.DataFrame()
        i = 0
        while i < 20:
            time.sleep(0.5)
            response = make_request(next_token)
            if response['empty']:
                response = make_request(response['next_token'])
            next_token = response['next_token']
            df = df.append(response['response_df'])
            i += 1
            df = df.loc[df['lang'] == 'en']
            header = ['id', 'text', 'author_id', 'conversation_id', 'created_at', 'media_count',
                      'public_metrics', 'entities', 'lang']
            df.to_csv(os.path.join('/Users/mykytaturpitka/Desktop/PIE_Lab/MapMyRun Tweets',
                                   'mapmyrun_tweets' + str(iteration) + '.csv'), columns=header)
            print('next token for this iteration ' + response['next_token'])
        print('done with file ', iteration)

