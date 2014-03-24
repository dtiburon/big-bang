# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request
import json
from werkzeug.exceptions import ServiceUnavailable, BadRequest, InternalServerError
from planeteria.model.planet import Planet
from planeteria.model.feed import Feed
from planeteria import app, db

@app.route("/")
def index():
    return render_template('index')

@app.route("/thanks")
def thanks():
    return render_template('thanks')

@app.route("/tos")
def tos():
    return render_template('tos')

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
    # note: planet creation form should send user to URL http://planeteria.org/planet/<slug>/admin?new=1
    new_planet = int(request.args.get('new', "0"))  
    print "Is planet new?", new_planet

    # render template and pass in any variables to be used in template
    return render_template('planet-admin', slug=slug, new_planet=new_planet) 

@app.route("/ws/planet/<slug>", methods=["POST", "GET"])
def ws_planet(slug):
    """Loads and saves planet & feed data.
    Transitioning from simple data file to a sqlite database.
    """
    # use request object

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

        # Flask requires that this function return jquery
        return json.dumps({})


    else: #GET
        print "Loading"

        # load planet data:
        planet = Planet.query.filter_by(slug=slug).first()
        planet_name = planet.name
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

        # package data for jsonification
        jdata = {'planet_id':planet_id, 'slug':slug, 'planet_name':planet_name, 'planet_desc':planet_desc, 'feeds':feeds}
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