#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Beginning stages of the script to pull feed data from the web """

from sqlalchemy.exc import IntegrityError
from bigbang.model.planet import Planet
from bigbang.model.feed import Feed
from bigbang.model.feed_content import FeedContent
from bigbang import app, db
import feedparser


# load planet feed
planet_id = 1  # placeholder for testing; later, pass in ID (not slug)

print "Loading feed data from database"
db_feeds = Feed.query.filter_by(planet_id=planet_id).all()

# Pull entry data for each feed in the planet:
for db_feed in db_feeds:
    print "loaded feed:", db_feed.name

    # set globals
    feedurl = db_feed.url # u'http://planeteria.org/wfs/atom.xml' # u'http://www.harihareswara.net/rss.xml' # u'http://dtiburon.wordpress.com/feed/' 
    etag = db_feed.etag # wfs u'48b57-4f5fbdd68a9da-gzip' # sumana: "1ecf0-ac4a-4f5ea22fcfc40" # dtiburon: 'b3fd93fbab5cce40eb4d6ab9772e4662'
    pull = False # default is set here - certain conditions change it, otherwise it remains False
    feed_name = db_feed.name
    # blog_url = u''

    # pull all URL's of feed entries from DB for comparison
    db_entries = FeedContent.query.filter_by(feed_id=db_feed.id).all()
    print "db_entries type:", type(db_entries)
    print "db_entries length:", len(db_entries)
    print 


    print "Checking feed", feedurl

    # First time entry is pulled: create etag
    if not etag:
        # no need to check to see if feeds have been pulled since the last time, pull all feeds.
        pull = True
        print "New feed. Never been pulled."
        # Establish parsed feed object
        feed = feedparser.parse(feedurl) #todo: put in a try block. look up errors.

        try:
            etag = feed.etag
        except AttributeError:
            etag = u''
            print "No new etag for this feed."

        # more data for new feeds
        try:
            feed_name = feed.feed.title
        except: 
            feed_name = u''
        try:
            blog_url = feed.feed.link
        except:
            blog_url = u''

        # store new feed data in database
        print "feed_name:", feed_name
        if not db_feed.name:
            db_feed.name = feed_name
        print "blog_url", blog_url
        if not db_feed.blogurl:
            db_feed.blogurl = blog_url
        print "etag:", etag
        if etag:
            db_feed.etag = etag

        # todo: pull feed type (RSS vs Atom) and save to database
        # todo: pull feed author and save to database

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

    print 
    # if there are new entries to pull, pull them!
    if pull:
        print "Now looping through pulled entries to save them."
        for i, entry in enumerate(feed.entries):
            entry_url = feed.entries[i].link
            print "New entry URL:", entry_url
            
            # cross-reference URL with URLs of entries saved to Database
            for entry in db_entries:
                print "Database entry URL:", entry.url
                if entry.url == entry_url:
                    print "This entry is already in the database."
                    break

            new_entry = FeedContent()
            # create association with the feed in the database
            new_entry.feed = db_feed
            new_entry.title = feed.entries[i].title
            print "Entry title:", new_entry.title
            try:
                new_entry.date = feed.entries[i].published
            except (AttributeError): 
                new_entry.date = feed.entries[i].updated
            print "Entry date:", new_entry.date
            
            # Find the content in the parsed feed! It's in a different place for different feeds. Let the games begin.
            content = u''
            try: # todo: is this the most likely format?
                # Entry content is wrapped like so - {'content':[{'value':}]}
                content = feed.entries[i]['content'][0]['value']
            except (AttributeError, KeyError):
                if "summary_detail" in feed.entries[i]:
                    content = feed.entries[i]['summary_detail']['value']
                # last ditch - post description instead of content
                elif "description" in feed.entries: 
                    content = feed.entries[i].description
                    print "Feed description will have to suffice. "
                    print "Description length:", len(content)
                else:
                    print "No content found anywhere. You're screwed."
            if content:
                new_entry.body = content
                print "Content type:", type(content)

            # Add the new entry to the database session
            db.session.add(new_entry)

            print #break after each iteration of the for-loop

# commit all changes to database
    try:
        db.session.commit()
    except IntegrityError, err:
        print str(err)

