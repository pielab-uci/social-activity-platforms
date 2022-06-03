# dribbble_metadata.py
import asyncio
from pyppeteer import launch
import re
import json
from collections import defaultdict
import pandas as pd
import time

async def get_page(browser, url):
    '''Returns a new page of the given url'''
    page = await browser.newPage()
    await page.goto(url)
    return page

async def _close_browser(browser):
    await browser.close()

def close_browser(browser):
    loop = asyncio.get_event_loop()
    login_browser = loop.run_until_complete(_close_browser(browser))

async def _get_browser():
    browser = await launch(headless = True)
    return browser

def get_browser():
    loop = asyncio.get_event_loop()
    login_browser = loop.run_until_complete(_get_browser())
    return login_browser

async def get_comment_dict(page, comment):
    '''
    Returns the comment as a dict of 
    given Dribbble Shot page and comment
    '''
    comment_dict = dict()
    comment_text = await comment.querySelector('div.shot-comment-text')
    comment_dict['raw_text'] = await page.evaluate('(comment) => comment.innerText', comment_text)
    all_urls = await comment_text.querySelectorAll('a[href]')
    comment_dict['mention_count'] = 0
    comment_dict['url_count'] = 0
    for url_elem in all_urls:
        url = await page.evaluate('(url) => url.getAttribute("class")', url_elem)
        if url == 'url mention':
            comment_dict['mention_count'] += 1
        else:
            comment_dict['url_count'] += 1
    return comment_dict

async def _get_comments(page):
    '''
    Returns the comments as a dict and the unique
     comment count of given Dribbble Shot page
    '''
    # Click on the button with the class comments-action
    await page.click('button.comments-action')
    # wait for the sidebar to open. It seem to take a bit to fully open, though.
    await page.waitForSelector('div.sidebar-open', {'timeout':0})
    # Add a 300 ms wait. 
    await page.waitFor(300)

    # select all the authors in order
    commentAuthors = await page.querySelectorAll('a.shot-comment-author')
    commentAuthorsIds = [await page.evaluate('(author) => author.getAttribute("href")', author) for author in commentAuthors]

    # select all of the comments
    comments = await page.querySelectorAll('div.shot-comment-content')
    
    # build comments dictionary
    comments_dict = defaultdict(list)
    for i in range(len(commentAuthorsIds)):
        comment_dict = await get_comment_dict(page, comments[i])
        rebounds = await comments[i].querySelectorAll('div.shot-comment-rebound')
        if rebounds != None:
            comment_dict['rebound_count'] = len(rebounds)
        else:
            comment_dict['rebound_count'] = 0
        comments_dict[commentAuthorsIds[i]].append(comment_dict)
    return dict(comments_dict), len(comments)

async def _get_photos_count(page):
    '''Returns the photos count of given Dribbble Shot page'''
    multiShot = await page.querySelector('div.multishot-goods-content')
    if multiShot == None:
        return 1 # Only as one photo so return 1
    photos = await page.querySelectorAll('li.media-gallery-thumbnail.still')
    return len(photos)
    
async def _get_shot_description(page):
    '''Returns the shot descriptions of given Dribbble Shot page'''
    description = await page.querySelector('div.shot-description-container')
    description_text = await page.evaluate('(description) => description.textContent', description)
    return description_text.strip()

async def _get_main_shot_data(page):
    '''
    Returns the data such as likesCount, commentsCount,
    shotId, shot User, title, and date posted of given
    as a dictonary based on the given Dribbble Shot page
     '''
    html_content = await page.content()
    public_info = re.search('shotData: (.+)', html_content)
    if public_info == None:
        return None
    s = public_info.group(1)[:-1]
    shot_dict = json.loads(s)
    desired_info = ['likesCount', 'commentsCount', 'shotId', 'shotUser', 'title', 'postedOn']
    shot_dict = {i : shot_dict[i] for i in desired_info}
    shot_dict['username'] = shot_dict['shotUser']['username']
    shot_dict['shotUser'] = shot_dict['shotUser']['id']
    
    return shot_dict

