# mymaprun_metadata.py
import re
import asyncio
from pyppeteer import launch
import time
import numpy as np
import queue 

# Make True to switch to debug mode
DEBUG = False

MYMAPRUN_LOGIN_PAGE = 'https://www.mapmyrun.com/auth/login/'

EMAIL_AND_PASS1 = {'email': 'ENTER EMAIL HERE', 'password': 'ENTER PASSWORD HERE'}
EMAIL_AND_PASS2 = {'email': 'ENTER EMAIL HERE', 'password': 'ENTER PASSWORD HERE'}
EMAIL_AND_PASS3 = {'email': 'ENTER EMAIL HERE', 'password': 'ENTER PASSWORD HERE'}
EMAIL_AND_PASS4 = {'email': 'ENTER EMAIL HERE', 'password': 'ENTER PASSWORD HERE'}
EMAIL_AND_PASS5 = {'email': 'ENTER EMAIL HERE', 'password': 'ENTER PASSWORD HERE'}

ACCOUNT_QUEUE = queue.SimpleQueue()
ACCOUNT_QUEUE.put(EMAIL_AND_PASS1)
ACCOUNT_QUEUE.put(EMAIL_AND_PASS2)
ACCOUNT_QUEUE.put(EMAIL_AND_PASS3)
ACCOUNT_QUEUE.put(EMAIL_AND_PASS4)
ACCOUNT_QUEUE.put(EMAIL_AND_PASS5)

class LoginError(Exception):
    pass

async def get_page(browser, url):
    page = await browser.newPage()
    await page.goto(url)
    return page

async def _close_browser(browser):
    await browser.close()

def close_browser(browser):
    loop = asyncio.get_event_loop()
    login_browser = loop.run_until_complete(_close_browser(browser))

async def _login():
    email_and_pass = ACCOUNT_QUEUE.get() # grab least recently used account
    try:
        browser = await launch(headless = True)
        
        login_page = await get_page(browser, MYMAPRUN_LOGIN_PAGE)

        await login_page.screenshot({'path': 'loginInput.png', 'fullPage':True})

        
        await login_page.type('input[name="email"]', email_and_pass['email'])
        await login_page.type('input[name="password"]', email_and_pass['password'])
        ACCOUNT_QUEUE.put(email_and_pass) # add account to the back of the queue

        await login_page.waitFor(500)

        await login_page.screenshot({'path': 'loginInput.png', 'fullPage':True})

        navigationPromise = asyncio.ensure_future(login_page.waitForNavigation())
        await login_page.click('button[class*="success"]')  # cause a navigation
        
        await login_page.waitFor(500)
        await login_page.screenshot({'path': 'preNavLoginScreen.png', 'fullPage':True}) # Look here to see if you got caught in a captcha
        await navigationPromise

        await login_page.waitFor(800)
        await login_page.screenshot({'path': 'postNavLoginScreen.png', 'fullPage':True}) # You should see the workout calender for the account you logged into

        email = email_and_pass['email']
        print(f'LOGIN SUCCESSFUL with {email}')
        return browser
        
    except Exception as e:
        email = email_and_pass['email']
        raise LoginError(f'LOGIN UNSUCCESSFUL with {email}')

def get_login_browser():
    loop = asyncio.get_event_loop()
    login_browser = loop.run_until_complete(_login())
    return login_browser

async def _get_workout_id(mymaprun_link):
    workout_id = re.search('mapmyrun.com/workout/(\d+)', mymaprun_link)
    if DEBUG:
        print(f'\tworkout_id: {workout_id.group(1)}')
    return workout_id.group(1)

async def _get_workout_title(page):
    title_elem = await page.querySelector('h4[class*="jss336"]')
    descrip_jss = 338 # description and title always 2 apart
    if title_elem == None:
        title_elem = await page.querySelector('h4[class*="jss338"]')
        descrip_jss = 340
    title = await page.evaluate('(title_elem) => title_elem.innerText', title_elem)
    if DEBUG:
        print(f'\ttitle: {title}')
    return title, descrip_jss

async def _get_workout_description(page, descrip_jss):
    selector_str = f'p[class*="jss{descrip_jss}"]'
    description_elem = await page.querySelector(selector_str)
    if description_elem == None:
        if DEBUG:
            print(f'\thas no description')
        return '' # No description, return empty string
    else:
        description = await page.evaluate('(description_elem) => description_elem.innerText', description_elem)
        if DEBUG:
            print(f'\tdescription: {description}')
        return description

