from smimeX509validation import TrustStore, LoadDirChainOfTrust,smimeX509validation, smimeX509ValidationError
from hepixvmitrust.vmitrustlib import time_format_definition as time_format_definition

import logging
import vmcatcher.databaseDefinition as model
import json

class output_driver_base(object):

    def __init__(self):
        self.fpOutput = None
        self.saSession = None
        self.x509anchor = None
    
    def query_imagedef_Identifier(self,imagelistIdentifier):
        imageDefs = self.saSession.query(model.ImageDefinition,model.Subscription).\
            filter(model.Subscription.id == model.ImageDefinition.subscription).\
            filter(model.ImageDefinition.identifier==imagelistIdentifier)
        return imageDefs
    
    def bitmap_vmcatcher_image(self,imagedef,subscription):
        subauthq = self.saSession.query(model.ImageInstance,model.ImageListInstance).\
                filter(model.ImageDefinition.id == imagedef.id).\
                filter(model.Subscription.id == subscription.id).\
                filter(model.ImageDefinition.subscription == model.Subscription.id).\
                filter(model.ImageInstance.fkIdentifier == model.ImageDefinition.id).\
                filter(model.ImageInstance.fkimagelistinstance == model.ImageListInstance.id).\
                filter(model.Subscription.imagelist_latest == model.ImageListInstance.id)
        bimappedOutput = imagedef.cache
        if subauthq.count() == 1:
            q_result = subauthq.one()
            imageInstance = q_result[0]
            listInstance = q_result[1]
            available = 0
            if ((imagedef.latest == imageInstance.id) and (subscription.authorised == 1) and
                (subscription.imagelist_latest == listInstance.id) and (listInstance.expired == None) and
                (imageInstance.fkimagelistinstance != None) and (imagedef.latest !=None)):
                available = 1
            bimappedOutput = imagedef.cache + (available << 1)
        return bimappedOutput

