from smimeX509validation import TrustStore, LoadDirChainOfTrust,smimeX509validation, smimeX509ValidationError
from hepixvmitrust.vmitrustlib import time_format_definition as time_format_definition

import logging
import vmcatcher.databaseDefinition as model
import json

class output_driver_base(object):
    def __init__(self):
        self.log = logging.getLogger("output_driver_base")
    def __init__(self):
        self.fpOutput = None
        self.saSession = None
        self.x509anchor = None
    
    def info(self, *args, **kwargs):
        self.log.debug("info")
        outut = {}
        argSubscription = kwargs.get('Subscription', None)
        if argSubscription != None:
            outut["Subscription"] =  self.info_Subscription(argSubscription)
        
        argImageListInstance = kwargs.get('ImageListInstance', None)
        if argImageListInstance != None:
            outut["ImageListInstance"] =  self.info_ImageListInstance(argImageListInstance)
        
        argImageInstance = kwargs.get('ImageInstance', None)
        if argImageInstance != None:
            outut["ImageInstance"] =  self.info_ImageInstance(argImageInstance)
        
        argImageDefinition = kwargs.get('ImageDefinition', None)
        if argImageDefinition != None:
            outut["ImageDefinition"] =  self.info_ImageDefinition(argImageDefinition)
        
        self.fpOutput.write(json.dumps(outut,sort_keys=True, indent=4))
        #print dir(imagelistInstance)
        #display_subscription
    
    def query_imagedef_Identifier(self,imagelistIdentifier):
        self.log.debug("query_imagedef_Identifier")
        imageDefs = self.saSession.query(model.ImageDefinition,model.Subscription).\
            filter(model.Subscription.id == model.ImageDefinition.subscription).\
            filter(model.ImageDefinition.identifier==imagelistIdentifier)
        return imageDefs
    
    def bitmap_vmcatcher_image(self,imagedef,subscription):
        self.log.debug("bitmap_vmcatcher_image")
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
    def __init__(self):
        output_driver_base.__init__(self)
        self.log = logging.getLogger("output_driver_lister")
    def list_vmcatcher_subscribe(self):
        subauthq = self.saSession.query(model.Subscription).all()
        for item in subauthq:
            self.fpOutput.write ("%s\t%s\t%s\n" % (item.identifier,item.authorised,item.uri))
    
    def info(self, *args, **kwargs):
        self.log.debug("info")
        argSubscription = kwargs.get('Subscription', None)
        if argSubscription != None:
            self.info_Subscription(argSubscription)
        
        argImageListInstance = kwargs.get('ImageListInstance', None)
        if argImageListInstance != None:
            self.info_ImageListInstance(argImageListInstance)
        
        argImageInstance = kwargs.get('ImageInstance', None)
        if argImageInstance != None:
            self.info_ImageInstance(argImageInstance)
        
        argImageDefinition = kwargs.get('ImageDefinition', None)
        if argImageDefinition != None:
            self.info_ImageDefinition(argImageDefinition)
        
    def list_vmcatcher_image(self):
        self.log.debug("list_vmcatcher_image")
        imageDefs = self.saSession.query(model.ImageDefinition,model.Subscription).\
            filter(model.Subscription.id == model.ImageDefinition.subscription)
        for q_result in imageDefs:
            imagedef = q_result[0]
            subscription = q_result[1]
            bimappedOutput = self.bitmap_vmcatcher_image(imagedef,subscription)
            self.fpOutput.write("%s\t%s\t%s\n" % (imagedef.identifier,bimappedOutput,subscription.identifier))
    def list_vmcatcher_endorser_cred(self):
        self.log.debug("list_vmcatcher_endorser_cred")
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
        self.log.debug("list_vmcatcher_endorser_link")
        allLinks = self.saSession.query(model.Subscription,model.Endorser,model.SubscriptionAuth).\
            filter(model.Endorser.id==model.SubscriptionAuth.endorser).\
            filter(model.Subscription.id==model.SubscriptionAuth.subscription)
        for sub,endorser,aubauth in allLinks:
            self.fpOutput.write ("'%s'\t'%s'\t'%s'\n" % (endorser.identifier,sub.identifier,aubauth.authorised))
    def display_imagelistImage(self,subscription,imagedef,imagelist,image):
        self.log.debug("display_imagelistImage")
        self.info(ImageInstance=image,Subscription=subscription,ImageListInstance=imagelist,ImageDefinition=imagedef)
        
        
        return True

    def display_subscription(self,subscription):   
        return self.info_Subscription(subscription)

    def display_subscriptionInfo(self,imagedef,imagelist,image):
        self.log.debug("display_subscriptionInfo")
        self.info(ImageDefinition=image)
        return True    

    def display_endorser(self,endorser):
        self.log.debug("display_endorser")
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

    def info_ImageListInstance(self,argImageListInstance):
        self.log.debug("info_ImageListInstance")
        expired = False
        if argImageListInstance.expired == None:
            msg = "imagelist.expired=False\n"
            expired = True
        else:
            msg = "imagelist.expired=True\n"
        if not expired:
            self.fpOutput.write ('imagelist.vmcatcher.dc:date:expired=%s\n' % (argImageListInstance.expired.strftime(time_format_definition)))
        self.fpOutput.write (msg)
        self.fpOutput.write ('imagelist.dc:date:imported=%s\n' % (argImageListInstance.imported.strftime(time_format_definition)))
        self.fpOutput.write ('imagelist.dc:date:created=%s\n' % (argImageListInstance.created.strftime(time_format_definition)))
        self.fpOutput.write ('imagelist.dc:date:expires=%s\n' % (argImageListInstance.expires.strftime(time_format_definition)))
        return True
    def info_Subscription(self,subscription):
        self.log.debug("info_Subscription")
        # imagelist.dc:identifier for backwards compatability for 0.2.X versions
        self.fpOutput.write ('imagelist.dc:identifier=%s\n' % (subscription.identifier))
        self.fpOutput.write ('subscription.dc:identifier=%s\n' % (subscription.identifier))
        self.fpOutput.write ('subscription.dc:description=%s\n' % (subscription.description))
        self.fpOutput.write ('subscription.sl:authorised=%s\n' % (subscription.authorised))
        self.fpOutput.write ('subscription.hv:uri=%s\n' % (subscription.uri))
        if subscription.updated:
            self.fpOutput.write ('subscription.dc:date:updated=%s\n' % (subscription.updated.strftime(time_format_definition)))
        else:
            self.fpOutput.write ('subscription.dc:date:updated=%s\n'% (False))
        return True
    def info_ImageInstance(self,imageInstance):
        self.fpOutput.write ('image.dc:description=%s\n' % (imageInstance.description))
        self.fpOutput.write ('image.dc:title=%s\n' % (imageInstance.title))
        self.fpOutput.write ('image.hv:hypervisor=%s\n' % (imageInstance.hypervisor))
        self.fpOutput.write ('image.hv:size=%s\n' % (imageInstance.size))
        self.fpOutput.write ('image.hv:uri=%s\n' % (imageInstance.uri))
        self.fpOutput.write ('image.hv:version=%s\n' % (imageInstance.version))
        self.fpOutput.write ('image.sl:arch=%s\n' % (imageInstance.hypervisor))
        self.fpOutput.write ('image.sl:checksum:sha512=%s\n' % (imageInstance.sha512))
        self.fpOutput.write ('image.sl:comments=%s\n' % (imageInstance.comments))
        self.fpOutput.write ('image.sl:os=%s\n' % (imageInstance.os))
        self.fpOutput.write ('image.sl:osversion=%s\n' % (imageInstance.osversion))
    def info_ImageDefinition(self,imageDef):
        self.fpOutput.write ('imagedef.dc:identifier=%s\n' % (imageDef.identifier))
        self.fpOutput.write ('imagedef.cache=%s\n' % (imageDef.cache))
