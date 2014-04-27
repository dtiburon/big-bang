# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect
import json
from werkzeug.exceptions import ServiceUnavailable, BadRequest, InternalServerError, NotFound
from sqlalchemy.exc import IntegrityError
from bigbang.model.planet import Planet
from bigbang.model.feed import Feed
from bigbang.model.feed_content import FeedContent
from bigbang import app, db
import time
import config # make sure you have a config.py file in the same directory that designates the site domain

@app.route("/")
def index():
    return render_template('index')

@app.route("/thanks")
def thanks():
    return render_template('thanks')

@app.route("/new")
def new():
    return render_template('newplanet')

@app.route("/directory")
def directory():
    return render_template('directory')

@app.route("/planet/new", methods=["POST"])
def newplanet():
    slug = request.form['slug']
    print slug
    planet_name = request.form['name']

    return redirect(os.path.join('planet', slug, 'admin?new=1'))

@app.route("/planet/<slug>")
def planet(slug):
    if not slug:
        raise BadRequest(description="Cannot load. Planet name missing.")
    else:
        planet = Planet.query.filter_by(slug=slug).first()
        return render_template('planet-feed', slug=slug, planet_name=planet.name)

@app.route("/planet/<slug>/admin")
def admin(slug):
    if not slug:
        raise BadRequest(description="Cannot load. Planet name missing.")

    # note: planet creation form should send user to URL http://bigbang.org/planet/<slug>/admin?new=1
    new_planet = int(request.args.get('new', "0"))  
    print "Is planet new?", new_planet
    site_url = "http://" + config.SITE_DOMAIN
    if not new_planet:
        planet = Planet.query.filter_by(slug=slug).first()
        planet_name = planet.name
    else:
        planet_name = ""
    # render template and pass in any variables to be used in jinja template
    return render_template('planet-admin', slug=slug, new_planet=new_planet, planet_name=planet_name, site_url=site_url)

@app.route("/ws/planet/<slug>", methods=["GET"])
def ws_planet_view(slug):
    """Loads planet feed & entry data for planet feed display."""

    # load planet data:
    planet = Planet.query.filter_by(slug=slug).first()
    try:
        planet_name = planet.name
    except AttributeError:
        print "No planet found with slug %s. Please check the URL and try again." % (slug)
        raise NotFound
    planet_desc = planet.desc
    planet_id = planet.id

    # pull all entries from a planet's feeds at once, and sort them by entry date, with the most recent last.
    planet_feeds = db.session.query("feed_id", "name", "feed_url", "image", "entry_id", "author", "entry_title", "entry_url", "entry_date", "body") \
                    .from_statement("SELECT feed.id AS feed_id, name, feed.url AS feed_url, image, feed_content.id AS entry_id, author, feed_content.title AS entry_title, feed_content.url AS entry_url, date AS entry_date, body from feed, feed_content where feed_id=feed.id and planet_id=:d order by date;") \
                    .params(d=planet_id).all()

    # parse entry data. each entry = 1 dictionary
    entries = []
    feeds = []
    for entry in planet_feeds:
        
        # add only entries with unique feed URL's to the list(feeds)
        newfeed = {}
        newfeed['feed_id'] = entry[0]
        newfeed['name'] = entry[1]
        newfeed['feed_url'] = entry[2]
        newfeed['image'] = entry[3]
        if not newfeed in feeds:
            feeds.append(newfeed)
            print "added feed %s to the feeds list" % entry[1]

        newentry = {}
        newentry['feed_id'] = entry[0]
        newentry['name'] = entry[1]
        newentry['feed_url'] = entry[2]
        newentry['image'] = entry[3]
        newentry['entry_id'] = entry[4]
        newentry['author'] = entry[5]
        newentry['title'] = entry[6]
        newentry['entry_url'] = entry[7]

        # change date format from epoch to human-friendly string 
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry[8]))
        newentry['date'] = date        
        newentry['content'] = entry[9]
        entries.append(newentry)



    # package data for jsonification
    jdata = {'planet_id':planet_id, 'slug':slug, 'planet_name':planet_name, 'planet_desc':planet_desc, 'entries':entries, 'feeds':feeds}
    return json.dumps(jdata)


