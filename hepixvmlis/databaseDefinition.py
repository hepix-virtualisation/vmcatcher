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

metadata = MetaData()

Column('id', Integer, Sequence('endorser_id_seq'), primary_key=True)
Column('id', Integer, Sequence('endorserprincible_id_seq'), primary_key=True)

Column('id', Integer, Sequence('imagelist_id_seq'), primary_key=True)
Column('id', Integer, Sequence('image_id_seq'), primary_key=True)
Column('id', Integer, Sequence('subscription_seq'), primary_key=True)
Column('id', Integer, Sequence('subscription_auth_seq'), primary_key=True)





Endorser_table = Table('endorser', metadata,
        Column('id', Integer, Sequence('endorser_id_seq'), primary_key=True),
        Column('identifier', String(50)),
    )

Endorserprincible_table = Table('endorserprincible', metadata,
        Column('id', Integer, Sequence('endorserprincible_id_seq'), primary_key=True),
        Column('hv_ca', String(50),nullable = False),
        Column('hv_dn', String(50),unique=True,nullable = False),
        Column('ca_pubkey', String(50)),
        Column('endorser', Integer, ForeignKey('endorser.id', onupdate="CASCADE", ondelete="CASCADE")),
    )





Subscription_table = Table('subscription', metadata,
        Column('id', Integer, Sequence('subscription_seq'), primary_key=True),
        Column('uuid', String(50),nullable = False,unique=True),
        Column('description', String(200)),
        Column('url', String(200),nullable = False,unique=True),
        Column('authorised', Boolean,nullable = False),
        Column('imagelist_latest', Integer, ForeignKey('subscription.id')),
    )

Subscriptionauth_table = Table('subscription_auth', metadata,
        Column('id', Integer, Sequence('subscription_auth_seq'), primary_key=True),
        Column('subscription', Integer, ForeignKey('subscription.id', onupdate="CASCADE", ondelete="CASCADE")),
        Column('endorser', Integer, ForeignKey('endorser.id', onupdate="CASCADE", ondelete="CASCADE"),nullable = False),
    )



Imagelist_table = Table('imagelist', metadata,
        Column('id', Integer, Sequence('imagelist_id_seq'), primary_key=True),
        Column('identifier', String(50),unique=True),
        Column('endorsed', String(50)),
        Column('url', String(100)),
        Column('sub_auth', Integer, ForeignKey('subscription_auth.id', onupdate="CASCADE", ondelete="CASCADE")),
        Column('data', String(1000)),
        Column('data_hash', String(128)),
        Column('expired', DateTime),
    )


Image_table = Table('image', metadata,
        Column('id', Integer, Sequence('image_id_seq'), primary_key=True),
        Column('identifier', String(50)),
        
        Column('description', String(50)),
        Column('hypervisor', String(50)),
        Column('sha512', String(128)),
        Column('uri', String(128)),
        Column('os', String(50)),
        Column('osversion', String(50)),
        Column('arch', String(50)),
        Column('version', String(50)),
        Column('size', Integer),
        Column('title', String(100)),
        Column('comments', String(100)),
        Column('imagelist', Integer, ForeignKey('imagelist.id')),
    )




class Endorser(object):
    __tablename__ = 'endorser'
    def __init__(self, metadata):
        identifier = ''
        identifier_str = u'dc:identifier'
        if identifier_str in metadata.keys():
            identifier = metadata[identifier_str]
        id = Column(Integer, primary_key=True)
        
        self.identifier = identifier

class EndorserPrincible(object):
    __tablename__ = 'endorser'
    def __init__(self, endorser, metadata):
        hv_dn = None
        hv_dn_str = u'hv:dn'
        if hv_dn_str in metadata.keys():
            hv_dn = metadata[hv_dn_str]
        hv_ca = None
        hv_ca_str = u'hv:ca'
        if hv_ca_str in metadata.keys():
            hv_ca = metadata[hv_ca_str]
        id = Column(Integer, primary_key=True)
        self.endorser = endorser
        self.hv_ca = hv_ca
        self.hv_dn = hv_dn


class Subscription(object):
    __tablename__ = 'subscription'
    id = Column(Integer, primary_key=True)
    def __init__(self,details, authorised = False):
        self.uuid = details[u'dc:identifier']
        self.description = details[u'dc:description']
        self.url = details[u'hv:uri']
        self.authorised = authorised
    def __repr__(self):
        return "<Subscription('%s','%s', '%s')>" % (self.uuid, self.url, self.description)

class SubscriptionAuth(object):
    __tablename__ = 'subscription_auth'
    id = Column(Integer, primary_key=True)
    def __init__(self,subscription,endorser,authorised=False):
        self.subscription = subscription
        self.endorser = endorser
        self.authorised = authorised
        
    def __repr__(self):
        return "<SubscriptionAuth('%s','%s', '%s')>" % (self.subscription, self.authorised,self.endorser)

        

class Imagelist(object):
    __tablename__ = 'imagelist'
    def __init__(self, sub_auth, metadata):
        id = Column(Integer, primary_key=True)
        #print metadata
        self.Identifier = metadata[u'dc:identifier']
        self.endorsed = metadata[u'hv:uri']
        self.url = metadata[u'hv:uri']
        self.sub_auth = sub_auth
        self.data = metadata[u'data']
        self.data_hash = metadata[u'data-hash']
class Image(object):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
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
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    mapper(Endorser, Endorser_table)
    mapper(EndorserPrincible,Endorserprincible_table)
    mapper(Subscription,Subscription_table)
    mapper(SubscriptionAuth,Subscriptionauth_table)
 
    mapper(Imagelist, Imagelist_table)
    mapper(Image, Image_table)
   