class output_driver_lister_json(output_driver_lister):
    def __init__(self):
        output_driver_lister.__init__(self)
        self.log = logging.getLogger("output_driver_lister_json")
    def info(self, *args, **kwargs):
        self.log.debug("info")
        outut = {}
        argSubscription = kwargs.get('Subscription', None)
        if argSubscription != None:
            outut["Subscription"] =  self.info_Subscription(argSubscription)
        
        argImageListInstance = kwargs.get('ImageListInstance', None)
        if argImageListInstance != None:
            outut["ImageListInstance"] =  self.info_ImageListInstance(argImageListInstance)
        
        argImageInstance = kwargs.get('ImageInstance', None)
        if argImageInstance != None:
            outut["ImageInstance"] =  self.info_ImageInstance(argImageInstance)
        argImageDefinition = kwargs.get('ImageDefinition', None)
        if argImageDefinition != None:
            outut["ImageDefinition"] =  self.info_ImageDefinition(argImageDefinition)
        self.fpOutput.write(json.dumps(outut,sort_keys=True, indent=4))    
    def list_vmcatcher_subscribe(self):
        self.log.debug("list_vmcatcher_subscribe")
        output = []
        subauthq = self.saSession.query(model.Subscription).all()
        for item in subauthq:
            output.append({"identifier" : item.identifier,
                "authorised" : item.authorised,
                "uri" : item.uri})
        self.fpOutput.write (json.dumps(output,sort_keys=True, indent=4))
    def list_vmcatcher_image(self):
        self.log.debug("list_vmcatcher_image")
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
        self.log.debug("list_vmcatcher_endorser_cred")
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
        self.log.debug("list_vmcatcher_endorser_link")
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
        self.log.debug("display_endorser")
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
    def display_subscription(self,subscription):
        self.log.debug("display_subscription")
        output = {}
        output["identifier"] = subscription.identifier
        output["description"] = subscription.description
        output["authorised"] = subscription.authorised
        output["uri"] = subscription.uri
        if subscription.updated:
            output["updated"] = subscription.updated.strftime(time_format_definition)
        
        self.fpOutput.write (json.dumps(output,sort_keys=True, indent=4))
        return True
    
    def display_subscriptionInfo(self,imagedef,imagelist,image):
        self.log.debug("display_subscriptionInfo")
        #self.log.info(type(imagedef))
        #self.log.info(type(imagelist))
        #self.log.info(type(image))
        #self.log.info(dir(image))
        output = {}
        if image.expired == None:
            output["active"] =  True
            
            
        else:
            output["active"] =  False
        output["imported"] = image.imported.strftime(time_format_definition)
        output["created"] = image.created.strftime(time_format_definition)
        output["expires"] = image.expires.strftime(time_format_definition)
        
        #self.fpOutput.write ('imagedef.dc:identifier=%s\n' % (imagedef.identifier))
        #self.fpOutput.write ('imagedef.cache=%s\n' % (imagedef.cache))
        
        return True        
    def info_Subscription(self,subscription):
        upddated = False
        if subscription.updated:
            upddated = subscription.updated.strftime(time_format_definition)
            
        output = {"identifier" : subscription.identifier, 
            "description" : subscription.description,
            "authorised" : subscription.authorised,
            "uri" : subscription.uri,
            "updated" : upddated}
        return output    
    def info_ImageListInstance(self,argImageListInstance):
        #self.fpOutput.write ('imagelist.dc:date:imported=%s\n' % (argImageListInstance.imported.strftime(time_format_definition)))
        #self.fpOutput.write ('imagelist.dc:date:created=%s\n' % (argImageListInstance.created.strftime(time_format_definition)))
        #self.fpOutput.write ('imagelist.dc:date:expires=%s\n' % (argImageListInstance.expires.strftime(time_format_definition)))
        output = {"imported" : argImageListInstance.imported.strftime(time_format_definition),
            "created" : argImageListInstance.created.strftime(time_format_definition),
            "expires": argImageListInstance.expires.strftime(time_format_definition)}
        return output
    def info_Subscription(self,subscription):
        upddated = False
        if subscription.updated:
            upddated = subscription.updated.strftime(time_format_definition)
            
        output = {"identifier" : subscription.identifier, 
            "description" : subscription.description,
            "authorised" : subscription.authorised,
            "uri" : subscription.uri,
            "updated" : upddated}
        return output    
    def info_ImageInstance(self,imageInstance):
        output = {"description" : imageInstance.description,
                    "title" : imageInstance.title,
                    "hypervisor" : imageInstance.hypervisor,
                    "size" :imageInstance.size,
                    "uri" : imageInstance.uri,
                    "version" : imageInstance.version,
                    "arch" : imageInstance.hypervisor,
                    "sha512" : imageInstance.sha512,
                    "comments" : imageInstance.comments,
                    "sl:os" : imageInstance.os,
                    "sl:osversion" : imageInstance.osversion}
        return output
    def info_ImageDefinition(self,imageDef):
        output = { "identifier" : imageDef.identifier,
                "cache" : imageDef.cache}
        return output


