import vmcatcher.databaseDefinition as model

class queryby_base(object):
    """"Base class for querying subscriptions"""
    def __init__(self,session):
        self.session = session
    def subscription_by_id(self,private_id):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.id==private_id)
        return subscriptionlist
    def subscription_by_uri(self,uri):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.uri==uri)
        return subscriptionlist
    def subscription_by_uuid(self,uuid):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.identifier==uuid)
        return subscriptionlist
    def imagelistInstance_by_id(self,private_id):
        subscriptionlist = self.session.query(model.ImageListInstance).\
                filter(model.ImageListInstance.id==private_id)
        return subscriptionlist

        # Now the virtual class
    def subscription_get(self,by_id):
        return self.subscription_by_id(by_id)

    def endorser_all(self):
        return self.session.query(model.Endorser).all()
    def endorser_by_uuid(self,uuid):
        endorser_list = self.session.query(model.Endorser).\
                filter(model.Endorser.identifier==uuid)
        return endorser_list
    def princible_by_endorserId(self,identifier):
        princible_list = self.session.query(model.EndorserPrincible).\
                filter(model.EndorserPrincible.endorser == identifier)
        return princible_list
    def subscriptionAuth_by_endorserId(self,identifier):
        subauth_list = self.session.query(model.SubscriptionAuth).\
                filter(model.SubscriptionAuth.endorser == identifier)
        return subauth_list
    def links_all(self):
        return self.session.query(model.Subscription,model.Endorser,model.SubscriptionAuth).\
            filter(model.Endorser.id==model.SubscriptionAuth.endorser).\
            filter(model.Subscription.id==model.SubscriptionAuth.subscription)

    def imageDefinition_by_imageUuid(self,uuid):
        imagelistImage = self.session.query(model.ImageDefinition).\
                filter(model.ImageDefinition.identifier == uuid)


        return imagelistImage
    def imageDefinition_by_imageSha512(self,sha512):
        imagelistImage = self.session.query(model.ImageDefinition).\
                filter(model.ImageListInstance.id==model.ImageInstance.fkimagelistinstance).\
                filter(model.ImageInstance.sha512 == sha512).\
                filter(model.ImageInstance.fkIdentifier == model.ImageDefinition.id)
        return imagelistImage 
class queryby_uri(queryby_base):
    def subscription_get(self,url):
        return self.subscription_by_uri(url)

class queryby_uuid(queryby_base):
    def subscription_get(self,uuid):
        return self.subscription_by_uuid(uuid)


class queryby_sha512(queryby_base):
    def imageDefinition_get(self,sha512):
        return self.imageDefinition_by_imageSha512(sha512)

class queryby_uuid(queryby_base):
    def imageDefinition_get(self,uuid):
        return self.imageDefinition_by_imageUuid(uuid)
