import os
from flask import Flask, render_template, request
import json
from werkzeug.exceptions import ServiceUnavailable, BadRequest, InternalServerError

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"
DATA_DIR = "data"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)

# to load any of the pages below, enter Flask ip address as URL + url path indicated in app route.
# failing to do this will cause a 404 or direct you to the homepage.
@app.route("/") #url path
def index():
    return render_template('index')

@app.route("/thanks")
def thanks():
    return render_template('thanks')

@app.route("/tos")
def tos():
    return render_template('tos')

@app.route("/planet/<planetname>")
def planet(planetname):
    if not planetname:
        planetname = "wfs" #for testing purposes
        # replace with error message for launch
    else:
        return render_template('planet-feed')

@app.route("/planet/<planetname>/admin")
def admin(planetname):
    if not planetname:
        # planetname = "wfs" #for testing purposes
        raise BadRequest(description="Cannot load. Planet name missing.")
    new = int(request.args.get('new', "0"))  # URL would be something like http://127.0.0.1:5000/planet/wfs/admin?new=1
    print "Is planet new?", new
    return render_template('planet-admin', planetname=planetname, new=new)

@app.route("/ws/planet/<planetname>", methods=["POST", "GET"])
def ws_planet(planetname):
    """Loads and saves feed data.
    Simply saves data to a file as a temporary measure for testing. 
    Real database to be added later.
    """
    print "load/save"
    # use request object
    if request.method == "POST":
        try:
            # 1. open file for writing
            datafile = open(os.path.join(DATA_DIR, planetname), 'w')
            # 2. write to file
            datafile.write(request.data)
            # 3. close it
            datafile.close()
        except IOError:
            raise InternalServerError(description="Failed to save planet feed data.")

        return json.dumps({})

    else: #GET

        # test data:
        # feeds_to_save = [{'id':22, 'url':'http://dtiburon.wordpress.com/feed', 'name':'Aleta Dunne', 'image':'https://dl.dropbox.com/u/6356650/clay_aleta_200x200.jpg'}, {'id':23, 'url':'http://thelittlerobotblogs.wordpress.com/feed/', 'name':'Ana Marian Pedro', 'image':'http://i.imgur.com/xXWG7.jpg'}, {'id':24, 'url':'http://wowsig.in/log/feed/', 'name':'Aakanksha Gaur', 'image':''}]
        # jdata = {'planetname':'wfs', 'feeds':feeds_to_save, 'highest_feed_id':24}
        # return some json-wrapped info to work with (what you loaded or test data)
        # return json.dumps(jdata)

        try:
            datafile = open(os.path.join(DATA_DIR, planetname), 'rbU')
            jdata = datafile.read()
            datafile.close()
        except IOError:
            raise InternalServerError(description="Failed to load planet feed data.")
        return jdata

if __name__ == "__main__":
    app.run(debug=True)