class output_driver_lister(output_driver_base):
    def list_vmcatcher_subscribe(self):
        subauthq = self.saSession.query(model.Subscription).all()
        for item in subauthq:
            self.fpOutput.write ("%s\t%s\t%s\n" % (item.identifier,item.authorised,item.uri))
    def list_vmcatcher_image(self):
        imageDefs = self.saSession.query(model.ImageDefinition,model.Subscription).\
            filter(model.Subscription.id == model.ImageDefinition.subscription)
        for q_result in imageDefs:
            imagedef = q_result[0]
            subscription = q_result[1]
            bimappedOutput = self.bitmap_vmcatcher_image(imagedef,subscription)
            self.fpOutput.write("%s\t%s\t%s\n" % (imagedef.identifier,bimappedOutput,subscription.identifier))
    def list_vmcatcher_endorser_cred(self):
        allendorsers = self.saSession.query(model.Endorser).all()
        for endorser in allendorsers:
            EndId = str(endorser.identifier)
            subauthq = self.saSession.query(model.Endorser,model.EndorserPrincible).\
                filter(model.Endorser.id==model.EndorserPrincible.endorser).\
                filter(model.Endorser.identifier==EndId)
            for item in subauthq:
                endorser = item[0]
                princible = item[1]
                self.fpOutput.write ("'%s'\t'%s'\t'%s'\n" % (endorser.identifier,princible.hv_dn,princible.hv_ca))
    def list_vmcatcher_endorser_link(self):
        allLinks = self.saSession.query(model.Subscription,model.Endorser,model.SubscriptionAuth).\
            filter(model.Endorser.id==model.SubscriptionAuth.endorser).\
            filter(model.Subscription.id==model.SubscriptionAuth.subscription)
        for sub,endorser,aubauth in allLinks:
            self.fpOutput.write ("'%s'\t'%s'\t'%s'\n" % (endorser.identifier,sub.identifier,aubauth.authorised))
    def display_imagelistImage(self,subscription,imagedef,imagelist,image):
        self.fpOutput.write ('imagelist.dc:identifier=%s\n' % (subscription.identifier))
        self.fpOutput.write ('imagelist.dc:date:imported=%s\n' % (imagelist.imported.strftime(time_format_definition)))
        self.fpOutput.write ('imagelist.dc:date:created=%s\n' % (imagelist.created.strftime(time_format_definition)))
        self.fpOutput.write ('imagelist.dc:date:expires=%s\n' % (imagelist.expires.strftime(time_format_definition)))
        self.fpOutput.write ('imagedef.dc:identifier=%s\n' % (imagedef.identifier))
        self.fpOutput.write ('imagedef.cache=%s\n' % (imagedef.cache))
        self.fpOutput.write ('image.dc:description=%s\n' % (image.description))
        self.fpOutput.write ('image.dc:title=%s\n' % (image.title))
        self.fpOutput.write ('image.hv:hypervisor=%s\n' % (image.hypervisor))
        self.fpOutput.write ('image.hv:size=%s\n' % (image.size))
        self.fpOutput.write ('image.hv:uri=%s\n' % (image.uri))
        self.fpOutput.write ('image.hv:version=%s\n' % (image.version))
        self.fpOutput.write ('image.sl:arch=%s\n' % (image.hypervisor))
        self.fpOutput.write ('image.sl:checksum:sha512=%s\n' % (image.sha512))
        self.fpOutput.write ('image.sl:comments=%s\n' % (image.comments))
        self.fpOutput.write ('image.sl:os=%s\n' % (image.os))
        self.fpOutput.write ('image.sl:osversion=%s\n' % (image.osversion))
        return True

    def display_subscription(self,subscription):    
        self.fpOutput.write ('subscription.dc:identifier=%s\n' % (subscription.identifier))
        self.fpOutput.write ('subscription.dc:description=%s\n' % (subscription.description))
        self.fpOutput.write ('subscription.sl:authorised=%s\n' % (subscription.authorised))
        self.fpOutput.write ('subscription.hv:uri=%s\n' % (subscription.uri))
        if subscription.updated:
            self.fpOutput.write ('subscription.dc:date:updated=%s\n' % (subscription.updated.strftime(time_format_definition)))
        else:
            self.fpOutput.write ('subscription.dc:date:updated=%s\n'% (False))
        return True
    def display_subscriptionInfo(self,imagedef,imagelist,image):
        #self.log.info(type(imagedef))
        #self.log.info(type(imagelist))
        #self.log.info(type(image))
        #self.log.info(dir(image))
        if image.expired == None:
            msg = "imagelist.expired=False\n"
            
        else:
            msg = "imagelist.expired=True\n"
        self.fpOutput.write (msg)
        self.fpOutput.write ('imagelist.dc:date:imported=%s\n' % (image.imported.strftime(time_format_definition)))
        self.fpOutput.write ('imagelist.dc:date:created=%s\n' % (image.created.strftime(time_format_definition)))
        self.fpOutput.write ('imagelist.dc:date:expires=%s\n' % (image.expires.strftime(time_format_definition)))
        #self.fpOutput.write ('imagedef.dc:identifier=%s\n' % (imagedef.identifier))
        #self.fpOutput.write ('imagedef.cache=%s\n' % (imagedef.cache))
        
        return True
    def display_endorser(self,endorser):
        self.fpOutput.write ("endorser.dc:identifier=%s\n" % (endorser.identifier))
        if len(endorser.princibles) == 0:
            self.log.warning("endorser '%s' has no princibles" % (selector_filter))
            return False
        for princible in endorser.princibles:
            self.fpOutput.write("endorser.hv:dn=%s\n" % (princible.hv_dn))
            self.fpOutput.write("endorser.hv:ca=%s\n" % (princible.hv_ca))
        for subauth in endorser.subscriptionauth:
            #self.fpOutput.write("subauth.authorised=%s\n" % (subauth.authorised))
            subscription_query = self.saSession.query(model.Subscription).\
                filter(model.Subscription.id == subauth.subscription)
            for subscription in subscription_query:
                self.display_subscription(subscription)    
