# dribbble_retrieve_shots
import dribbble_metadata
import pandas as pd
import time
import re

def _form_row_as_list(shot_dict):
    '''
    Returns the given project dict as a list 
    representing a row in dataframe
    '''
    return [shot_dict['shotId'], shot_dict['postedOn'], 0 if shot_dict['likesCount'] == 0 else 1, shot_dict['likesCount'],
            0 if shot_dict['commentsCount'] == 0 else 1, shot_dict['commentsCount'], len(shot_dict['comments']), shot_dict['num_comments_retrieved'],
            shot_dict['comments'], shot_dict['title'], shot_dict['description'], shot_dict['photos_count'], shot_dict['shotUser'], shot_dict['username']] # add shot_dict['followers_count'] to the end to add followers count

def _scrape_dribbble_shot(tweet_id, dribbble_link):
    '''
    If dribbble link leads to public shot, returns the list 
    formatted row of all the shot data, otherwise, returns
    None if private or handled an unexpected exception
    '''
    url = re.search('https:\/\/dribbble\.com\/shots\/(\d+)', dribbble_link)
    if url == None:
        print(f'{dribbble_link} not a valid dribbble link')
        return None
    shot = dribbble_metadata.get_dibbble_shot(tweet_id, url.group(0))
    if shot != None and shot != -1:
        print(f'{dribbble_link} scraped successfully')
        row = [tweet_id, dribbble_link] + _form_row_as_list(shot)
        return row
    else:
        return shot

## PRIMARY RETRIEVAL FUNCTION ##
def retrieve_shots(df, filenum):
    '''
    Given a df of dribbble tweets, returns a 
    df with the correlating dribbble shot data
    '''
    cols = ['matching_tweet_id', 'dribbble_link', 'shot_id', 'created_at', 'has_likes', 'like_count',
            'has_comments', 'comment_count', 'unique_comment_count', 'comments_retrieved_count',
            'comments','shot_title', 'shot_description', 'photos_count', 'user_id', 'username'] # add 'followers_count' at the end to get followers count

    dribbble_shot_data_list = []
    
    count = 1
    hitRateLimit = False
    for index, row in df.iterrows():
        print(f'{count}:', end=' ')
        dribbble_shot= _scrape_dribbble_shot(row['tweet_id'], row['dribbble_link'])
        if dribbble_shot == -1:
            hitRateLimit = True
            print(f'hit rate limit at count {count} with url {row["dribbble_link"]}')
            break
        if dribbble_shot != None:
           dribbble_shot_data_list.append(dribbble_shot)
        count += 1
        time.sleep(1)

    dribbble_shots = pd.DataFrame(dribbble_shot_data_list, columns = cols)
    
    return dribbble_shots, hitRateLimit