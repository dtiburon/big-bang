import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapper, relationship, backref

STATIC_PATH = "/static"
STATIC_FOLDER = os.path.join("..","static")
TEMPLATE_FOLDER = os.path.join("..","templates")

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

from planeteria.view import admin