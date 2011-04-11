import databaseDefinition as model
from sqlalchemy.orm import sessionmaker
import dowloader as downloader
import smimeX509validation.loadcanamespace as loadcanamespace
import hepixvmitrust.vmitrustlib as vmitrustlib
import json
class DatabaseQuerys():
    def __init__(self,session):
        self.session = session
    def endorser_get(self,metadata):
        return self.session.query(model.Endorser).\
                filter(model.Endorser.id==model.EndorserPrincible.id).\
                filter(model.EndorserPrincible.hv_dn==metadata[u'hv:dn']).\
                filter(model.EndorserPrincible.hv_ca==metadata[u'hv:ca'])
    def endorser_create(self,metadata):
        gotquery = self.endorser_get(metadata)
        if gotquery.count() != 0:
            return gotquery
        newlist = model.Endorser(metadata)
        self.session.add(newlist)
        self.session.commit()
        new_endorser = model.EndorserPrincible(newlist.id,metadata)
        
        self.session.add(new_endorser)
        self.session.commit()
        return self.endorser_get(metadata)
    def subscription_get(self,metadata):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.url==metadata[u'hv:uri'])
        return subscriptionlist
        
    def subscription_create(self,metadata,authorised=True):
        subscription_query = self.subscription_get(metadata)
        if subscription_query.count() != 0:
            return subscription_query
        endorser_list = self.endorser_create(metadata)
        endorser = endorser_list.one()
        new_subscription = model.Subscription(metadata)
        self.session.add(new_subscription)
        self.session.commit()
        new_auth = model.SubscriptionAuth(new_subscription.id,endorser.id,authorised)
        self.session.add(new_auth)
        self.session.commit()
        return self.subscription_get(metadata)
        
        
        
    def create_endorser(self,dn):
        ed_user = model.Endorser('Ian Gable', '/C=CA/O=Grid/CN=Grid Canada Certificate Authority','/C=CA/O=Grid/OU=phys.uvic.ca/CN=Ian Gable')
        #print ed_user.dc_creator
        try:
            self.session.add(ed_user)
            self.session.commit()
        except  :
            self.session.rollback()
            print "already exists"

            ed_user = None
            for instance in self.session.query(model.Endorser).order_by(model.Endorser.id):
                ed_user = instance
            
        print "got it %s %s" % (ed_user.dc_creator, ed_user.hv_dn)
        return ed_user
        
    def Imagelist_Get(self, uuid):
        found = None
        qr = self.session.query(model.Imagelist).filter(model.Imagelist.identifier==uuid)
        for item in qr:
            found = item
            break
        return found
    def Imagelist_Create(self,uuid,endorsedmetadata,url,endorser):
        print "uuid=%s" % (uuid)
        newlist = model.Imagelist( uuid ,endorsedmetadata,url,endorser)
        try:
            self.session.add(newlist)
            self.session.commit()
        except  :
            self.session.rollback()
            print "already exists"
class Database():
    def __init__(self,engine):
        self.engine = engine
        self.SessionFactory = sessionmaker(bind=self.engine)
    def ImageListSubscribe(self,metadata):
        print "request to update imagelists %s" % (metadata)
        
        session = self.SessionFactory()
        dq = DatabaseQuerys(session)
        
        endorserlist = dq.subscription_create(metadata)

    def ImageListUpdate(self,updator):
        session = self.SessionFactory()
        dq = DatabaseQuerys(session)
        anchor = loadcanamespace.ViewTrustAnchor()
        anchor.update_ca_list('/etc/grid-security/certificates/')
        subscriptionlist = session.query(model.Subscription).all()
        for subscription in subscriptionlist:
            print subscription.id
            update = downloader.https_read(subscription.url)
            
            validated_data = anchor.validate_text(update)
            data = validated_data['data']
            dn = validated_data['signer_dn']
            ca = validated_data['issuer_dn']
            # Now we know the data better check the SubscriptionAuth
            subauthq = session.query(model.SubscriptionAuth).\
                filter(model.Endorser.id==model.EndorserPrincible.id).\
                filter(model.EndorserPrincible.hv_dn==dn).\
                filter(model.EndorserPrincible.hv_ca==ca).\
                filter(model.SubscriptionAuth.endorser == model.Endorser.id).\
                filter(model.SubscriptionAuth.subscription == model.Subscription.id).\
                filter(model.Subscription.id == subscription.id)
                
            count = subauthq.count()
            if count == 0:
                print 'Endorser not authorised on subscription'
                continue
            authsub = subauthq.one()
            jsontext = json.loads(data)

            vmilist = vmitrustlib.VMimageListDecoder(jsontext)
            if vmilist.endorser.metadata[u'hv:dn'] != dn:
                print 'Endorser DN does not match signature'
                continue
            if vmilist.endorser.metadata[u'hv:ca'] != ca:
                print 'list hv:ca does not match signature'
                continue
            if vmilist.metadata[u'hv:uri'] != subscription.url:
                print 'list hv:uri does not match subscription uri'
                continue
            if vmilist.metadata[u'dc:identifier'] != subscription.uuid:
                print 'list dc:identifier does not match subscription uuid'
                continue
            metadata = vmilist.metadata
            metadata[u'data'] = update
            imagelist = model.Imagelist(authsub.id,metadata)
            session.add(imagelist)
            session.commit()
            for imageObj in vmilist.images:
                imageDb = model.Image(imagelist.id,imageObj.metadata)
                session.add(imageDb)
                session.commit()
class Updater():
    def update(self, imagelist):
        #DatabaseQuerysViewTrustAnchor
        print "UUID=%s" % (imagelist.identifier)
        print "imagelist.url=%s" % (imagelist.url)
        print "imagelist.endorsedmetadata,%s" % (imagelist.endorsed)
        print "imagelist.endorser%s" % (imagelist.endorser)

def init(engine):
    model.init(engine)
    
