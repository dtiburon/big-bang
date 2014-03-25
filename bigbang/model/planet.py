from bigbang import db
from sqlalchemy import Table, Column, Integer, String, UnicodeText, UniqueConstraint, Text

class Planet(db.Model): 
    """
    Information about a planet. 
    """

    __tablename__ = 'planet' 
    id = Column(Integer, primary_key=True)
    slug = Column(UnicodeText, nullable=False)
    name = Column(UnicodeText, nullable=False) 
    desc = Column(UnicodeText, nullable=True) 
    user = Column(Integer, nullable=False) # for planet owner - todo

    # Constraint to ensure each slug is unique
    UniqueConstraint('slug', name='planet_slug_undx')

    query = db.session.query_property()  # creates an object for query - important
    def __init__(self, slug = u'', name = u'', desc = u'', user = 0): 
        self.name = name
        self.desc = desc
        self.slug = slug
        self.user = user

    def __repr__(self): # print string for the object
        return "<Planet('%s','%s','%s')>" % (self.id, self.slug, self.name)