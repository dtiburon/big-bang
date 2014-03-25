from bigbang import db
from sqlalchemy import Table, Column, Integer, String, UnicodeText, UniqueConstraint, Text, Index, ForeignKey

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
    planet_id = Column(Integer, ForeignKey('planet.id'), nullable=False)
    # Constraint to ensure each url within a planet is unique
    __table_args__ = (UniqueConstraint('planet_id', 'url', name='feed_planet_url_undx'),)


    query = db.session.query_property()
    def __init__(self, url = u'', name = u'', image = u'', planet_id = 0): 
        self.url = url
        self.name = name
        self.image = image
        self.planet_id = planet_id

    def __str__(self): 
    # print string for the object
        return "<Feed('%s','%s','%s')>" % (self.id, self.name, self.url)

# Index to easily find all feeds associated with a single planet
Index('feed_planet_ndx', Feed.planet_id)