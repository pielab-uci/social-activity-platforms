# behance_metadata.py
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

async def _get_project_id(page):
    '''Returns the project id of given Behance Project page'''
    idElem = await page.querySelector('[projectid]')
    projectId = await page.evaluate('(idElem) => idElem.getAttribute("projectid")', idElem)
    
    return projectId

async def _get_project_name(page):
    '''Returns the project name of given Behance Project page'''
    projInfoName = await page.querySelector('h1[class^="ProjectInfo-projectName"]')
    projName = await page.evaluate('(projInfoName) => projInfoName.innerText', projInfoName)
    
    return projName

async def _get_project_description(page):
    '''Returns the project descritption of given Behance Project page'''
    projInfoDescripton = await page.querySelector('article[class^="ProjectInfo-projectDescription"]')
    if projInfoDescripton == None:
        return ""
    projDescription = await page.evaluate('(projInfoDescripton) => projInfoDescripton.innerText', projInfoDescripton)
    
    return projDescription

async def _get_appreciation_count(page):
    '''Returns theappreciation count of given Behance Project page'''
    projInfoAppr = await page.querySelector('div[class*="ProjectInfo-projectStat-appreciations"]')
    projApprSpan = await projInfoAppr.querySelector('span[title]')
    projApprecCount = await page.evaluate('(projApprSpan) => projApprSpan.getAttribute("title")', projApprSpan)
    projApprecCount = int(projApprecCount.replace(',', ''))
    
    return projApprecCount

async def _get_comment_count(page):
    '''Returns the comment count of given Behance Project page'''
    projInfoComment = await page.querySelector('div[class*="project-comment-count"]')
    projCommentSpan = await projInfoComment.querySelector('span[title]')
    projCommentCount = await page.evaluate('(projCommentSpan) => projCommentSpan.getAttribute("title")', projCommentSpan)
    projCommentCount = int(projCommentCount.replace(',', ''))

    return projCommentCount

async def _get_date_published(page):
    '''Returns the date publised of given Behance Project page'''
    projInfoDate = await page.querySelector('div[class*="ProjectInfo-projectPublished"]')
    projDateTime = await projInfoDate.querySelector('time[datetime]')
    projPubDate = await page.evaluate('(projDateTime) => projDateTime.getAttribute("datetime")', projDateTime)
   
    return projPubDate

def _get_username_from_link(user_link):
    '''Returns the username found in the given user_link string'''
    username = re.search('www\.behance\.net\/(.+)', user_link).group(1)
    return username

async def _get_username(page):
    '''Returns the username of given Behance Project page'''
    projUser = await page.querySelector('a[class*="UserInfo-userName"]')
    userLink = await page.evaluate('(projUser) => projUser.getAttribute("href")', projUser)
    username = _get_username_from_link(userLink)
    
    return username

async def _get_comment_dict(page, comment):
    '''Creates and returns a comment dictary using the given page and comments element''' 
    comment_dict = dict()
    commentText = await comment.querySelector('div[class$=comment-text]')
    comment_dict['raw_text'] = await page.evaluate('(commentText) => commentText.innerText', commentText)
    comment_dict['mention_count'] = len(await commentText.querySelectorAll('a[href]'))
    return comment_dict
    
async def _get_comments(page):
    '''Returns the comments as a dictionary of given Behance Project page'''
    # may possible neeed to press "See More Comments" button
    # look at div.js-see-more comments pagination
    # Keep on pressing "See more comments until no more"
    commentsList = await page.querySelector('ul[class*=comments-list]')
    comments = await commentsList.querySelectorAll('div.comment-text-container')
    
    # build comments dictionary
    comments_dict = defaultdict(list)
    for comment in comments:
        commentAuthor = await comment.querySelector('a[class*=user-name-link')
        commentAuthLink = await page.evaluate('(commentAuthor) => commentAuthor.getAttribute("href")', commentAuthor)
        commentUsername = _get_username_from_link(commentAuthLink)
        comments_dict[commentUsername].append(await _get_comment_dict(page, comment))
    return dict(comments_dict), len(comments)

async def _get_photos_count(page):
    '''Returns the photos count of given Behance Project page'''
    projCanvas = await page.querySelector('#project-canvas')
    ImgElem = await projCanvas.querySelectorAll('div[class^=ImageElement-root]')
    photoCount = len(ImgElem) if ImgElem != None else 0
    gridImg = await projCanvas.querySelectorAll('img[class^=grid__item-image]')
    photoCount += len(gridImg) if gridImg != None else 0
    return photoCount

async def _get_followers_count(page):
    '''Returns the followers count of given Behance Project page'''
    profilePic = await page.hover('img[class*=Miniprofile-Avatar]')
        
    await page.waitFor(800)
    
    miniProf = await page.querySelector('div[class*=MiniprofileContent]')
    allStats = await miniProf.querySelectorAll('div[class*=UserSummaryStats-statDivider]')
    
    followersDivider = await allStats[1].querySelector('h4[class*=UserSummaryStats-statAmount]')
    followersCount = await page.evaluate('(followerStat) => followerStat.getAttribute("title")', followersDivider) # the second divider should be followers
    
    return int(followersCount)
    
async def _get_project_data(tweet_id, behance_link):
    '''
    If behance_link leads to public project, returns a dictionary
    with all the project data, otherwise, returns
    None if private or handled an unexpected exception
    '''
    pageFound = False
    try:
        browser = await launch()
        page = await get_page(browser, behance_link)
        
        # await page.screenshot({'path': 'behance_through_api.png', 'fullPage':True})

        project_data = dict()
        project_data['projectId'] = await _get_project_id(page)
        pageFound = True
        project_data['projectName'] = await _get_project_name(page)
        project_data['projectDescription'] = await _get_project_description(page)
        project_data['appreciationCount'] = await _get_appreciation_count(page)
        project_data['commentsCount'] = await _get_comment_count(page)
        project_data['pusblishDate'] = await _get_date_published(page)
        project_data['username'] = await _get_username(page)
        project_data['comments'], project_data['num_comments_retrieved'] = await _get_comments(page)
        project_data['followersCount'] = await _get_followers_count(page)
        
        project_data['photosCount'] = await _get_photos_count(page)

        await browser.close()
        return project_data
    except Exception as e:
        if not pageFound:
            print(f'tweet_id [{tweet_id}] with link [{behance_link}] has no page found')
        else:
            print(f'tweet_id [{tweet_id}] with link [{behance_link}] caused exception: {e}')
        await browser.close()
        return None

def get_behance_project(tweet_id, behance_link):
    '''
    Returns the project as a dictionary of 
    its info if public. Returns None if 
    the project is private. Handles 
    Exceptions if there are any.
    '''
    try:
        loop = asyncio.get_event_loop()
        project = loop.run_until_complete(_get_project_data(tweet_id, behance_link))
        return project
    except Exception as e:
        print(f'tweet_id [{tweet_id}] with link [{behance_link}] caused exception: {e}')
        return None

# Testing helper functions
# async def take_screenshot(url):
#     browser = await launch()
#     page = await get_page(browser, url)
    
#     #project_data = await get_main_shot_data(page)
#     await page.screenshot({'path': 'webpage.png', 'fullPage':True})
#     await browser.close()
#     #return shot_data


# # has large engagement:
# url = 'https://www.behance.net/gallery/96104551/Self-Isolating-Cabin' 

# ### url = 'https://www.behance.net/gallery/136271183/UX-CASESTUDY-ON-A-CHURCH-MOBILE-APPLICATION'
# #url = 'https://www.behance.net/gallery/136003481/Photoshop-Cutout'
# proj = get_behance_project(1, url)
# print(proj)

