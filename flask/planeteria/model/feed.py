from planeteria import db
from sqlalchemy import Table, Column, Integer, String, UnicodeText, UniqueConstraint, Text, Index

class Feed(db.Model): 
    """
    Information about a feed.
    """

    __tablename__ = 'feed' 
    id = Column(Integer, primary_key=True)
    url = Column(UnicodeText, nullable=False)
    name = Column(UnicodeText, nullable=False) 
    image = Column(UnicodeText, nullable=True) 
    # refer to corresponding planet
    planet = Column(Integer, nullable=False)

    # Constraint to ensure each url within a planet is unique
    UniqueConstraint('planet', 'url', name='feed_planet_url_undx')

    query = db.session.query_property()
    def __init__(self, url = u'', name = u'', image = u'', planet = 0): 
        self.id = id
        self.url = url
        self.name = name
        self.image = image
        self.planet = planet

    def __str__(self): 
    # print string for the object
        return "<Feed('%s','%s','%s')>" % (self.id, self.name, self.url)

# Index to easily find all feeds associated with a single planet
Index('feed_planet_ndx', Feed.planet)