#!/usr/bin/env python
from sqlalchemy import create_engine
import hepixvmlis.databaseDefinition as model

import logging
import optparse
import smimeX509validation.loadcanamespace as loadcanamespace
import sys
from hepixvmlis.__version__ import version

from sqlalchemy.orm import sessionmaker
import hepixvmlis
import urllib2
import urllib
import json

from hepixvmitrust.vmitrustlib import VMimageListDecoder as VMimageListDecoder

def formatter(filename):
    print filename
    pass
class db_actions():
    
    def __init__(self,session):
        self.session = session
        self.log = logging.getLogger("vmlisub_sub.db_actions")
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
        
    def subscribe_file(self,anchor,filename):
        req = urllib2.Request(url=filename)
        f = urllib2.urlopen(req)
        validated_data = anchor.validate_text(f.read())
        jsontext = json.loads(validated_data['data'])
        vmilist = VMimageListDecoder(jsontext)
        
        metadata = {}
        metadata.update(vmilist.metadata)
        metadata.update(vmilist.endorser.metadata)
        if u'dc:identifier' not in metadata.keys():
            self.log.error('list dc:identifier does not found')
            return False
        if metadata[u'hv:dn'] != validated_data['signer_dn']:
            self.log.error('Endorser DN does not match signature')
            return False
        if metadata[u'hv:ca'] != validated_data['issuer_dn']:
            self.log.error('list hv:ca does not match signature')
            return False
        if metadata[u'hv:uri'] != filename:
            self.log.warning('list hv:uri does not match subscription uri')
        
            
        self.subscription_create(metadata,authorised=True)

    def subscriptions_lister(self,formatter2 = formatter):
        output = ''

        subauthq = self.session.query(model.SubscriptionAuth).all()


        #print self.session.query(model.SubscriptionAuth).count()
        subauthq = self.session.query(model.Subscription).all()
        for item in subauthq:
            obj = {u'dc:identifier' : str(item.uuid),
                    u'dc:description' : str(item.description),
                    u'hv:uri' : str(item.url),
                    u'authorised' : str(item.authorised),
                    }
            output += json.dumps(obj, sort_keys=True, indent=4)
        return output


    def subscriptions_update(self,anchor):
        
        subscriptionlist = self.session.query(model.Subscription).all()
        for subscription in subscriptionlist:
            self.log.info("Updating:%s" % (subscription.uuid))
            req = urllib2.Request(url=subscription.url)
            f = urllib2.urlopen(req)
            update_unprocessed = f.read()
            validated_data = anchor.validate_text(update_unprocessed)
            data = validated_data['data']
            dn = validated_data['signer_dn']
            ca = validated_data['issuer_dn']
            # Now we know the data better check the SubscriptionAuth
            subauthq = self.session.query(model.SubscriptionAuth).\
                filter(model.Endorser.id==model.EndorserPrincible.id).\
                filter(model.EndorserPrincible.hv_dn==dn).\
                filter(model.EndorserPrincible.hv_ca==ca).\
                filter(model.SubscriptionAuth.endorser == model.Endorser.id).\
                filter(model.SubscriptionAuth.subscription == model.Subscription.id).\
                filter(model.Subscription.id == subscription.id)
                
            count = subauthq.count()
            if count == 0:
                self.log.error('Endorser not authorised on subscription')
                continue
            authsub = subauthq.one()
            jsontext = json.loads(data)

            vmilist = VMimageListDecoder(jsontext)
            if vmilist.endorser.metadata[u'hv:dn'] != dn:
                self.log.error('Endorser DN does not match signature')
                continue
            if vmilist.endorser.metadata[u'hv:ca'] != ca:
                self.log.error( 'list hv:ca does not match signature')
                continue
            if vmilist.metadata[u'hv:uri'] != subscription.url:
                self.log.error('list hv:uri does not match subscription uri')
                continue
            if vmilist.metadata[u'dc:identifier'] != subscription.uuid:
                self.log.error('list dc:identifier does not match subscription uuid')
                continue
            
            metadata = vmilist.metadata
            metadata[u'data'] = update_unprocessed
            imagelist = model.Imagelist(authsub.id,metadata)
            self.session.add(imagelist)
            self.session.commit()
            for imageObj in vmilist.images:
                imageDb = model.Image(imagelist.id,imageObj.metadata)
                self.session.add(imageDb)
                self.session.commit()
            

def main():
    """Runs program and handles command line options"""
    actions = set([])
    anchor = loadcanamespace.ViewTrustAnchor()
    anchor_needed = False
    dbinitiation_default = 'sqlite:///tutorial.db'
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-l', '--list', action ='store_true',help='list subscriptions', metavar='OUTPUTFILE')
    p.add_option('-d', '--database', action ='store', help='Database Initiation string',
        default='sqlite:///tutorial.db')
    p.add_option('-s', '--subscribe', action ='append',help='Subscribe', metavar='INPUTFILE')
    p.add_option('-c', '--cert-dir', action ='store',help='Subscribe', metavar='INPUTFILE',
        default='/etc/grid-security/certificates/')
    p.add_option('-u', '--update', action ='store_true',help='update subscriptions')
    options, arguments = p.parse_args()
    anchor =  loadcanamespace.ViewTrustAnchor()

    subscription_url_list = []
    if options.list:
        actions.add('list')
    if options.update:
        actions.add('update')
        anchor_needed = True

    if options.subscribe:
        anchor_needed = True
        actions.add('subscribe')
        for subscriptions_ui in options.subscribe:
            subscription_url_list.append(subscriptions_ui)
        
    if len(actions) == 0:
        return
    # 1 So we have some actions to process
    
    # 1.1 Initate DB
    engine = create_engine(options.database, echo=False)
    model.init(engine)
    SessionFactory = sessionmaker(bind=engine)
    # 2 Initate CA's to manage files
    if anchor_needed:
        anchor.update_ca_list(options.cert_dir)
    # Handle actions
    if 'subscribe' in actions:
        Session = SessionFactory()
        db = db_actions(Session)
        for uri in subscription_url_list:
            db.subscribe_file(anchor,uri)
            
    if 'list' in actions:
        Session = SessionFactory()
        db = db_actions(Session)
        print db.subscriptions_lister()
    if 'update' in actions:
        Session = SessionFactory()
        db = db_actions(Session)
        db.subscriptions_update(anchor)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