"""Uncomment to get followers count by clicking through pages from original dribbble shot"""
# async def _get_followers_count(page):
#     '''Returns the followers count of given Dribbble Shot page'''

#     navigationPromise = asyncio.ensure_future(page.waitForNavigation())
#     await page.click('a[class="hoverable shot-user-link"]')  # indirectly cause a navigation to user profile
#     await navigationPromise  # wait until navigation finishes

#     navigationPromise = asyncio.ensure_future(page.waitForNavigation())
#     aboutElem = await page.querySelector('li[class^="about"]') 
#     aboutLink = await aboutElem.querySelector('a[href]')
#     await aboutLink.click() # indirectly cause a navigation to user about page
#     await navigationPromise # wait until navigation finishes

#     # await page.screenshot({'path': 'userAboutPage.png', 'fullPage':True})

#     profileStatsElem = await page.querySelector('section[class*=profile-stats]')
#     followerElem = await profileStatsElem.querySelector('a[href*="followers"]')
#     CountElem = await followerElem.querySelector('span.count')
#     followersCount = await page.evaluate('(CountElem) => CountElem.innerText', CountElem)
    
#     return int(followersCount.replace(',', ''))

"""Uncomment to get followers count by going straight to about page"""
# async def _get_followers_count(browser, username):
#     '''Returns the followers count of given Dribbble Shot page'''

#     profile_about_url = f'https://dribbble.com/{username}/about'
#     page = await get_page(browser, profile_about_url)

#     # #await page.screenshot({'path': 'userAboutPage.png', 'fullPage':True})

#     profileStatsElem = await page.querySelector('section[class*=profile-stats]')
#     followerElem = await profileStatsElem.querySelector('a[href*="followers"]')
#     CountElem = await followerElem.querySelector('span.count')
#     followersCount = await page.evaluate('(CountElem) => CountElem.innerText', CountElem)
    
#     return int(followersCount.replace(',', ''))

async def _get_shot_data(dribbble_link, browser):
    '''
    If dribbble_link leads to public shot, returns a dictionary
    with all the shot data, otherwise, returns
    None if private or handled an unexpected exception
    '''
    # browser = await launch()

    page = await get_page(browser, dribbble_link)
    shot_data = await _get_main_shot_data(page)

    if shot_data == None:
        # Check to see if we hit the rate limit
        titleElem = await page.querySelector('title')
        titleText = await page.evaluate('(titleElem) => titleElem.innerText', titleElem)
        if titleText == "Dribbble - You've been rate limited":
            await page.close()
            return -1 # return -1 to signal that we hit the rate limit
        print(f'{dribbble_link} is not valid or public dribbble shot page')
        await page.close()
        return None
    shot_data['photos_count'] = await _get_photos_count(page)
    shot_data['description'] = await _get_shot_description(page)
    shot_data['comments'], shot_data['num_comments_retrieved'] = await _get_comments(page)
    """Uncomment to get followers count by clicking through pages"""
    # shot_data['followers_count'] = await _get_followers_count(page)
    """Uncomment to get followers count by by going straight to about page"""
    # shot_data['followers_count'] = await _get_followers_count(browser, shot_data['username'])

    await page.close()
    # await browser.close()
    return shot_data

def get_dribbble_shot(tweet_id, dribbble_link, browser):
    '''
    Returns the shot as a dictionary of 
    its info if public. Returns None if 
    the shot is private. Handles 
    Exceptions if there are any.
    '''
    try:
        loop = asyncio.get_event_loop()
        shot = loop.run_until_complete(_get_shot_data(dribbble_link, browser))
        return shot
    except Exception as e:
        print(f'tweet_id [{tweet_id}] with link [{dribbble_link}] caused exception: {e}')
        return None
