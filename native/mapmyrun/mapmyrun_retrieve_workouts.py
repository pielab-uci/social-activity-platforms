# behance_retrieve_projects.py
import mapmyrun_metadata
import pandas as pd
import time

def _form_row_as_list(workout_dict):
    '''
    Returns the given workout dict as a list 
    representing a row in dataframe
    '''
    return [workout_dict['workoutId'], workout_dict['pusblishDate'], 0 if workout_dict['likeCount'] == 0 else 1, workout_dict['likeCount'],
            0 if workout_dict['commentCount'] == 0 else 1, workout_dict['commentCount'], workout_dict['workoutTitle'], workout_dict['workoutDescription'],
             workout_dict['photosCount'], workout_dict['userId']]

def _scrape_mymaprun_workout(tweet_id, mymaprun_link, browser):
    '''
    If mymaprun link leads to public workout, returns the list 
    formatted row of all the project data, otherwise, returns
    None if private or handled an unexpected exception
    '''
    url = mymaprun_link 
    workout = mapmyrun_metadata.get_mymaprun_workout(tweet_id, url, browser)
    if workout != None:
        print(f'{mymaprun_link} scraped successfully')
        return [tweet_id, mymaprun_link] + _form_row_as_list(workout)
    else:
        return None

## PRIMARY RETRIEVAL FUNCTION ##
def retrieve_workouts(df, file_num):
    '''
    Given a df of behance tweets, returns a 
    df with the correlating behance project data
    '''
    cols = ['matching_tweet_id', 'mapmyrun_link', 'workout_id', 'created_at', 'has_likes', 'like_count',
            'has_comments', 'comment_count','workout_title', 'workout_description', 'photos_count', 'user_id']

    mymaprun_data_list = []

    browser = mapmyrun_metadata.get_login_browser()

    count = 1
    try:
        for index, row in df.iterrows():
            print(f'mapmyrun_tweets{file_num} on link #{count}:', end=' ')
            mapmyrun_workout = _scrape_mymaprun_workout(row['tweet_id'], row['mapmyrun_link'], browser)
            if mapmyrun_workout != None:
                mymaprun_data_list.append(mapmyrun_workout)
            time.sleep(.5)
            if count % 500 == 0 and count != 2000: # relogin and open a new broser every 500 links
                mapmyrun_metadata.close_browser(browser)
                browser = mapmyrun_metadata.get_login_browser()
            count += 1

        mapmyrun_metadata.close_browser(browser)
    except Exception as e:
        print(e)
        print(f'saving mapmyrun_tweets{file_num} up to count {count}...')
    finally:
        mymaprun_workouts = pd.DataFrame(mymaprun_data_list, columns = cols)
        
        return mymaprun_workouts