@app.route("/ws/planet/<slug>/admin", methods=["POST", "GET"])
def ws_planet_admin(slug):
    """Loads and saves planet & feed data for admin page."""

    if request.method == "POST":
        print "Saving admin page data"

        data = request.json
        planet_id = data['planet_id']
        print "Planet ID:", planet_id
        feeds_to_save = data['feeds']
        to_delete = {}
        print 
        print "========== Start of save =========="
        print_feed_info(feeds_to_save, to_delete)

        # load/create planet data object
        if planet_id == 0: # if a new planet that doesn't exist in the DB
            planet = Planet()

        else: # if planet already exists in the DB
            planet = Planet.query.filter_by(slug=slug).first()

            # load planet's feeds from feed table
            db_feeds = Feed.query.filter_by(planet_id=planet_id).all()
            
            # create checklist with db feed URLS to determine which ones no longer exist in the DOM for later deletion
            for feed in db_feeds:
                to_delete[feed.id] = feed

        # save Planet data
        planet.slug = data['slug']
        planet.name = data['planet_name']
        planet.desc = data['planet_desc']

        # Save all of the feeds. \ø/
        for feed in feeds_to_save:
            # check to see if it's in the DB, only add if it's not there.
            if planet_id != 0:
                # ID feeds in DB, update any changed feed data, & remove it from list of feeds to delete.
                is_new = update_feeds(feed, db_feeds, to_delete) # returns False if it exists in DB
            else:
                is_new = True
            print "Is feed", feed['url'], "new?", is_new
            
            if is_new:
                print "creating a new feed object for the new feed"
                newfeed = Feed()
                newfeed.name = feed['name']
                newfeed.url = feed['url']
                newfeed.image = feed['image']
                newfeed.planet = planet
                db.session.add(newfeed)

        db.session.add(planet)

        print "Deleting %i removed feeds." % (len(to_delete))
        print "to_delete:", to_delete
        for feed in to_delete:
            
            # printouts for troubleshooting 
            feed_obj = to_delete[feed]
            print feed_obj
            feed_entries = FeedContent.query.filter_by(feed_id=feed).all()
            print len(feed_entries), "entries associated with this feed."

            db.session.delete(to_delete[feed])

        try:
            db.session.commit()
        except IntegrityError as inst:
            print str(inst)
            raise BadRequest(description="Planet data does not meet database constraints: %s" % str(inst))

        # Flask requires that this function return jquery but it's not used.
        return json.dumps({})


    else: #GET
        print "Loading"

        # load planet data:
        planet = Planet.query.filter_by(slug=slug).first()
        try:
            planet_name = planet.name
        except AttributeError:
            print "No planet found with slug %s. Please check the URL and try again." % (slug)
            raise NotFound
        planet_desc = planet.desc
        planet_id = planet.id

        # load planet feeds:
        db_feeds = Feed.query.filter_by(planet_id=planet_id).all()

        # build feed list from DB feeds for jsonification
        feeds = []
        for feed in db_feeds:
            newfeed = {}
            newfeed['id'] = feed.id
            newfeed['url'] = feed.url
            newfeed['name'] = feed.name
            newfeed['image'] = feed.image
            feeds.append(newfeed)
        print "All feeds:", feeds

        # package data for jsonification
        jdata = {'planet_id':planet_id, 'slug':slug, 'planet_name':planet_name, 'planet_desc':planet_desc, 'feeds':feeds}
        return json.dumps(jdata)


def update_feeds(feed, db_feeds, to_delete):
# Cross-references feed against a planet's feeds in the database and updates DB as needed.

    for oldfeed in db_feeds:
        print "Cross-referencing oldfeed %s | %s with new feeds." % (oldfeed.id, oldfeed.url)
        # print "Oldfeed types: %s | %s " % (type(oldfeed.id), type(oldfeed.url))
        # print "Newfeed: %s | %s" % (feed['id'], feed['url'])
        # print "Newfeed types: %s | %s " % (type(feed['id']), type(feed['url']))
        if int(feed['id']) == oldfeed.id:
            # print "Feed %s | %s is a match!" % (feed['id'], feed['url'])
            
            # Remove from the list of items to delete.
            to_delete.pop(int(feed['id']))

            # Check to see if feed data has been updated by user and if so, update DB.  
            if feed['name'] != oldfeed.name:
                oldfeed.name = feed['name']
                print "feed name updated"

            if feed['url'] != oldfeed.url:
                oldfeed.url = feed['url']
                print "feed url updated"

            if feed['image'] != oldfeed.image:
                oldfeed.image = feed['image']
                print "feed image updated"

            print "Updated", "ID", oldfeed.id, "|", feed['url']

            return False

    # if for loop hasn't found any duplicates:
    return True

def print_feed_info(feeds_to_save, to_delete):
    print "Saving data for planet", planet
    print "Total feeds to save:", len(feeds_to_save)
    for i, feed in enumerate(feeds_to_save):
        print "== Feed", i, "to save =="
        print "id: %s  | name: %s  | url: %s  | image: %s" % (feed['id'], feed['name'], feed['url'], feed['image'])
    print
    num_deletions = len(to_delete)
    print "Items to delete:", num_deletions
    for i, feed in enumerate(to_delete):
        print "== Feed", i, "to be deleted =="
        print "id: %s  | name: %s  | url: %s  | image: %s" % (feed['id'], feed['name'], feed['url'], feed['image'])
    print 
        
