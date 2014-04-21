from bigbang import db
from sqlalchemy import Table, Column, Integer, String, UnicodeText, UniqueConstraint, Text, Index, ForeignKey

class Feed(db.Model): 
    """
    Information about a feed.
    """

    __tablename__ = 'feed'
    id = Column(Integer, primary_key=True)
    url = Column(UnicodeText, nullable=False)
    name = Column(UnicodeText, nullable=False) # given by user - usually blogger/author name
    image = Column(UnicodeText, nullable=True) 
    etag = Column(UnicodeText, nullable=True) # from feedparser during first pull; sometimes buggy
    title = Column(UnicodeText, nullable=True) # from feedparser during first pull
    blogurl = Column(UnicodeText, nullable=True) # from feedparser during first pull
    # track RSS vs Atom vs Netscape vs CDF - for statistical purposes / later improvements
    feedtype = Column(UnicodeText, nullable=True) # from feedparser during first pull. 
    # refer to corresponding planet
    planet_id = Column(Integer, ForeignKey('planet.id'), nullable=False)
    # Constraint to ensure each url within a planet is unique
    __table_args__ = (UniqueConstraint('planet_id', 'url', name='feed_planet_url_undx'),)


    query = db.session.query_property()
    def __init__(self, url = u'', name = u'', image = u'', etag = u'', title = u'', blogurl = u'', feedtype = u''):
        self.url = url
        self.name = name
        self.image = image
        self.etag = etag
        self.title = title
        self.blogurl = blogurl
        self.feedtype = feedtype

    def __repr__(self): 
    # print string for the object
        return "<Feed('%s','%s','%s')>" % (self.id, self.name, self.url)

# Index to easily find all feeds associated with a single planet
Index('feed_planet_ndx', Feed.planet_id)