#import os
from flask import Flask, render_template, request
import json

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"

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
		planetname = "wfs" #for testing purposes
		# replace with error message for launch
	else:
		return render_template('planet-admin', planetname=planetname) # Q: this should be done regardless of above conditional, right?

@app.route("/ws/planet/<planetname>", methods=["POST", "GET"])
def ws_planet(planetname):
    # use request object!
    if request.method == "POST":
        print request.json['feeds']
        return json.dumps({})
    else: #GET
        pass
        # return some json-wrapped info to work with (what you loaded)


if __name__ == "__main__":
    app.run(debug=True)