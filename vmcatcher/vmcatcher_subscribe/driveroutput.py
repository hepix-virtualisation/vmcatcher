import logging
import vmcatcher.databaseDefinition as model

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
 