class output_driver_lister_json(output_driver_lister):
    def list_vmcatcher_subscribe(self):
        output = []
        subauthq = self.saSession.query(model.Subscription).all()
        for item in subauthq:
            output.append({"identifier" : item.identifier,
                "authorised" : item.authorised,
                "uri" : item.uri})
        self.fpOutput.write (json.dumps(output,sort_keys=True, indent=4))
    def list_vmcatcher_image(self):
        imageDefs = self.saSession.query(model.ImageDefinition,model.Subscription).\
            filter(model.Subscription.id == model.ImageDefinition.subscription)
        output = []
        for q_result in imageDefs:
            imagedef = q_result[0]
            subscription = q_result[1]
            bimappedOutput = self.bitmap_vmcatcher_image(imagedef,subscription)
            output.append({ "image" : imagedef.identifier,
                "state" : bimappedOutput,
                "subscription" : subscription.identifier})
        self.fpOutput.write (json.dumps(output,sort_keys=True, indent=4))
    def list_vmcatcher_endorser_cred(self):
        output = []
        allendorsers = self.saSession.query(model.Endorser).all()
        for endorser in allendorsers:
            EndId = str(endorser.identifier)
            subauthq = self.saSession.query(model.Endorser,model.EndorserPrincible).\
                filter(model.Endorser.id==model.EndorserPrincible.endorser).\
                filter(model.Endorser.identifier==EndId)
            endorser_json = { "endorser" : endorser.identifier }
            endorser_cred = []
            for item in subauthq:
                endorser = item[0]
                princible = item[1]
                endorser_cred.append({ "subject" : princible.hv_dn,
                    "issuer" : princible.hv_ca})
            if len (endorser_cred) > 0:
                endorser_json["princibles"] = endorser_cred
            output.append(endorser_json)
        self.fpOutput.write (json.dumps(output,sort_keys=True, indent=4))
    def list_vmcatcher_endorser_link(self):
        output = []
        allLinks = self.saSession.query(model.Subscription,model.Endorser,model.SubscriptionAuth).\
            filter(model.Endorser.id==model.SubscriptionAuth.endorser).\
            filter(model.Subscription.id==model.SubscriptionAuth.subscription)
        for sub,endorser,aubauth in allLinks:
            output.append({ "endorser" : endorser.identifier,
                "subscription" : sub.identifier,
                "authorised" : aubauth.authorised
            })
        self.fpOutput.write(json.dumps(output,sort_keys=True, indent=4))
    def display_endorser(self,endorser):
        self.fpOutput.write ("endorser.dc:identifier=%s\n" % (endorser.identifier))
        if len(endorser.princibles) == 0:
            self.log.warning("endorser '%s' has no princibles" % (selector_filter))
            return False
        for princible in endorser.princibles:
            self.fpOutput.write("endorser.hv:dn=%s\n" % (princible.hv_dn))
            self.fpOutput.write("endorser.hv:ca=%s\n" % (princible.hv_ca))
        for subauth in endorser.subscriptionauth:
            #self.fpOutput.write("subauth.authorised=%s\n" % (subauth.authorised))
            subscription_query = self.saSession.query(model.Subscription).\
                filter(model.Subscription.id == subauth.subscription)
            for subscription in subscription_query:
                self.display_subscription(subscription)    
class output_driver_smime(output_driver_lister,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister.__init__(self)
        self.log = logging.getLogger("output_driver_smime")

    def display_imagelist(self,imagelist):
        self.fpOutput.write(imagelist.data)
        return True
    def display_imagelistImage(self,subscription,imagedef,imagelist,image):
        if not self.display_imagelist(imagelist):
            return False
        return True
    def display_subscriptionInfo(self,imagedef,imagelist,image):
        return self.display_imagelist(image)


class output_driver_message(output_driver_lister,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister.__init__(self)
        self.log = logging.getLogger("output_driver_message")
    def display_imagelist(self,imagelist):
        smimeProcessor =  smimeX509validation(self.x509anchor)
        try:
            smimeProcessor.Process(str(imagelist.data))
        except smimeX509ValidationError,E:
            self.log.error("Failed to validate text for '%s' produced error '%s'" % (imagelist,E))
            return False
        if not smimeProcessor.verified:
            self.log.error("Failed to validate text for '%s' produced error '%s'" % (subscriptionKey,E))
            return False
        self.fpOutput.write (smimeProcessor.InputDaraStringIO.getvalue())
        return True

    def display_imagelistImage(self,subscription,imagedef,imagelist,image):
        if not self.display_imagelist(imagelist):
            return False
        return True    
    
    def display_subscription(self,subscription):
        pass
    

    def display_imagelistImage(self,subscription,imagedef,imagelist,image):
        if not self.display_imagelist(imagelist):
            return False
        return True
    def display_subscriptionInfo(self,imagedef,imagelist,image):
        return self.display_imagelist(image)

class output_driver_json(output_driver_lister_json,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister_json.__init__(self)
        self.log = logging.getLogger("output_driver_lines")
        

class output_driver_lines(output_driver_lister,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister.__init__(self)
        self.log = logging.getLogger("output_driver_json")
