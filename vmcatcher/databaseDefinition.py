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
import datetime
Base = declarative_base()

""" Things to change in data base.
1) Images definitions need more status flags.
2) 
"""
class Endorser(Base):
    """This table defines the Human Name for the Endorser."""
    __tablename__ = 'endorser'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(50),unique=True,nullable = False)
    princibles = relationship("EndorserPrincible", backref="Endorser",cascade='all, delete')
    subscriptionauth = relationship("SubscriptionAuth", backref="Endorser",cascade='all, delete')
    def __init__(self, metadata):
        identifier = ''
        identifier_str = u'dc:identifier'
        if identifier_str in metadata.keys():
            identifier = metadata[identifier_str]
        self.identifier = identifier
    def __repr__(self):
        return "<Endorser(%s,%s,%s)>" % (self.identifier,self.princibles,self.subscriptionauth)

class EndorserPrincible(Base):
    """This table stores the set of identies that an endorser has"""
    __tablename__ = 'endorserPrincible'
    id = Column(Integer, primary_key=True)
    hv_dn = Column(String(50),unique=True,nullable = False)
    hv_ca = Column(String(50),nullable = False)
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
    def __repr__(self):
        return "<EndorserPrincible(%s,%s)>" % (self.hv_dn,self.hv_ca)


class Subscription(Base):
    """This table stores the set of Subscriptions the system has"""
    __tablename__ = 'subscription'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(50),nullable = False,unique=True)
    description = Column(String(200))
    uri = Column(String(200),nullable = False,unique=True)
    authorised = Column( Boolean,nullable = False)
    # Line would be but for inconsitancy #imagelist_latest =Column(Integer, ForeignKey('imagelist.id'))
    imagelist_latest =Column(Integer)
    orm_auth = relationship("SubscriptionAuth", backref="Subscription",cascade='all, delete')
    # The data of the last update to the subscription.
    #     This is different from the creation time of the image list.
    #     It is provided only for instrumentation purposes.
    updated = Column(DateTime)
    # Trust achor selector.
    # 0 = None
    # 1 = Browser based
    # 2 = Interoperable Global Trust Federation
    trustAnchor = Column(Integer,default=0,nullable = False)
    # UserName for protocols using username
    userName = Column(String(200), default=0,nullable = False)
    # passWord for protocols using password
    password = Column(String(200), default=0,nullable = False)
    def __init__(self,details, authorised = False):
        self.identifier = details[u'dc:identifier']
        self.description = details[u'dc:description']
        self.uri = details[u'hv:uri']
        self.imagelist_latest = None
        self.authorised = authorised
        self.trustAnchor = 0
        self.userName = ''
        self.password = ''
    def __repr__(self):
        return "<Subscription('%s','%s', '%s')>" % (self.identifier, self.uri, self.description)





class SubscriptionAuth(Base):
    """This table stores the set of Subscriptions  Endorser Link and is
    easier to think of as Authorisations to write to Image list"""
    __tablename__ = 'subscriptionAuth'
    id = Column(Integer, primary_key=True)
    subscription = Column(Integer, ForeignKey(Subscription.id, onupdate="CASCADE", ondelete="CASCADE"))
    orm_subscription = relationship(Subscription, backref=backref('auth', order_by=id, cascade="all,delete"))
    endorser = Column(Integer, ForeignKey(Endorser.id, onupdate="CASCADE", ondelete="CASCADE"))
    authorised = Column(Boolean,nullable = False)
    orm_imagelist = relationship("ImageListInstance", backref="SubscriptionAuth",cascade='all, delete')
    def __init__(self,subscription,endorser,authorised=False):
        self.subscription = subscription
        self.endorser = endorser
        self.authorised = authorised

    def __repr__(self):
        return "<SubscriptionAuth('%s','%s', '%s')>" % (self.subscription, self.authorised,self.endorser)



