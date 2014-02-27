import os
from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapper, relationship, backref
import json
from werkzeug.exceptions import ServiceUnavailable, BadRequest, InternalServerError

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"
DATA_DIR = "data" # temporary place to store data w/out a database for testing

# create database
SQLALCHEMY_DATABASE_FILE = 'planeteria.db'

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + SQLALCHEMY_DATABASE_FILE

# create database object
db = SQLAlchemy(app)

from model.planet import Planet
from model.feed import Feed

Planet.feed = relationship(Feed, backref=backref("planet"))


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

@app.route("/planet/<planetdir>")
def planet(planetdir):
    if not planetdir:
        # planetdir = "wfs" #for testing purposes
        raise BadRequest(description="Cannot load. Planet name missing.")
    else:
        return render_template('planet-feed', planetdir=planetdir)

@app.route("/planet/<planetdir>/admin")
def admin(planetdir):
    if not planetdir:
        # planetdir = "wfs" #for testing purposes
        raise BadRequest(description="Cannot load. Planet name missing.")

    # look for arguments in URL to indicate whether it's a new planet (in which case there are no feeds to be loaded)
    # todo: planet creation form should send user to URL http://planeteria.org/planet/<planetdir>/admin?new=1
    new_planet = int(request.args.get('new', "0"))  
    print "Is planet new?", new_planet

    # render template and pass in any variables to be used in template
    return render_template('planet-admin', planetdir=planetdir, new_planet=new_planet) 

@app.route("/ws/planet/<planetdir>", methods=["POST", "GET"])
def ws_planet(planetdir):
    """Loads and saves feed data.
    Simply saves data to a file as a temporary measure for testing. 
    Real database to be added later.
    """
    # use request object

    print "load/save" # to verify function is triggered

    if request.method == "POST":
        print "Saving"
        try:
            datafile = open(os.path.join(DATA_DIR, planetdir), 'w')
            datafile.write(request.data)
            datafile.close()
        except IOError:
            raise InternalServerError(description="Failed to save planet feed data.")

        # Although we have saved the data above, Flask requires returning JSON data
        return json.dumps({})

    else: #GET
        print "Loading"
        # test data:
        # feeds_to_save = [{'id':22, 'url':'http://dtiburon.wordpress.com/feed', 'name':'Aleta Dunne', 'image':'https://dl.dropbox.com/u/6356650/clay_aleta_200x200.jpg'}, {'id':23, 'url':'http://thelittlerobotblogs.wordpress.com/feed/', 'name':'Ana Marian Pedro', 'image':'http://i.imgur.com/xXWG7.jpg'}, {'id':24, 'url':'http://wowsig.in/log/feed/', 'name':'Aakanksha Gaur', 'image':''}]
        # jdata = {'planetdir':'wfs', 'feeds':feeds_to_save, 'highest_feed_id':24}
        # return some json-wrapped info to work with (what you loaded or test data)
        # return json.dumps(jdata)

        try:
            datafile = open(os.path.join(DATA_DIR, planetdir), 'rbU')
            jdata = datafile.read()
            datafile.close()
        except IOError:
            raise InternalServerError(description="Failed to load planet feed data.")
        return jdata

if __name__ == "__main__":
    app.run(debug=True)