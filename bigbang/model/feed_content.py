from bigbang import db
from sqlalchemy import Table, Column, Integer, String, UnicodeText, UniqueConstraint, Text, Index, ForeignKey

class FeedContent(db.Model): 
    """
    Content for feed entries. A row is one entry.
    """

    __tablename__ = 'feed_content'
    id = Column(Integer, primary_key=True)
    title = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)
    body = Column(UnicodeText, nullable=False)
    date = Column(UnicodeText, nullable=False) # Feedparser normalizes date format to a string in GMT...
    author = Column(UnicodeText, nullable=True)
    # refer to corresponding feed
    feed_id = Column(Integer, ForeignKey('feed.id'), nullable=False)

    # Add constraints here. 
    # Constraint to ensure each entry within a feed is unique??

    query = db.session.query_property()
    def __init__(self, url = u'', title = u'', body = u'', date = u'', author = u''):
        # list all columns once they're determined
        self.url = url
        self.title = title
        self.body = body
        self.date = date
        self.author = author

    def __repr__(self): 
    # print string for the object
        return "<FeedContent('%s' - '%s')>" % (self.url, self.date)

# Index to easily find all entry URLs associated with a single feed
Index('feed_content_url_ndx', FeedContent.url)