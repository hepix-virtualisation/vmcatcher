import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, DatabaseError, ProgrammingError
import vmcatcher.databaseDefinition as model
import os
import re
import logging
import optparse
import  smimeX509validation 
from vmcatcher.__version__ import version
import vmcatcher
import urllib2
import urllib
import hashlib
import datetime
import uuid
from hepixvmitrust.vmitrustlib import VMimageListDecoder as VMimageListDecoder
from hepixvmitrust.vmitrustlib import time_format_definition as time_format_definition

from vmcatcher.vmcatcher_subscribe.stringsort import split_numeric_sort
from vmcatcher.launch import EventObj
from vmcatcher.vmcatcher_subscribe.msgcheck import fileView

from vmcatcher.listutils import pairsNnot
import vmcatcher.outputfacard
import retrieveFacard
import vmcatcher.queryby
try:
    import simplejson as json
except:
    import json

# command line error codes.
#  10 failed to download image list.
#  11 failed to validate image list.
#  12 metadata and certificate dont match.
#  13 Endorser not authorised on subscription.
#  14 trust anchor missing
#  15 Database integrity error.
#  16 New version number is same as old version number.
#  17 New version number is less than old version number.


#  31 imagelist dc:identifier invalid.
#  32 image dc:identifier invalid.
#  33 imagelist dc:date:created invalid.
#  34 image has missing parameters in the message.
#  35 image has missing parameters in the message.
#  36 image is not registeresd with subscription.
#  37 Message was not valid JSON.
#  38 Message JSON was not valid to build image list.







class db_actions(object):
    def __init__(self,session):
        self.session = session
        self.log = logging.getLogger("db_actions")
    def endorser_get(self,metadata):
        return self.session.query(model.Endorser).\
                filter(model.Endorser.id==model.EndorserPrincible.id).\
                filter(model.EndorserPrincible.hv_dn==metadata[u'hv:dn']).\
                filter(model.EndorserPrincible.hv_ca==metadata[u'hv:ca'])
    def endorser_create(self,metadata):
        hv_dn_str = metadata[u'hv:dn']
        gotquery = self.session.query(model.Endorser).\
            filter(model.Endorser.id==model.EndorserPrincible.id).\
            filter(model.EndorserPrincible.hv_dn==metadata[u'hv:dn'])
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
                filter(model.Subscription.uri==metadata[u'hv:uri'])
        return subscriptionlist

    def subscription_create(self,metadata,authorised):
        subscription_query = self.subscription_get(metadata)
        if subscription_query.count() > 0:
            return subscription_query
        endorser_list = self.endorser_get(metadata)
        if endorser_list.count() == 0:
            return subscription_query
        endorser = endorser_list.one()
        endorserId = int(endorser.id)
        new_subscription = model.Subscription(metadata)
        # We will make the new subscription enabled by default
        new_subscription.authorised = True
        self.session.add(new_subscription)
        self.session.commit()
        new_auth = model.SubscriptionAuth(new_subscription.id,endorser.id,authorised)
        self.session.add(new_auth)
        try:
            self.session.commit()
        except IntegrityError,E:
             self.log.error("Database integrity error '%s' while subscribing to  '%s'." % (E.args,metadata))
             self.log.debug(E.params)
             self.session.rollback()
        return self.subscription_get(metadata)

    def ImageDefinition_get(self,subscriptionKey,metadata):
        subscriptionlist = self.session.query(model.ImageDefinition).\
                filter(model.ImageDefinition.identifier == metadata[u'dc:identifier'])
        return subscriptionlist

    def ImageDefinition_create(self,subscriptionKey,metadata):
        ImageDefinitionQuery = self.ImageDefinition_get(subscriptionKey,metadata)
        if ImageDefinitionQuery.count() > 0:
            return ImageDefinitionQuery
        newlist = model.ImageDefinition(subscriptionKey,metadata)
        self.session.add(newlist)
        self.session.commit()
        ImageDefinitionQuery = self.ImageDefinition_get(subscriptionKey,metadata)
        return ImageDefinitionQuery
    def ImageDefinition_list(self,subscriptionKey):
        imagedefList = self.session.query(model.ImageDefinition).\
                filter(model.ImageDefinition.subscription==subscriptionKey)
        return imagedefList


 