async def _get_date_published(page, date_jss):
    if date_jss == None: # there was no userId to base this off
        date_elem = None
        jss = 434
        while date_elem == None and jss != 444:
            jss += 1
            selector_str = f'p[class*="jss{jss}"]'
            date_elem = await page.querySelector(selector_str)
    else:
        selector_str = f'p[class*="jss{date_jss}"]'
        date_elem = await page.querySelector(selector_str)
    date = await page.evaluate('(date_elem) => date_elem.innerText', date_elem)
    if DEBUG:
        print(f'\tdate: {date}')
    return date

async def _get_userId(page):
    user_elem = None
    jss = 436
    while user_elem == None and jss != 439:
        jss += 1
        selector_str = f'a[class*="jss{jss}"]'
        user_elem = await page.querySelector(selector_str)
    datePosted_jss = jss + 1
    try:
        user_profile = await page.evaluate('(user_elem) => user_elem.getAttribute("href")', user_elem)
    except Exception as e:
        if DEBUG:
            print(f'\thas no userId')
        return np.NaN, None # handles if UserId does not exist
    user_id = re.search('/profile/(\d+)', user_profile).group(1)
    if DEBUG:
        print(f'\tuser_id: {user_id}')
    return user_id, datePosted_jss

async def _get_photos_count(page):
    photo_jss_check = await page.querySelector('img[class*="jss453"]')
    if photo_jss_check != None:
        photos_elems = await page.querySelectorAll('img[class*="jss453"]')
        return photos_elems
    photos_elems = await page.querySelectorAll('img[class*="jss455"]')
    if DEBUG:
        print(f'\tphotos_count: {len(photos_elems)}')
    return len(photos_elems)

async def _get_like_and_comment_count(page):
    jss = 457
    like_and_comment_elem = None
    while like_and_comment_elem == None and jss != 466:
        jss += 1
        selector_str = f'div[class*="jss{jss}"]'
        like_and_comment_elem = await page.querySelector(selector_str)
        if like_and_comment_elem != None:
            like_comment_str = await page.evaluate('(like_and_comment_elem) => like_and_comment_elem.innerText', like_and_comment_elem)
            match = re.search('(\d+)\n•\n(\d+)', like_comment_str)
            if match != None:
                like_count = match.group(1)
                if DEBUG:
                    print(f'\tlike count: {like_count}')
                comment_count = match.group(2)
                if DEBUG:
                    print(f'\tcomment count: {comment_count}')
                return like_count, comment_count
            like_and_comment_elem = None


async def _get_workout_data(mymaprun_link, browser):
    '''
    If mymaprun_link leads to public workout, returns a dictionary
    with all the project data, otherwise, returns
    None if private or handled an unexpected exception
    '''
    
    workout_page = await get_page(browser, mymaprun_link)

    try:
        await workout_page.waitForSelector('div[class^="MuiCardContent-root"]', {'visible': True, 'timeout': 4000}) # wait 4 seconds
    except:
        print(f'{mymaprun_link} is private or not found')
        return None

    if DEBUG:
        workout = await workout_page.querySelector('div[class^="MuiCardContent-root"]')
        html = await workout_page.evaluate('(workout) => workout.innerHTML', workout)
        print('WORKOUT HTML:')
        print(html)

    workout_data = dict()
    workout_data['workoutId'] = await _get_workout_id(mymaprun_link)
    workout_data['workoutTitle'], descrip_jss = await _get_workout_title(workout_page)
    workout_data['workoutDescription']  = await _get_workout_description(workout_page, descrip_jss)

    workout_data['likeCount'], workout_data['commentCount'] = await _get_like_and_comment_count(workout_page)

    workout_data['userId'], pubDate_jss = await _get_userId(workout_page)
    workout_data['pusblishDate'] = await _get_date_published(workout_page, pubDate_jss)

    workout_data['photosCount'] = await _get_photos_count(workout_page)

    await workout_page.close() # close each workoutpage to save memory
    return workout_data

def get_mymaprun_workout(tweet_id, mymaprun_link, browser):
    '''
    Returns the workout as a dictionary of 
    its info if public. Returns None if 
    the workout is private. Handles 
    Exceptions if there are any.
    '''
    try:
        loop = asyncio.get_event_loop()
        workout = loop.run_until_complete(_get_workout_data(mymaprun_link, browser))
        return workout
    except Exception as e:
        print(f'tweet_id [{tweet_id}] with link [{mymaprun_link}] caused exception: {e}')
        return None
