#!/usr/bin/env python
# encoding: utf-8
"""
classify.pynytimes_comments

Created by Neal Caren on 2012-04-17.
neal.caren@unc.edu

Takes a times article and returns a list of dictionaries for each item.

Note: Does not use the Times API, but you should use it:
http://developer.nytimes.com/docs/community_api
Also, if you are having trouble with accessing the web, you will get an error message.
"""

import urllib
import json
from time import sleep


def nytimes_comments(article):
    
    article=article.replace(':','%253A') #convert the : to an HTML entity
    article=article.replace('/','%252F') #convert the / to an HTML entity
    offset=0 #Start off at the very beginning
    total_comments=1 #set a fake minimum number of contents
    comment_list=[] #Set up a place to store the results
    while total_comments>offset:
        url='http://www.nytimes.com/svc/community/V3/requestHandler?callback=NYTD.commentsInstance.drawComments&method=get&cmd=GetCommentsAll&url='+article+'&offset='+str(offset)+'&sort=newest' #store the secret URL
        sleep(1) #They don't like you to vist the page too quickly so take a one second break before downloading
        file=urllib.urlopen(url).read() #Get the file and read it into a string

        file=file.replace('NYTD.commentsInstance.drawComments(','') #clean the file by removing some clutter at the front end
        file=file[:-2] #clean the file by remvoings some clutter at the back end

        results=json.loads(file,  'iso-8859-1') #load the file as json
        comment_list=comment_list+results['results']['comments']
        if offset==0: #print out the number of comments, but only the first time through the loop
            total_comments=results['results']['totalCommentsFound'] # store the total number of comments
            print 'Found '+str(total_comments)+' comments'

        offset=offset+25 #increment the counter
        
    return comment_list #return the list back


'''
A sample of what it does.
You probably want to run it over a loop of articles. 
You might also store the fields you want in a CSV file for later use or export.
'''

article_url='http://opinionator.blogs.nytimes.com/2012/04/17/whos-afraid-of-greater-luxembourg/'#  URL of the article you want to get
comments=nytimes_comments(article_url)


for comment in comments: #loop through the list
    print comment['commentBody'] #print out the comment text
    
    
for comment in comments[0]: #loop through the list
    print comment #print out all the itmes that are stored
    
    
