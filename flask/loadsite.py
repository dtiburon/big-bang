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

@app.route("/thanks") #url path
def thanks():
    return render_template('thanks')

@app.route("/tos") #url path
def tos():
    return render_template('tos')

@app.route("/planet/<planetname>") #url path
def planet(planetname):
	if not planetname:
		planetname = "wfs" #for testing purposes
		# return render_template('index')
		# add error message
	else:
		return render_template('planet-feed')

@app.route("/planet/<planetname>/admin") #url path
def admin(planetname):
	if not planetname:
		planetname = "wfs" #for testing purposes
		# return render_template('index')
		# add error message
	else:
		return render_template('planet-admin')

@app.route("/ws/planet/<planetname>", methods=["POST", "GET"])
def ws_planet(planetname):
    # use request object!
    if request.method == "POST":
        print request.json['feeds']
    else: #GET
        pass
    return json.dumps({})


if __name__ == "__main__":
    app.run(debug=True)