import logging
import vmcatcher.databaseDefinition as model
from smimeX509validation import TrustStore, LoadDirChainOfTrust,smimeX509validation, smimeX509ValidationError
from hepixvmitrust.vmitrustlib import time_format_definition as time_format_definition

class output_driver_base(object):
    def __init__(self,file_pointer,session,anchor):
        self.session = session
        self.log = logging.getLogger("db_actions")
        self.file_pointer = file_pointer
        self.anchor = anchor
    def display_subscription_imagelist(self,subscription,imagelist):
        status = None

        self.display_subscription(subscription)
        self.display_imagelist(imagelist)

        return True
    def display_subscription(self,subscription):
        pass
    def display_imagelist(self,imagelist):
        pass
    def subscriptions_lister(self):
        pass
    def display_image_def(self,subscription):
        pass


class output_driver_smime(output_driver_base):
    def display_subscription(self,subscription):
        pass
    def display_imagelist(self,imagelist):
        self.file_pointer.write (imagelist.data)
        return True
    def display_imagelistImage(self,imagedef,imagelist,image):
        if not self.display_imagelist(imagelist):
            return False
        return True


class output_driver_message(output_driver_base):
    def __init__(self,file_pointer,session,anchor):
        output_driver_base.__init__(self,file_pointer,session,anchor)
        self.log = logging.getLogger("output_driver_message")
    def display_subscription(self,subscription):
        pass
    def display_imagelist(self,imagelist):
        smimeProcessor =  smimeX509validation(self.anchor)
        try:
            smimeProcessor.Process(str(imagelist.data))
        except smimeX509ValidationError,E:
            self.log.error("Failed to validate text for '%s' produced error '%s'" % (imagelist,E))
            return False
        if not smimeProcessor.verified:
            self.log.error("Failed to validate text for '%s' produced error '%s'" % (subscriptionKey,E))
            return False
        self.file_pointer.write (smimeProcessor.InputDaraStringIO.getvalue())
        return True

    def display_imagelistImage(self,imagedef,imagelist,image):
        if not self.display_imagelist(imagelist):
            return False
        return True


class output_driver_lines(output_driver_base):
    def display_subscription(self,subscription):
        self.file_pointer.write ('subscription.dc:identifier=%s\n' % (subscription.identifier))
        self.file_pointer.write ('subscription.dc:description=%s\n' % (subscription.description))
        self.file_pointer.write ('subscription.sl:authorised=%s\n' % (subscription.authorised))
        self.file_pointer.write ('subscription.hv:uri=%s\n' % (subscription.uri))
        if subscription.updated:
            self.file_pointer.write ('subscription.dc:date:updated=%s\n' % (subscription.updated.strftime(time_format_definition)))
        else:
            self.file_pointer.write ('subscription.dc:date:updated=%s\n'% (False))
        return True

    def display_imagelist(self,imagelist):
        self.file_pointer.write ('imagelist.dc:date:imported=%s\n' % (imagelist.imported.strftime(time_format_definition)))
        self.file_pointer.write ('imagelist.dc:date:created=%s\n' % (imagelist.created.strftime(time_format_definition)))
        self.file_pointer.write ('imagelist.dc:date:expires=%s\n' % (imagelist.expires.strftime(time_format_definition)))
        if imagelist.expired == None:
            self.file_pointer.write ('imagelist.expired=0\n')
        else:
            self.file_pointer.write ('imagelist.expired=%s\n' % (imagelist.expired.strftime(time_format_definition)))
    def subscriptions_lister(self):
        subauthq = self.session.query(model.Subscription).all()
        for item in subauthq:
            self.file_pointer.write ("%s\t%s\t%s\n" % (item.identifier,item.authorised,item.uri))

    def display_image_def(self,imagedef):
        self.file_pointer.write ('subscription.image.dc:identifier=%s\n' % (imagedef.identifier))

    def endorser_lister(self,allendorsers):
        for endorser in allendorsers:
            EndId = str(endorser.identifier)
            subauthq = self.session.query(model.Endorser,model.EndorserPrincible).\
                filter(model.Endorser.id==model.EndorserPrincible.endorser).\
                filter(model.Endorser.identifier==EndId)
            for item in subauthq:
                endorser = item[0]
                princible = item[1]
                self.file_pointer.write ("'%s'\t'%s'\t'%s'\n" % (endorser.identifier,princible.hv_dn,princible.hv_ca))

    def links_lister(self,allLinks):
        for sub,endorser,aubauth in allLinks:
            self.file_pointer.write ("'%s'\t'%s'\t'%s'\n" % (endorser.identifier,sub.identifier,aubauth.authorised))

    def display_endorser(self,endorser):
        self.file_pointer.write ("endorser.dc:identifier=%s\n" % (endorser.identifier))
        princible_query = self.query.princible_by_endorserId(endorser.id)
        if princible_query.count() == 0:
            self.log.warning("endorser '%s' has no princibles" % (selector_filter))
            return False
        for princible in princible_query:
            self.file_pointer.write("endorser.hv:dn=%s\n" % (princible.hv_dn))
            self.file_pointer.write("endorser.hv:ca=%s\n" % (princible.hv_ca))
        subauth_query = self.query.subscriptionAuth_by_endorserId(endorser.id)
        for subauth in subauth_query:
            #self.file_pointer.write("subauth.authorised=%s\n" % (subauth.authorised))
            subscription_query = self.query.subscription_by_id(subauth.subscription)
            for subscription in subscription_query:
                self.display_subscription(subscription)


    def display_imagelistImage(self,imagedef,imagelist,image):
        self.file_pointer.write ('imagelist.dc:identifier=%s\n' % (imagedef.identifier))
        self.file_pointer.write ('imagelist.dc:date:imported=%s\n' % (imagelist.imported.strftime(time_format_definition)))
        self.file_pointer.write ('imagelist.dc:date:created=%s\n' % (imagelist.created.strftime(time_format_definition)))
        self.file_pointer.write ('imagelist.dc:date:expires=%s\n' % (imagelist.expires.strftime(time_format_definition)))
        self.file_pointer.write ('imagedef.dc:identifier=%s\n' % (imagedef.identifier))
        self.file_pointer.write ('imagedef.cache=%s\n' % (imagedef.cache))
        self.file_pointer.write ('image.dc:description=%s\n' % (image.description))
        self.file_pointer.write ('image.dc:title=%s\n' % (image.title))
        self.file_pointer.write ('image.hv:hypervisor=%s\n' % (image.hypervisor))
        self.file_pointer.write ('image.hv:size=%s\n' % (image.size))
        self.file_pointer.write ('image.hv:uri=%s\n' % (image.uri))
        self.file_pointer.write ('image.hv:version=%s\n' % (image.version))
        self.file_pointer.write ('image.sl:arch=%s\n' % (image.hypervisor))
        self.file_pointer.write ('image.sl:checksum:sha512=%s\n' % (image.sha512))
        self.file_pointer.write ('image.sl:comments=%s\n' % (image.comments))
        self.file_pointer.write ('image.sl:os=%s\n' % (image.os))
        self.file_pointer.write ('image.sl:osversion=%s\n' % (image.osversion))
        return True
