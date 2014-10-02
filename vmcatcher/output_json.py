import logging
import json
from hepixvmitrust.vmitrustlib import time_format_definition as time_format_definition
from vmcatcher.outputbase import output_driver_lister
from vmcatcher.outputbase import output_driver_display_metadata
from vmcatcher.outputbase import output_driver_base
from vmcatcher.outputbase import trustAnchorMap

import vmcatcher.databaseDefinition as model

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


        argSubscriptionAuth = kwargs.get('SubscriptionAuth', None)
        if argSubscriptionAuth != None:
            outut["SubscriptionAuth"] =  self.info_SubscriptionAuth(argSubscriptionAuth)

        argEndorser = kwargs.get('Endorser', None)
        if argEndorser != None:
            outut["Endorser"] =  self.info_Endorser(argEndorser)
        argEndorserPrincible = kwargs.get('EndorserPrincible', None)
        if argEndorserPrincible != None:
            outut["EndorserPrincible"] =  self.info_EndorserPrincible(argEndorserPrincible)

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
        if len(endorser.princibles) == 0:
            self.log.warning("endorser '%s' has no princibles" % (selector_filter))
            return False
        output = {'Princables' : [] , 'Subscription' : []}

        for princible in endorser.princibles:
            tmp = { "hv:dn" : princible.hv_dn,
                'hv:ca' : princible.hv_ca
            }
            output['Princables'].append(tmp)


        for subauth in endorser.subscriptionauth:
            #self.fpOutput.write("subauth.authorised=%s\n" % (subauth.authorised))
            subscription_query = self.saSession.query(model.Subscription).\
                filter(model.Subscription.id == subauth.subscription)
            for subscription in subscription_query:
                tmp = self.info_Subscription(subscription)
                output['Subscription'].append(tmp)
        self.fpOutput.write(json.dumps(output,sort_keys=True, indent=4))
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


    def info_Subscription(self,subscription):
        upddated = False
        if subscription.updated:
            upddated = subscription.updated.strftime(time_format_definition)

        output = {"identifier" : subscription.identifier,
            "description" : subscription.description,
            "authorised" : subscription.authorised,
            "uri" : subscription.uri,
            "updated" : upddated}
        if (subscription.userName != None):
            if len(subscription.userName) > 0:
                output["uri.username"] = subscription.userName
        if (subscription.password != None):
            if len(subscription.password) > 0:
                output["uri.password"] = subscription.password
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
            "updated" : upddated,
            "uri.trustAnchor" : trustAnchorMap[subscription.trustAnchor]}
        if (subscription.userName != None):
            if len(subscription.userName) > 0:
                output["uri.username"] = subscription.userName
        if (subscription.password != None):
            if len(subscription.password) > 0:
                output["uri.password"] = subscription.password
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

    def info_SubscriptionAuth(self,SubscriptionAuth):
        return {}
    def info_Endorser(self,Endorser):
        output = {"identifier" : Endorser.identifier
        }
        return output
    def info_EndorserPrincible(self,EndorserPrincible):
        output = {"subject" :EndorserPrincible.hv_dn,
            "issuer" : EndorserPrincible.hv_ca
        }
        return output




class output_driver_json(output_driver_display_metadata, output_driver_lister_json,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister_json.__init__(self)
        output_driver_display_metadata.__init__(self)
        self.log = logging.getLogger("output_driver_json")
