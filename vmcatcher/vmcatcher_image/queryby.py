import vmcatcher.databaseDefinition as model
class queryby_base:
    """"Base class for querying subscriptions"""
    def __init__(self,session):
        self.session = session
    def subscription_by_id(self,private_id):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.id==private_id)
        return subscriptionlist
    def subscription_by_uri(self,url):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.url==url)
        return subscriptionlist
    def subscription_by_uuid(self,uuid):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.identifier==uuid)
        return subscriptionlist
    def imagelist_by_id(self,private_id):
        subscriptionlist = self.session.query(model.ImageListInstance).\
                filter(model.ImageListInstance.id==private_id)
        return subscriptionlist

        # Now the virtual class
    def subscription_get(self,by_id):
        return self.subscription_by_id(by_id)

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


class queryby_sha512(queryby_base):
    def imageDefinition_get(self,sha512):
        return self.imageDefinition_by_imageSha512(sha512)

class queryby_uuid(queryby_base):
    def imageDefinition_get(self,uuid):
        return self.imageDefinition_by_imageUuid(uuid)
