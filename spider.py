#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Beginning stages of the script to pull feed data from the web """
import feedparser

# fake data
feedurl = u'http://planeteria.org/wfs/atom.xml' # u'http://www.harihareswara.net/rss.xml' # u'http://dtiburon.wordpress.com/feed/' 
etag = u'48b57-4f5fbdd68a9da-gzip' # < wfs  # sumana: "1ecf0-ac4a-4f5ea22fcfc40" # dtiburon: 'b3fd93fbab5cce40eb4d6ab9772e4662'
pull = False # default is set here - certain conditions change it, otherwise it remains False
feedtitle = u''
feedlink = u''

# Everything below is for 1 feed URL. Wrap in a for-loop for fetching multiple feeds.
print "Checking feed", feedurl

# First time entry is pulled: create etag
if not etag:
    # no need to check to see if feeds have been pulled since the last time, pull all feeds.
    pull = True
    print "New feed. Never been pulled."
    # Establish parsed feed object
    feed = feedparser.parse(feedurl) #todo: put in a try block. look up errors.
    print "Feed length:", len(feed)
    try:
        etag = feed.etag # make sure to save this in the database
    except AttributeError:
        etag = u''
        print "Etag is fuss. No new etag for this feed."
    # more data for new feeds
    try:
        feedtitle = feed.feed.title
    except: 
        feedtitle = u''
    try:
        feedlink = feed.feed.link
    except:
        feedlink = u''

else:
    print "Feed has been pulled before."
    # Establish parsed feed object
    feed = feedparser.parse(feedurl, etag=etag)
    if feed.status != 304:
        print "New feed content published since last pull"
        pull = True
    else:
        print "No new feed content since last pull"
        print "Pull flag should be False:", pull

# if pull flag is True (there are new feeds to pull!)
if pull:
    for i, entry in enumerate(feed.entries):
        content = u''
        title = feed.entries[i].title
        print "Entry title:", title
        try: 
            date = feed.entries[i].published
        except (AttributeError): 
            date = feed.entries[i].updated
        print "Entry date:", date
        entrylink = feed.entries[i].link
        print "Entry link:", entrylink

        # Find the content in the parsed feed! It's in a different place for different feeds.
        try: # is this the most likely format?
            # Entry content is wrapped like so - {'content':[{'value':}]}
            content = feed.entries[i]['content'][0]['value']
        except (AttributeError, KeyError):
            if "summary_detail" in feed.entries[i]:
                content = feed.entries[i]['summary_detail']['value']
            # last ditch - post description instead of content
            elif "description" in feed.entries: 
                content = feed.entries[i].description
                print "Feed description:", content
            else:
                print "No content found anywhere. You're screwed."
        if content:
            print "Content type:", type(content)
        print

# store feed data in database (if it's a new feed)
print "feedtitle:", feedtitle
print "feedlink", feedlink
print "etag:", etag

# store entry data in database

    # compare date of last entry in DB with date in each entry in the parsed feed.
    # only if the parsed feed entry is newer should we save it.