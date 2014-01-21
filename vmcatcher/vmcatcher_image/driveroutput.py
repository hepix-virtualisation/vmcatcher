import logging
from hepixvmitrust.vmitrustlib import time_format_definition as time_format_definition

from smimeX509validation import TrustStore, LoadDirChainOfTrust,smimeX509validation, smimeX509ValidationError

class output_driver_base:
    def __init__(self,file_pointer,session,anchor):
        self.session = session
        self.log = logging.getLogger("db_actions")
        self.file_pointer = file_pointer
        self.anchor = anchor
    def display_subscription_imagelist(self,subscription,imagelist):
        status = None

        self.display_subscription(subscription)
        if not self.display_imagelist(imagelist):
            return False
        return True
    def display_subscription(self,subscription):
        pass
    def display_imagelist(self,imagelist):
        return True
    def subscriptions_lister(self):
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
    def display_subscription(self,image):
        self.file_pointer.write ('image.dc:identifier=%s\n' % (image.identifier))
        self.file_pointer.write ('image.dc:description=%s\n' % (image.description))
        self.file_pointer.write ('image.hv:uri=%s\n' % (image.uri))
        return True
    def display_imagelist(self,imagelist):
        smimeProcessor =  smimeX509validation(self.anchor)
        try:
            smimeProcessor.Process(str(imagelist.data))
        except smimeX509ValidationError,E:
            self.log.error("Failed to validate text for '%s' produced error '%s'" % (imagelist,E))
            return False
        self.file_pointer.write (smimeProcessor.InputDaraStringIO.getvalue())
        return True
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

    def subscriptions_lister(self):
        subauthq = self.session.query(model.Subscription).all()
        for item in subauthq:
            self.file_pointer.write ("%s\t%s\t%s\n" % (item.uuid,item.authorised,item.url))