class ImageDefinition(Base):
    """This table stores the set of Subscriptions  Images
    Since all Images have to havea unique UUID this table ennforces
    this."""
    __tablename__ = 'ImageDefinition'
    # The table stores the definitions of image UUID.
    # This table stores information on the image
    id = Column(Integer, primary_key = True)
    # All identifier for image instances must never clash.
    identifier = Column(String(50),nullable = False,unique=True)
    # This stores the Latest Image Instance
    latest = Column(Integer)
    # Set of cache options
    # 1 Subscribed the Image In cache if posible.
    cache = Column(Integer,nullable = False)
    subscription = Column(Integer, ForeignKey(Subscription.id, onupdate="CASCADE", ondelete="CASCADE"))
    def __init__(self, SubscriptionKey,Metadata):
        self.subscription = SubscriptionKey
        self.identifier = str(Metadata[u'dc:identifier'])
        self.cache = int(Metadata[u'cache'])
        self.latest = 0

    def __repr__(self):
        return "<ImageDefinition('%s','%s', '%s')>" % (self.identifier, self.subscription,self.latest)

class ImageListInstance(Base):
    """This table stores the Instances of images lists subscribed to.
    Including the message, its x509 checksum, 
    """
    __tablename__ = 'imageListInstance'
    id = Column(Integer, primary_key=True)
    # Raw signed messsage
    data = Column(String(1000),nullable = False)
    # Hash of Raw signed message
    data_hash = Column(String(128),nullable = False)
    # Null until expired then with date
    expired = Column(DateTime)
    sub_auth = Column(Integer, ForeignKey(SubscriptionAuth.id, onupdate="CASCADE", ondelete="CASCADE"))
    orm_image = relationship("ImageInstance", backref="ImageListInstance", passive_updates=False)
    imported = Column(DateTime,nullable = False)
    created = Column(DateTime,nullable = False)
    expires = Column(DateTime,nullable = False)
    version = Column(String(50),nullable = False)
    def __init__(self, SubscriptionAuthKey, metadata):
        #print metadata
        self.sub_auth = SubscriptionAuthKey
        self.data = metadata[u'data']
        self.data_hash = metadata[u'data-hash']

        # All times are in UTC at all times, except display.
        self.imported = datetime.datetime.utcnow()
        self.created = metadata[u'dc:date:created']
        self.expires = metadata[u'dc:date:expires']
        self.version = metadata[u'hv:version']
        if u'expired' in metadata.keys():
            self.expired = metadata[u'expired']
    def __repr__(self):
        return "<ImageListInstance ('%s','%s')>" % (self.id, self.imported)

class ImageInstance(Base):
    """Subscribers work with images not imagelists, 
    this table makes processing images easier, and enfocing 
    image UUID uniqueness."""
    __tablename__ = 'ImageInstance'
    # Stores the parsed Images status
    # Only accepted Image instances Get commited.
    # refused are stored
    id = Column(Integer, primary_key = True)
    description = Column(String(50),nullable = False)
    hypervisor = Column(String(50),nullable = False)
    sha512 = Column(String(128),nullable = False)
    uri = Column(String(128),nullable = False)
    os = Column(String(50),nullable = False)
    osversion = Column(String(50),nullable = False)
    arch = Column(String(50),nullable = False)
    version = Column(String(50),nullable = False)
    size = Column(Integer,nullable = False)
    title = Column(String(100),nullable = False)
    comments = Column(String(100))
    fkIdentifier = Column(Integer, ForeignKey(ImageDefinition.id, onupdate="CASCADE", ondelete="CASCADE"))
    fkimagelistinstance = Column(Integer, ForeignKey(ImageListInstance.id, onupdate="CASCADE", ondelete="CASCADE"))
    def __init__(self, ImageListInstanceKey,ImageDefinitionKey,metadata):
        self.fkimagelistinstance = ImageListInstanceKey
        self.fkIdentifier = ImageDefinitionKey
        self.description = metadata[u'dc:description']
        self.hypervisor = metadata[u'hv:hypervisor']
        self.sha512 = metadata[u'sl:checksum:sha512']
        self.uri = metadata[u'hv:uri']
        self.os = str(metadata[u'sl:os'])
        self.osversion = str(metadata[ u'sl:osversion'])
        self.arch = metadata[u'sl:arch']
        self.version = metadata[ u'hv:version']
        self.size = metadata[u'hv:size']
        self.title = metadata[u'dc:title']
        self.comments = metadata[u'sl:comments']

    def __repr__(self):
        return "<ImageInstance('%s','%s', '%s')>" % (self.fkIdentifier, self.description,self.uri)


def init(engine):
    Base.metadata.create_all(engine)