class output_driver_display_message(output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        self.log = logging.getLogger("output_driver_display_message")
    
    def display_subscription(self,subscription):   
        subauthq = self.saSession.query(model.ImageListInstance).\
                filter(model.Subscription.id == subscription.id).\
                filter(model.ImageInstance.fkIdentifier == model.ImageDefinition.id).\
                filter(model.ImageInstance.fkimagelistinstance == model.ImageListInstance.id).\
                filter(model.Subscription.imagelist_latest == model.ImageListInstance.id)
        sub = subauthq.first()         
        return self.display_imagelist(sub)

class output_driver_display_metadata(output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        self.log = logging.getLogger("output_driver_display_metadata")

    def display_subscription(self,subscription):
        query_imagelistInstance = self.saSession.query(model.ImageListInstance).\
            filter(model.ImageListInstance.id==subscription.imagelist_latest)
        for imagelistInstance in query_imagelistInstance:
            #self._outputter.display_subscriptionInfo(firstSubscription,item,imagelistInstance)
            self.info(Subscription=subscription,ImageListInstance=imagelistInstance)

class output_driver_smime(output_driver_display_message,output_driver_lister,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister.__init__(self)
        output_driver_display_message.__init__(self)
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
    def info(self, *args, **kwargs):
        self.log.debug("info")
        outut = {}
        argSubscription = kwargs.get('Subscription', None)
        if argSubscription != None:
            pass
        argImageListInstance = kwargs.get('ImageListInstance', None)
        if argImageListInstance != None:
            pass
        argImageInstance = kwargs.get('ImageInstance', None)
        if argImageInstance != None:
            pass
        argImageDefinition = kwargs.get('ImageDefinition', None)
        if  argImageDefinition != None:
            pass
        
        
        
        if argImageInstance != None:
            self.display_imagelist(argImageInstance)

class output_driver_message(output_driver_display_message,output_driver_lister,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister.__init__(self)
        output_driver_display_message.__init__(self)
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
    def display_subscriptionInfo(self,imagedef,imagelist,image):
        return self.display_imagelist(image)

class output_driver_json(output_driver_display_metadata, output_driver_lister_json,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister_json.__init__(self)
        output_driver_display_metadata.__init__(self)
        self.log = logging.getLogger("output_driver_json")
    def display_subscription(self,subscription):
        query_imagelistInstance = self.saSession.query(model.ImageListInstance).\
            filter(model.ImageListInstance.id==subscription.imagelist_latest)
        for imagelistInstance in query_imagelistInstance:
            #self._outputter.display_subscriptionInfo(firstSubscription,item,imagelistInstance)
            self.info(Subscription=subscription,ImageListInstance=imagelistInstance)

class output_driver_lines(output_driver_display_metadata, output_driver_lister,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister.__init__(self)
        output_driver_display_metadata.__init__(self)
        self.log = logging.getLogger("output_driver_lines")
    def display_subscription(self,subscription):
        query_imagelistInstance = self.saSession.query(model.ImageListInstance).\
            filter(model.ImageListInstance.id==subscription.imagelist_latest)
        for imagelistInstance in query_imagelistInstance:
            #self._outputter.display_subscriptionInfo(firstSubscription,item,imagelistInstance)
            self.info(Subscription=subscription,ImageListInstance=imagelistInstance)
