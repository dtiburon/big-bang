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
import datetime, time

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
        # slug = "wfs" #for testing purposes
        raise BadRequest(description="Cannot load. Planet name missing.")
    else:
        return render_template('planet-feed', slug=slug)

@app.route("/planet/<slug>/admin")
def admin(slug):
    if not slug:
        # slug = "wfs" #for testing purposes
        raise BadRequest(description="Cannot load. Planet name missing.")

    # look for arguments in URL to indicate whether it's a new planet (in which case there are no feeds to be loaded)
    # note: planet creation form should send user to URL http://bigbang.org/planet/<slug>/admin?new=1
    new_planet = int(request.args.get('new', "0"))  
    print "Is planet new?", new_planet

    # render template and pass in any variables to be used in template
    return render_template('planet-admin', slug=slug, new_planet=new_planet) 

@app.route("/ws/planet/<slug>", methods=["POST", "GET"])
def ws_planet(slug):
    """Loads and saves planet & feed data.
    """

    print "load/save" # to verify function is triggered

    if request.method == "POST":
        print "Saving"

        data = request.json
        planet_id = data['planet_id']
        print "Planet ID:", planet_id
        feeds_to_save = data['feeds']
        to_delete = {}

        # load data from database if appropriate
        if planet_id == 0: # if a new planet that doesn't exist in the DB
            planet = Planet()

        else: # if planet already exists in the DB

            planet = Planet.query.filter_by(slug=slug).first()
            # planet_id = planet.id
            # load planet's feeds from feed table
            db_feeds = Feed.query.filter_by(planet_id=planet_id).all()
            
            # create checklist with db feed URLS to determine which ones no longer exist in the DOM for later deletion
            for feed in db_feeds:
                to_delete[feed.url] = feed

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

            if is_new:
                newfeed = Feed()
                newfeed.name = feed['name']
                newfeed.url = feed['url']
                newfeed.image = feed['image']
                newfeed.planet = planet
                db.session.add(newfeed)

        db.session.add(planet)

        print "Deleting %i removed feeds." % (len(to_delete))
        for feed in to_delete:
            db.session.delete(to_delete[feed])

        try:
            db.session.commit()
        except IntegrityError:
            raise BadRequest(description="Planet data does not meet database constraints.")

        # Flask requires that this function return json but it's not used
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

        # Database query pulls all entries from a planet's feeds at once, and sorts them by entry date, with the most recent last.
        planet_feeds = db.session.query("feed_id", "name", "feed_url", "image", "entry_id", "author", "entry_title", "entry_url", "entry_date", "body") \
                        .from_statement("SELECT feed.id AS feed_id, name, feed.url AS feed_url, image, feed_content.id AS entry_id, author, feed_content.title AS entry_title, feed_content.url AS entry_url, date AS entry_date, body from feed, feed_content where feed_id=feed.id and planet_id=:d order by date;") \
                        .params(d=planet_id).all()

        # build entry list from DB feeds for jsonification
        entries = []
        feeds = []
        print planet_feeds[1]
        print

        unique_feeds = []

        # parse entry data - each entry = 1 dictionary
        for entry in planet_feeds:
            newentry = {}
            newentry['feed_id'] = entry[0]
            newentry['name'] = entry[1]
            newentry['feed_url'] = entry[2]
            newentry['image'] = entry[3]
            newentry['id'] = entry[4]
            newentry['author'] = entry[5]
            newentry['title'] = entry[6]
            newentry['entry_url'] = entry[7]
            # change date format from epoch to human-friendly string 
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry[8]))
            newentry['date'] = date
            
            newentry['content'] = entry[9]
            print "New entry:", newentry
            entries.append(newentry)

            # save only unique feeds for admin page display
            if not entry[2] in unique_feeds:
                print "Saving new unique feed:", entry[2]
                unique_feeds.append(entry[2])
                newfeed = {}
                newfeed['id'] = entry[0]
                newfeed['name'] = entry[1]
                newfeed['url'] = entry[2]
                newfeed['image'] = entry[3]
                feeds.append(newfeed)
        print "Final feeds list:", feeds

        # package data for jsonification
        jdata = {'planet_id':planet_id, 'slug':slug, 'planet_name':planet_name, 'planet_desc':planet_desc, 'feeds':feeds, 'entries':entries}
        return json.dumps(jdata)


def update_feeds(feed, db_feeds, to_delete):
# Cross-references feed against a planet's feeds in the database and updates DB as needed

    for oldfeed in db_feeds:
        if feed['url'] == oldfeed.url:

            # Remove from the list of items to delete.
            to_delete.pop(feed['url'])

            # Check to see if feed data has been updated by user and if so, update DB.  
            if feed['name'] != oldfeed.name:
                oldfeed.name = feed['name']

            if feed['url'] != oldfeed.url:
                oldfeed.url = feed['url']

            if feed['image'] != oldfeed.image:
                oldfeed.image = feed['image']

            print "Updated", feed['url'], "ID", oldfeed.id

            return False

    # if for loop hasn't found any duplicates:
    return True