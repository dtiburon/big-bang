The Big Bang is a hosted planet reader, which allows anyone to make a planet,
host it, and administer it on the host site.

### What is a planet? 

A _planet_ is a collection of posts from many different blogs, all
somewhat related to one topic (otherwise known as a blog aggregator). 
It's a great way to keep tabs on a subject, a community, a technology,
a team, a project or anything else that attracts a diverse range of
bloggers. It's a great tool for community building, especially when the
community members are in different locations. This is a widely-used 
tool in Open Source Software communities.

The main difference between a planet and a feed reader such as 
Google Reader is that it is managed by a community member (or a few), 
rather than being managed by you in your personal feed reader account. 
This means that the reader spends less time monitoring which blogs 
should be added or removed and can just read.

## Work in Progress

You'll see a lot of "todo" comments in the code and broken pieces as of this
writing (March 2014).  Please forgive the dust, it's still in progress.
We're seeking help with the web design and testing the project when it nears
completion.  If interested, please contact aleta dot dunne at gmail.

## Origin & Credits

This project was inspired by Planeteria.org, a project by James Vasile
which was adapted from the single-planet software [Venus](http://intertwingly.net/code/venus/).
The Big Bang is a modern implementation of the multi-planet concept, 
with a code base that is easy to install and implement for testing or 
deployment on your own website.

## About the Codebase

- The codebase is primarily written in Python v 2.7.1
- The project uses the Model View Controler design pattern
- It uses the [Flask](http://flask.pocoo.org/) webframework
- Data is stored in a sqlite3 database with sqlalchemy abstraction layer
- The HTML and CSS were created using [Bootstrap v2.2.2](http://getbootstrap.com/2.3.2/index.html) - a future project might be to update it to Bootstrap v3 or move to something faster such as the Living Styleguide (volunteers wanted).

### To be added soon:
- Mozilla Persona logins for planet administrators
- Testing
- A pretty design; the current bootstrap design is a placeholder

## Installation

To install and run the current (unfinished) project for development requires sqlite3 installed as well as the following dependencies.  We highly recommend that you first create a virtual environment and activate it.
Then install the following packages in a terminal window with pip:

    $ pip install SQLAlchemy
    $ pip install Flask-SQLAlchemy
    $ pip install feedparser
The Flask-SQLAlchemy package includes Flask and related packages. See the requirements.txt file for all dependencies.

Clone the repository to your local machine:

    $ git clone git://github.com/dtiburon/big-bang.git

The first time you load the site, start by creating the database by running create_db.py in the home directory: 

    $ python create_db.py

Then launch the server:

    $ python server.py

It should display something like:

    * Running on http://127.0.0.1:5000/
    * Restarting with reloader

Then open a browser window and enter the URL http://127.0.0.1:5000/ - _voila_!  Leave the terminal window open that's running server.py.
In the browser, you can then follow the instructions to create a planet, add feeds to it, and save (currently no password is required). 

Pulling feed content: in another terminal window, once you have added new feeds to a planet, run spider.py to pull the feed data (right now it needs to be done manually; that will be fixed soon):

    $ python spider.py

Then go to your planet's feed page to view the content at /planet/<<slug>>.

When you're done working on/testing/using the site, type ^C into the terminal window running server.py.