from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref



from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker

metadata = MetaData()

Column('id', Integer, Sequence('endorser_id_seq'), primary_key=True)
Column('id', Integer, Sequence('imagelist_id_seq'), primary_key=True)
Column('id', Integer, Sequence('image_id_seq'), primary_key=True)






Endorser_table = Table('endorser', metadata,
        Column('id', Integer, Sequence('endorser_id_seq'), primary_key=True),
        Column('dc_creator', String(50),nullable = False,unique=True),
        Column('hv_ca', String(50),nullable = False),
        Column('hv_dn', String(50),unique=True),
        Column('ca_pubkey', String(50))
    )
   

Imagelist_table = Table('imagelist', metadata,
        Column('id', Integer, Sequence('imagelist_id_seq'), primary_key=True),
        Column('identifier', String(50),unique=True),
        Column('endorsed', String(50)),
        Column('url', String(100)),
        Column('endorser', Integer, ForeignKey('endorser.id', onupdate="CASCADE", ondelete="CASCADE")),
    )


Image_table = Table('image', metadata,
        Column('id', Integer, Sequence('image_id_seq'), primary_key=True),
        Column('identifier', String(50)),
        Column('imagelist', Integer, ForeignKey('imagelist.id')),
    )



class Endorser(object):
    __tablename__ = 'endorser'
    def __init__(self, dc_creator,hv_ca,hv_dn):
        id = Column(Integer, primary_key=True)
        self.dc_creator = dc_creator
        self.hv_ca = hv_ca
        self.hv_dn = hv_dn

class Imagelist(object):
    __tablename__ = 'imagelist'
    def __init__(self, uid ,endorsed,url, endorser):
        id = Column(Integer, primary_key=True)
        self.Identifier = uid
        self.endorsed = endorsed
        self.url = url
        self.endorser = endorser
class Image(object):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user = relationship(Imagelist, backref=backref('imagelist', order_by=id))
    def __init__(self, identifier,referanceimage,Imagelist):
        self.identifier = identifier
        self.referanceimage = referanceimage
        self.imagelist = Imagelist
    def __repr__(self):
        return "<Image('%s','%s', '%s')>" % (self.identifier, self.referanceimage, self.imagelist)

def init(engine):
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    mapper(Endorser, Endorser_table)
    mapper(Imagelist, Imagelist_table)
    mapper(Image, Image_table)
