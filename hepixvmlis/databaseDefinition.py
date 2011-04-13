from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import mapper

from sqlalchemy import ForeignKey

from sqlalchemy.orm import backref
try:
    from sqlalchemy.orm import relationship
except:
    from sqlalchemy.orm import relation as relationship


from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Endorser(Base):
    __tablename__ = 'endorser'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(50))
    princibles = relationship("EndorserPrincible", backref="Endorser",cascade='all, delete')
    def __init__(self, metadata):
        identifier = ''
        identifier_str = u'dc:identifier'
        if identifier_str in metadata.keys():
            identifier = metadata[identifier_str]
        self.identifier = identifier

class EndorserPrincible(Base):
    __tablename__ = 'endorser_princible'
    id = Column(Integer, primary_key=True)    
    hv_dn = Column(String(50),unique=True,nullable = False)
    hv_ca = Column(String(50),nullable = False)
    ca_pubkey = Column(String(50))
    endorser = Column(Integer, ForeignKey(Endorser.id, ondelete="CASCADE", onupdate="CASCADE"))
    
    def __init__(self, endorser, metadata):
        hv_dn = None
        hv_dn_str = u'hv:dn'
        if hv_dn_str in metadata.keys():
            hv_dn = metadata[hv_dn_str]
        hv_ca = None
        hv_ca_str = u'hv:ca'
        if hv_ca_str in metadata.keys():
            hv_ca = metadata[hv_ca_str]
        
        self.endorser = endorser
        self.hv_ca = hv_ca
        self.hv_dn = hv_dn


class Subscription(Base):
    __tablename__ = 'subscription'
    id = Column(Integer, primary_key=True)
    uuid = Column(String(50),nullable = False,unique=True)
    description = Column(String(200))
    url = Column(String(200),nullable = False,unique=True)
    authorised = Column( Boolean,nullable = False)
    # Line woudl be but for inconsitancy #imagelist_latest =Column(Integer, ForeignKey('imagelist.id'))
    imagelist_latest =Column(Integer)
    orm_auth = relationship("SubscriptionAuth", backref="Subscription",cascade='all, delete')
    def __init__(self,details, authorised = False):
        self.uuid = details[u'dc:identifier']
        self.description = details[u'dc:description']
        self.url = details[u'hv:uri']
        self.authorised = authorised
    def __repr__(self):
        return "<Subscription('%s','%s', '%s')>" % (self.uuid, self.url, self.description)

class SubscriptionAuth(Base):
    __tablename__ = 'subscription_auth'
    id = Column(Integer, primary_key=True)
    subscription = Column(Integer, ForeignKey(Subscription.id, onupdate="CASCADE", ondelete="CASCADE"))
    subscription2 = relationship(Subscription, backref=backref('auth', order_by=id, cascade="all,delete"))
    endorser = Column(Integer, ForeignKey(Endorser.id, onupdate="CASCADE", ondelete="CASCADE"))
    authorised = Column(Boolean,nullable = False)
    orm_imagelist = relationship("Imagelist", backref="SubscriptionAuth",cascade='all, delete')
    def __init__(self,subscription,endorser,authorised=False):
        self.subscription = subscription
        self.endorser = endorser
        self.authorised = authorised
        
    def __repr__(self):
        return "<SubscriptionAuth('%s','%s', '%s')>" % (self.subscription, self.authorised,self.endorser)

        

class Imagelist(Base):
    __tablename__ = 'imagelist'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(50),unique=True)
    endorsed = Column(String(50))
    url = Column(String(100))
    data = Column(String(1000))
    data_hash = Column(String(128))
    expired = Column(DateTime)
    sub_auth = Column(Integer, ForeignKey(SubscriptionAuth.id, onupdate="CASCADE", ondelete="CASCADE"))
    orm_image = relationship("Image", backref="Imagelist", passive_updates=False)
    
    def __init__(self, sub_auth, metadata):
        
        #print metadata
        self.Identifier = metadata[u'dc:identifier']
        self.endorsed = metadata[u'hv:uri']
        self.url = metadata[u'hv:uri']
        self.sub_auth = sub_auth
        self.data = metadata[u'data']
        self.data_hash = metadata[u'data-hash']
class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(50))
    description = Column(String(50))
    hypervisor = Column(String(50))
    sha512 = Column(String(128))
    uri = Column(String(128))
    os = Column(String(50))
    osversion = Column(String(50))
    arch = Column(String(50))
    version = Column(String(50))
    size = Column(Integer)
    title = Column(String(100))
    comments = Column(String(100))
    
    
    imagelist = Column(Integer, ForeignKey(Imagelist.id, onupdate="CASCADE", ondelete="CASCADE"))
    def __init__(self, Imagelist,metadata):
        self.identifier = metadata[u'dc:identifier']
        self.description = metadata[u'dc:description']
        self.hypervisor = metadata[u'hv:hypervisor']
        self.sha512 = metadata[u'sl:checksum:sha512']
        self.uri = metadata[u'hv:uri']
        self.os = metadata[u'sl:os']
        self.osversion = metadata[ u'sl:osversion']
        self.arch = metadata[u'sl:arch']
        self.version = metadata[ u'hv:version']
        self.size = metadata[u'hv:size']
        self.title = metadata[u'dc:title']
        self.comments = metadata[u'sl:comments']
        self.imagelist = Imagelist
    def __repr__(self):
        return "<Image('%s','%s', '%s')>" % (self.identifier, self.referanceimage, self.imagelist)


def init(engine):
    Base.metadata.create_all(engine)
