import os
from flask import Flask, render_template, request
import json
from werkzeug.exceptions import ServiceUnavailable, BadRequest, InternalServerError
from planeteria.model.planet import Planet
from planeteria import app, db

# to load any of the pages below, enter Flask ip address as URL + url path indicated in app route.
# failing to do this will cause a 404 or direct you to the homepage.
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
    # todo: planet creation form should send user to URL http://planeteria.org/planet/<slug>/admin?new=1
    new_planet = int(request.args.get('new', "0"))  
    print "Is planet new?", new_planet

    # render template and pass in any variables to be used in template
    return render_template('planet-admin', slug=slug, new_planet=new_planet) 

# for testing - replace with sqlite database
from planeteria import DATA_DIR

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

        # Assuming for now it's a new planet that doesn't exist in the DB.
        # Save planet data in Planet table
        planet = Planet()

        try:
            planet.slug = data['slug']
            planet.name = data['planet_name']
            planet.desc = data['planet_desc']

        except ValueError:
            raise BadRequest(description="Failed to map planet metadata to database table")

        db.session.add(planet)
        db.session.commit()
        return json.dumps({})


    else: #GET
        print "Loading"

        try:
            datafile = open(os.path.join(DATA_DIR, slug), 'rbU')
            jdata = datafile.read()
            datafile.close()
        except IOError:
            raise InternalServerError(description="Failed to load planet feed data.")
            
        return jdata