class db_controler(object):
    def __init__(self,dboptions,dblog = False):
        self.log = logging.getLogger("db_controler")
        self.engine = create_engine(dboptions, echo=dblog)
        model.init(self.engine)
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.anchor = None
        self.factory_selector = None
        #self.factory_view = None
        # Set all callbacks to empty
        self.callbackEventImageNew = None
        self.selectors_available = ['sub_uuid', 'sub_uri']
        self.selector_curent = None
        self._outputter = vmcatcher.outputfacard.outputFacade()
        
        
    def set_selector(self,selector_string):
        self.selector_curent = None
        if not selector_string in self.selectors_available:
            self.log.warning("Invalid selector string set:%s" % (selector_string))
            return False
        if selector_string == 'sub_uuid':
            self.selector_curent = vmcatcher.queryby.query_subscriptions_by_identifier
        elif selector_string == 'sub_uri':
            self.selector_curent = vmcatcher.queryby.query_subscriptions_by_uri
        return True
        
    def setup_trust_anchor(self,directory):
        self.anchor = smimeX509validation.LoadDirChainOfTrust(directory)


    def setup_view_format(self,format):
        self._outputter.format = format
    def unsigned_message_by_identifier_tofilepath(self,instructions):


        Session = self.SessionFactory()
        db = db_actions(Session)
        for instruction in instructions:
            print instruction

        for selection_uuid in subscriptions_selected:
            db.sdsdsd(selection_uuid)
        Session.commit()
    def sessions_list(self):
        Session = self.SessionFactory()
        
        self._outputter.fpOutput = sys.stdout
        self._outputter.saSession = Session
        self._outputter.x509anchor = self.anchor
        
        self._outputter.list_vmcatcher_subscribe()
        #view = self.factory_view(sys.stdout,Session,self.anchor)
        #view.subscriptions_lister()
        return True
    
    def subscriptions_delete(self,subscriptions_selected):
        foundOne = False
        Session = self.SessionFactory()
        db = db_actions(Session)
        for selection_item in subscriptions_selected:
            query_subscription = self.selector_curent(Session, selection_item)
            for a_sub in query_subscription:
                # should not need thsi code but do maybe a bug in slqalchamy or more likely my db definition"
                query_image_def_linked = db.ImageDefinition_list(a_sub.id)
                for image_def_linked in query_image_def_linked:
                    Session.delete(image_def_linked)
                Session.delete(a_sub)
                foundOne = True
        Session.commit()
        return foundOne
    def subscriptions_subscribe(self,urls_selected,autoEndorse):
        rc = True
        Session = self.SessionFactory()
        db = db_actions(Session)
        for uri in urls_selected:
            if not self.subscribe_file(Session,self.anchor,uri,autoEndorse):
                rc = False
        return rc


    def subscriptions_info(self,subscriptions_selected,outputfiles):
        pairs, extra_selectors ,extra_paths = pairsNnot(subscriptions_selected,outputfiles)
        for item in extra_selectors:
            pairs.append([item,None])
        errorhappened = False
        Session = self.SessionFactory()
        for pair in pairs:
            selector_filter = pair[0]
            output_file_name = pair[1]
            output_fileptr = sys.stdout
            if output_file_name != None:
                output_fileptr = open(output_file_name,'w+')
                output_fileptr.flush()
            query_subscription = self.selector_curent(Session,selector_filter)
            if query_subscription.count() == 0:
                self.log.warning("Selections '%s' does not match any known subscriptions." % (selector_filter))
                continue
            firstSubscription = query_subscription.first()
            self._outputter.fpOutput = output_fileptr
            self._outputter.saSession = Session
            self._outputter.x509anchor = self.anchor
            for item in query_subscription:
                self._outputter.display_subscription(item)
            if output_file_name != None:
                output_fileptr.close()
            
    def setEventObj(self,obj):
        self.eventObj = obj

    def subscribe_file(self,Session,anchor,filename,autoEndorse):
        req = urllib2.Request(url=filename)
        f = urllib2.urlopen(req)
        smimeProcessor = smimeX509validation.smimeX509validation(anchor)
        try:
            smimeProcessor.Process(f.read())
        except smimeX509validation.truststore.TrustStoreError,E:
            self.log.error("Validate text '%s' produced error '%s'" % (filename,E))
            return False
        except smimeX509validation.smimeX509ValidationError,E:
            self.log.error("Validate text '%s' produced error '%s'" % (filename,E))
            return False
        if not smimeProcessor.verified:
            self.log.error("Failed to  verify text '%s'" % (filename))
            return False
        jsontext = json.loads(smimeProcessor.InputDaraStringIO.getvalue())
        if jsontext == None:
            self.log.error("Message downlaoded from '%s' was not valid JSON." % (filename))
            return False
        vmilist = VMimageListDecoder(jsontext)
        if vmilist == None:
            self.log.error("Failed to decode the json as an image list Object for '%s'." % (filename))
            return False
        metadata = {}
        metadata.update(vmilist.metadata)
        metadata.update(vmilist.endorser.metadata)
        if u'dc:identifier' not in metadata.keys():
            self.log.error('list dc:identifier does not found')
            return False
        if metadata[u'hv:dn'] != smimeProcessor.InputCertMetaDataList[0]['subject']:
            self.log.error('Endorser DN does not match signature')
            return False
        if metadata[u'hv:ca'] != smimeProcessor.InputCertMetaDataList[0]['issuer']:
            self.log.error('list hv:ca does not match signature')
            return False
        if metadata[u'hv:uri'] != filename:
            self.log.warning('list hv:uri does not match subscription uri')
        db = db_actions(Session)
        endorser_list = db.endorser_get(metadata)
        if endorser_list.count() == 0:
            if not autoEndorse:
                self.log.error("Endorser '%s':'%s' was not found in database." % (metadata[u'hv:dn'],metadata[u'hv:ca']))
                self.log.info("Use '--auto-endorse' to add endorser '%s':'%s' to subscription database." % (metadata[u'hv:dn'],metadata[u'hv:ca']))
                return False
            else:
                # We can create an endorser.
                newmetadata = dict(metadata)
                newmetadata[u'dc:identifier'] = unicode(uuid.uuid4())
                endorser_list = db.endorser_create(newmetadata)
                self.log.warning("Endorser '%s':'%s' added to database." % (metadata[u'hv:dn'],metadata[u'hv:ca']))
                
                if endorser_list.count() == 0:
                    self.log.error('Failed to create an authorised endorser in Database.')
                    return False
        subscription_query = db.subscription_create(metadata,True)
        if subscription_query.count() != 1:
            self.log.error('Creation of Subscription referance failed.')
            return False
        subscription = subscription_query.one()
        subscriptionKey = int(subscription.id)
        failedToCreateImages = []
        for imageReferance in vmilist.images:
            # Now we creat image definitions
            metadata = {}
            metadata.update(imageReferance.metadata)
            metadata['cache'] = 0
            ImageDefinition_query = db.ImageDefinition_create(subscriptionKey,metadata)
            if ImageDefinition_query.count() != 1:
                self.log.error('Creation of ImageDefinition referance failed.')
                failedToCreateImages.append(imageReferance)
                continue
        if len(failedToCreateImages) > 0:
            return False
        return True
    
    
    def subscript_update_image(self,Session,subscription,imagelistref,imageObj):
        subscriptionKey = subscription.id
        ProcessingSubscriptionUuid = subscription.identifier
        if not u'dc:identifier' in imageObj.metadata.keys():
            self.log.error('Image had no ID so ignored')
            # Error code - imagelist dc:identifier invalid.
            return 31
        db = db_actions(Session)
        imageDefQuery = db.ImageDefinition_get(subscriptionKey,imageObj.metadata)
        if imageDefQuery.count() != 1:
            if self.callbackEventImageNew != None:
                self.callbackEventImageNew(imageObj.metadata)
            # Triggor an event for new image.
            self.log.info("ImageId '%s' refused by subscription '%s'" %
                (imageObj.metadata[u'dc:identifier'],ProcessingSubscriptionUuid))
            # Error code - image dc:identifier invalid.
            return 32
        ThisImageDef = imageDefQuery.one()

        ThisImageDefId = int(ThisImageDef.id)
        #print ("ThisImageDefId=%s" % (ThisImageDefId))
        try:
            imageinstance = model.ImageInstance(imagelistref,ThisImageDefId,imageObj.metadata)
        except KeyError, E:
            self.log.error("missing parameters '%s'" % E.message)
            Session.rollback()
            return 34
        Session.add(imageinstance)
        try:
            Session.commit()
        except IntegrityError,E:
            self.log.error("Database integrity error '%s' processing '%s'." % (E.args,ProcessingSubscriptionUuid))
            self.log.debug(E.params)
            Session.rollback()
            return 0
        # So now we have done the updating of the database and just need to update 
        # the latest image instance record in the database.
        
        latestimageInstanceQuery = Session.query(model.ImageInstance).\
            filter(model.ImageInstance.fkimagelistinstance == imagelistref).\
            filter(model.ImageInstance.fkIdentifier == ThisImageDefId)
        if latestimageInstanceQuery.count() != 1:
            return 0
        imageInstancelatest = latestimageInstanceQuery.one()
        imageDefQuery = db.ImageDefinition_get(subscriptionKey,imageObj.metadata)
        if imageDefQuery.count() != 1:
            self.log.error("ImageId '%s' not accepted for subscription '%s'" %
                (imageObj.metadata[u'dc:identifier'],ProcessingSubscriptionUuid))
            return 36
        ThisImageDef = imageDefQuery.one()
        ThisImageDef.latest = imageInstancelatest.id
        Session.add(ThisImageDef)
        Session.commit()
        return 0
    

    def subscription_update(self,Session,subscription):
        subscriptionKey = int(subscription.id)
        ProcessingSubscriptionUuid = str(subscription.identifier)
        self.log.info("Updating:%s" % (ProcessingSubscriptionUuid))
        
        retriever = retrieveFacard.retrieveFacard()
        retriever.uri = subscription.uri
        retriever.trustanchor = self.anchor
        resultDict = retriever.requestAsString()
        if resultDict == None:
            return 99
        rc = resultDict['code']
        if rc != 0:
            if 'error' in resultDict:
                self.log.error("%s, while retrieving %s" % (resultDict['error'],subscription.id))
            else:
                self.log.error("Download of uri '%s' failed." % (subscription.id))
            if rc > 255:
                return rc
            else:
                return 10
        update_unprocessed = resultDict['responce']
        #update_unprocessed = str(f.read())
        # Now we have the update lets first check its hash
        messagehash = hashlib.sha512(update_unprocessed).hexdigest()
        now = datetime.datetime.utcnow()
        metadataFV = {
            u'hv:uri' : str(subscription.uri),
            u'dc:identifier' : str(subscription.identifier),
        }
        #self.log.error("errr:%s" % (ProcessingSubscriptionUuid))
        checker = fileView(self.anchor,update_unprocessed,metadataFV)
        if checker.errorNo != 0:
            self.log.error("Failed to verify subscription '%s' with URI '%s'" % (subscription.identifier,subscription.uri))
            return checker.errorNo
        if checker.Json == None:
            return 14
        metadata = checker.vmilist.metadata
        metadata[u'data'] = update_unprocessed
        metadata[u'data-hash'] = messagehash
        if checker.errorNo != 0:
            self.log.info('Message Expired:%s' % (ProcessingSubscriptionUuid))
            metadata[u'expired'] = now
            Session.commit()
        # Now we know the data better check the SubscriptionAuth
        subq = Session.query(model.Subscription, model.SubscriptionAuth).\
            filter(model.Endorser.id == model.EndorserPrincible.id).\
            filter(model.EndorserPrincible.hv_dn == checker.subject).\
            filter(model.EndorserPrincible.hv_ca == checker.issuer).\
            filter(model.SubscriptionAuth.endorser == model.Endorser.id).\
            filter(model.SubscriptionAuth.subscription == model.Subscription.id).\
            filter(model.Subscription.id == subscription.id)

        count = subq.count()
        if count == 0:
            self.log.error('Endorser not authorised on subscription %s' % (ProcessingSubscriptionUuid))
            # Error code - Endorser not authorised on subscription.
            return 13
        if count != 1:
            self.log.error('Database Error processing subq:%s' % (ProcessingSubscriptionUuid))
            assert (False)
        subscription, auth = subq.one()
        
        
        # Sets 
        VersionCompare = 0
        qeryJunction = Session.query(model.ImageListInstance).\
            filter(model.Subscription.imagelist_latest == model.ImageListInstance.id).\
            filter(model.Subscription.id == subscription.id)
        
        
        
        if qeryJunction.count() == 0:
            #"we have no older version"
            self.log.info("First version of:%s" % (ProcessingSubscriptionUuid))
        else:
            if qeryJunction.count() != 1:
                self.log.error('Database Error processing  qeryJunction:%s' % (ProcessingSubscriptionUuid))
                assert (False)
            imageList = qeryJunction.one()
            if imageList.data_hash == messagehash:
                self.log.debug('Same version:%s' % (ProcessingSubscriptionUuid))
                if now > imageList.expires:
                    self.log.info("Image list '%s' has expired on: '%s'" % (ProcessingSubscriptionUuid,imageList.expires))
                    if imageList.expired == None:
                        imageList.expired = now
                        Session.commit()
                # We now know imageList is not too old.
                if ((imageList.expired != None) and (checker.errorNo == 0)):
                    # we have expired previously but now it looks good.
                    self.log.info('imageList Validated:%s' % (ProcessingSubscriptionUuid))
                    imageList.expired = None
                    Session.commit()
                if ((imageList.expired == None) and (checker.errorNo != 0)):
                    # should expire.
                    self.log.info('imageList Expired:%s' % (ProcessingSubscriptionUuid))
                    imageList.expired = now
                    Session.commit()
                return 0    
            messageVersion = checker.Json[u'hv:imagelist'][u'hv:version']
            self.log.debug('Downloaded version:%s' % (messageVersion))
            VersionCompare = split_numeric_sort(imageList.version,messageVersion)
            if VersionCompare == 0:
                self.log.warning('Downloaded version "%s" version "%s" has the same version number than the old version "%s".' % (ProcessingSubscriptionUuid,messageVersion, imageList.version))                
                #return 16 #  16 New version number is same as old version number.
            if VersionCompare < 0:
                self.log.error('Downloaded version "%s" version "%s" has lower version number than the old version "%s".' % (ProcessingSubscriptionUuid,messageVersion, imageList.version))
                return 17 #  17 New version number is less than old version number.
        
        
        imagelist = model.ImageListInstance(auth.id,metadata)
        Session.add(imagelist)
        try:
            Session.commit()
        except IntegrityError,E:
            self.log.error("Database integrity error '%s' processing '%s'." % (E.args,ProcessingSubscriptionUuid))
            self.log.debug(E.params)
            Session.rollback()
            # Error code - Database integrity error.
            return 15
        imagelistref = int(imagelist.id)
        # Now make a global return number
        globalRc = 0
        for imageObj in checker.vmilist.images:
            # Now update each Image
            thisRc = self.subscript_update_image(Session,subscription,imagelistref,imageObj)
            if thisRc != 0:
                globalRc = thisRc

        if subscription.imagelist_latest != None:
            oldimagelist_q = Session.query(model.ImageListInstance).\
                filter(model.ImageListInstance.id == subscription.imagelist_latest)
            for imagelist in oldimagelist_q:
                imagelist.authorised = False
                Session.add(imagelist)
        subscription.updated = datetime.datetime.utcnow()

        subscription.imagelist_latest = imagelistref
        Session.add(subscription)
        Session.commit()
        return globalRc
        
    def subscriptions_update(self):
        if self.anchor == None:
            self.log.warning("No enabled certificates, check your x509 dir.")
            return 12
        Session = self.SessionFactory()
        db = db_actions(Session)
        rc = 0
        subscriptionlist = Session.query(model.Subscription).all()
        for subscription in subscriptionlist:
            thisRc = self.subscription_update(Session,subscription)
            if thisRc != 0:
                rc = thisRc
        return rc
    def subscriptions_image_list(self,subscriptions_selected,outputfiles):
        pairs, extra_selectors ,extra_paths = pairsNnot(subscriptions_selected,outputfiles)

        for item in extra_selectors:
            pairs.append([item,None])

        errorhappened = False
        Session = self.SessionFactory()
        for pair in pairs:
            selector_filter = pair[0]
            output_file_name = pair[1]
            output_fileptr = sys.stdout
            if output_file_name != None:
                output_fileptr = open(output_file_name,'w+')
                output_fileptr.flush()
            query_subscription = self.selector_curent(Session,selector_filter)
            if query_subscription.count() == 0:
                self.log.warning("Selections '%s' does not match any known subscriptions." % (selector_filter))
                continue
            self._outputter.fpOutput = output_fileptr
            self._outputter.saSession = Session
            self._outputter.x509anchor = self.anchor
            
            for item in query_subscription:
                self._outputter.display_subscription(item)
                query_image_def = Session.query(model.ImageDefinition).\
                    filter(model.ImageDefinition.subscription==item.id)
                for imagedef in query_image_def:
                    self._outputter.display_image_def(imagedef)
            if output_file_name != None:
                output_fileptr.close()
    def subscriptions_image_accept(self,subscriptions,images):
        pairs, extra_subscriptions ,extra_images = pairsNnot(subscriptions,images)
        if len(extra_subscriptions) > 0:
            self.log.error('Not enough images selected')
            return False
        if len(extra_images) > 0:
            self.log.error('Not enough subscriptions selected')
            return False
        Session = self.SessionFactory()
        errors = 0
        for sub_uuid, image_uuid in pairs:
            
            image_known = Session.query(model.ImageDefinition.identifier,model.Subscription.identifier).\
                filter(model.ImageDefinition.identifier == image_uuid).\
                filter(model.ImageDefinition.subscription == model.Subscription.id)
            if image_known.count() > 0:
                iident, sident = image_known.one()
                self.log.error("Subscription '%s' has image '%s' already." % (sident,iident))
                errors = errors + 1
                continue
            sub_known = Session.query(model.Subscription).\
                filter(model.Subscription.identifier == sub_uuid)
            if sub_known.count() == 0:
                self.log.error("Subscription '%s' is unknown." % (sub_uuid))
                errors = errors + 1
                return False
            subscription = sub_known.one()
            subscription.imagelist_latest = None
            key = subscription.id
            
            metadata = { 'dc:identifier' : image_uuid,
                'cache' : 0}
            newlist = model.ImageDefinition(key,metadata)
            Session.add(newlist)
            Session.add(subscription)
            Session.commit()
            #self.log.info("Subscription '%s' include image '%s'." % (sub_uuid,image_uuid))
        if errors != 0:
            return False
        return True


    def subscriptions_image_refuse(self,subscriptions,images):
        pairs, extra_subscriptions ,extra_images = pairsNnot(subscriptions,images)
        if len(extra_subscriptions) > 0:
            self.log.error('Not enough images selected')
            return False
        if len(extra_images) > 0:
            self.log.error('Not enough subscriptions selected')
            return False
        Session = self.SessionFactory()
        errors = 0
        for sub_uuid, image_uuid in pairs:
            image_known = Session.query(model.Subscription,model.ImageDefinition).\
                filter(model.ImageDefinition.identifier == image_uuid).\
                filter(model.ImageDefinition.subscription == model.Subscription.id).\
                filter(model.Subscription.identifier == sub_uuid)
            if image_known.count() == 0:
                self.log.error("Subscription '%s' already refuses image '%s'." % (sub_uuid,image_uuid))
                errors = errors + 1
                continue
            subscription ,imageDef = image_known.one()
            imageInstance_known = Session.query(model.ImageInstance).\
                filter(model.ImageInstance.fkIdentifier == imageDef.id)
            for instance in imageInstance_known:
                Session.delete(instance)
            subscription.imagelist_latest = None
            Session.delete(imageDef)
            Session.add(subscription)
            Session.commit()
        if errors != 0:
            return False
        return True
    
