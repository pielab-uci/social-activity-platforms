# behance_retrieve_projects.py
import behance_metadata
import pandas as pd
import time
import re

# API_KEY = '58dd4d4995c0fe4899b5d512d5c99a0f'
# NUM_RETRIES = 2
NUM_THREADS = 1

def _form_row_as_list(project_dict):
    '''
    Returns the given project dict as a list 
    representing a row in dataframe
    '''
    return [project_dict['projectId'], project_dict['pusblishDate'], 0 if project_dict['appreciationCount'] == 0 else 1, project_dict['appreciationCount'],
            0 if project_dict['commentsCount'] == 0 else 1, project_dict['commentsCount'], len(project_dict['comments']), project_dict['num_comments_retrieved'],
            project_dict['comments'], project_dict['projectName'], project_dict['projectDescription'], project_dict['photosCount'], project_dict['username'],
            project_dict['followersCount']]

def _scrape_behance_project(tweet_id, behance_link):
    '''
    If behance link leads to public project, returns the list 
    formatted row of all the project data, otherwise, returns
    None if private or handled an unexpected exception
    '''
    # Need to make sure this method actually works when we buy the APIscraper
    #url = f'http://api.scraperapi.com?api_key={API_KEY}&url={behance_link}'
    url = behance_link # have for testing before buying API subscription
    if re.search(r'behance.net/gallery', url) == None:
        print(f'{behance_link} not valid link')
        return None
    project = behance_metadata.get_behance_project(tweet_id, url)
    if project != None:
        print(f'{behance_link} scraped successfully')
        return [tweet_id, behance_link] + _form_row_as_list(project)
    else:
        return None

## PRIMARY RETRIEVAL FUNCTION ##
def retrieve_projects(df):
    '''
    Given a df of behance tweets, returns a 
    df with the correlating behance project data
    '''
    cols = ['matching_tweet_id', 'behance_link', 'project_id', 'created_at', 'has_likes', 'like_count',
            'has_comments', 'comment_count', 'unique_comment_count', 'comments_retrieved_count',
            'comments','proejct_name', 'project_description', 'photos_count', 'username', 'followers_count']

    behance_data_list = []
    
    for index, row in df.iterrows():
        behance_project = _scrape_behance_project(row['tweet_id'], row['behance_link'])
        if behance_project != None:
           behance_data_list.append(behance_project)
        time.sleep(0.5)

    behance_projects = pd.DataFrame(behance_data_list, columns = cols)
    
    return behance_projects
